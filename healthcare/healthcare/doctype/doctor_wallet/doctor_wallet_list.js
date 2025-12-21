// Copyright (c) 2025, Healthcare and contributors
// For license information, please see license.txt

frappe.listview_settings['Doctor Wallet'] = {
	add_fields: ["status", "doctor", "commission_amount"],
	get_indicator: function(doc) {
		if (doc.status === "Paid") {
			return [__("Paid"), "green", "status,=,Paid"];
		} else if (doc.status === "Unpaid") {
			return [__("Unpaid"), "orange", "status,=,Unpaid"];
		}
	},
	onload: function(listview) {
		// Add custom button for bulk payment
		if (frappe.user.has_role("Healthcare Administrator")) {
			listview.page.add_menu_item(__("Pay Selected Doctors"), function() {
				let selected = listview.get_checked_items();
				if (selected.length === 0) {
					frappe.msgprint(__("Please select at least one record"));
					return;
				}
				// Filter only unpaid entries
				selected = selected.filter(d => d.status === "Unpaid");
				if (selected.length === 0) {
					frappe.msgprint(__("Please select unpaid entries"));
					return;
				}
				// Group by doctor
				let doctor_groups = {};
				selected.forEach(doc => {
					if (!doctor_groups[doc.doctor]) {
						doctor_groups[doc.doctor] = [];
					}
					doctor_groups[doc.doctor].push(doc.name);
				});
				
				// Create payment entry for first doctor (one at a time)
				// For multiple doctors, user needs to select entries for one doctor at a time
				let doctors = Object.keys(doctor_groups);
				if (doctors.length > 1) {
					frappe.msgprint(__("Please select entries for one doctor at a time. Multiple doctors will be handled separately."));
					return;
				}
				
				// Open payment dialog
				frappe.call({
					method: "healthcare.healthcare.doctype.doctor_wallet.doctor_wallet.create_payment_entry",
					args: {
						wallet_entries: {
							doctor: doctors[0],
							entries: doctor_groups[doctors[0]]
						}
					},
					callback: function(r) {
						if (r.message) {
							frappe.set_route("Form", "Payment Entry", r.message);
							listview.refresh();
						}
					}
				});
			});

			// Add bulk mark as paid with filters
			listview.page.add_menu_item(__("Bulk Mark as Paid"), function() {
				let dialog = new frappe.ui.Dialog({
					title: __("Bulk Mark as Paid"),
					fields: [
						{
							fieldtype: "Link",
							fieldname: "doctor",
							options: "Healthcare Practitioner",
							label: __("Doctor"),
							get_query: function() {
								return {
									filters: {
										"is_active": 1
									}
								};
							}
						},
						{
							fieldtype: "Link",
							fieldname: "company",
							options: "Company",
							label: __("Company")
						},
						{
							fieldtype: "Select",
							fieldname: "service_type",
							label: __("Service Type"),
							options: "\nPatient Encounter\nLab Test\nClinical Procedure\nTherapy Session\nSales Invoice\nService Request\nPatient Appointment\nOther"
						},
						{
							fieldtype: "Section Break",
							label: __("Date Range")
						},
						{
							fieldtype: "Date",
							fieldname: "date_from",
							label: __("From Date")
						},
						{
							fieldtype: "Date",
							fieldname: "date_to",
							label: __("To Date"),
							default: frappe.datetime.get_today()
						},
						{
							fieldtype: "Section Break",
							label: __("Payment Entry (Optional)")
						},
						{
							fieldtype: "Link",
							fieldname: "payment_entry",
							options: "Payment Entry",
							label: __("Link Payment Entry")
						}
					],
					primary_action_label: __("Mark as Paid"),
					primary_action: function(values) {
						// Validate at least one filter is provided
						if (!values.doctor && !values.company && !values.service_type && !values.date_from && !values.date_to) {
							frappe.msgprint(__("Please provide at least one filter"));
							return;
						}

						// Show confirmation
						frappe.confirm(
							__("This will mark all unpaid entries matching the filters as paid. Continue?"),
							function() {
								// Yes
								dialog.hide();
								frappe.call({
									method: "healthcare.healthcare.doctype.doctor_wallet.doctor_wallet.bulk_mark_as_paid",
									args: {
										filters: {
											doctor: values.doctor || null,
											company: values.company || null,
											service_type: values.service_type || null,
											date_from: values.date_from || null,
											date_to: values.date_to || null
										},
										payment_entry: values.payment_entry || null
									},
									freeze: true,
									freeze_message: __("Updating wallet entries..."),
									callback: function(r) {
										if (r.message && r.message.count > 0) {
											listview.refresh();
										}
									}
								});
							},
							function() {
								// No - do nothing
							}
						);
					}
				});
				dialog.show();
			});
		}
	}
};

