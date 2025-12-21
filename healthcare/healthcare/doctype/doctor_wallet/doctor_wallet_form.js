// Copyright (c) 2025, Healthcare and contributors
// For license information, please see license.txt

frappe.ui.form.on('Doctor Wallet', {
	refresh: function(frm) {
		// Add Pay Doctor button for unpaid entries
		if (frm.doc.status === "Unpaid" && frappe.user.has_role("Healthcare Administrator")) {
			frm.add_custom_button(__('Pay Doctor'), function() {
				frappe.call({
					method: "healthcare.healthcare.doctype.doctor_wallet.doctor_wallet.create_payment_entry",
					args: {
						wallet_entries: [{
							doctor: frm.doc.doctor,
							entries: [frm.doc.name]
						}]
					},
					callback: function(r) {
						if (r.message) {
							frappe.set_route("Form", "Payment Entry", r.message);
						}
					}
				});
			}, __('Actions'));
		}

		// Add link to payment entry if exists
		if (frm.doc.payment_entry) {
			frm.add_custom_button(__('View Payment Entry'), function() {
				frappe.set_route("Form", "Payment Entry", frm.doc.payment_entry);
			}, __('View'));
		}
	},
	service_amount: function(frm) {
		if (frm.doc.service_amount && frm.doc.commission_percentage) {
			frm.set_value('commission_amount', 
				flt(frm.doc.service_amount) * flt(frm.doc.commission_percentage) / 100
			);
		}
	},
	commission_percentage: function(frm) {
		if (frm.doc.service_amount && frm.doc.commission_percentage) {
			frm.set_value('commission_amount', 
				flt(frm.doc.service_amount) * flt(frm.doc.commission_percentage) / 100
			);
		}
	},
	service_type: function(frm) {
		// Clear service_reference when service_type changes
		if (frm.doc.service_type) {
			frm.set_value('service_reference', '');
		}
	},
	service_reference: function(frm) {
		// Auto-sync patient and related details when service_reference is set
		if (frm.doc.service_type && frm.doc.service_reference) {
			// Fetch details from server and populate fields immediately
			frappe.call({
				method: 'healthcare.healthcare.doctype.doctor_wallet.doctor_wallet.get_service_details',
				args: {
					service_type: frm.doc.service_type,
					service_reference: frm.doc.service_reference
				},
				freeze: true,
				callback: function(r) {
					if (r.message && !r.exc) {
						let data = r.message;
						// Always update these fields if available
						if (data.patient) {
							frm.set_value('patient', data.patient);
						}
						if (data.patient_name) {
							frm.set_value('patient_name', data.patient_name);
						}
						if (data.doctor) {
							frm.set_value('doctor', data.doctor);
						}
						if (data.encounter) {
							frm.set_value('encounter', data.encounter);
						}
						if (data.appointment) {
							frm.set_value('appointment', data.appointment);
						}
						// Only set if not already set
						if (data.company && !frm.doc.company) {
							frm.set_value('company', data.company);
						}
						if (data.date && !frm.doc.date) {
							frm.set_value('date', data.date);
						}
						// Always update service_amount if available (it's the most important field)
						if (data.service_amount) {
							frm.set_value('service_amount', data.service_amount);
						}
						// Refresh fields to show updated values
						frm.refresh_fields();
					} else if (r.exc) {
						frappe.show_alert({
							message: __('Error fetching service details: {0}', [r.exc]),
							indicator: 'red'
						}, 5);
					}
				}
			});
		}
	}
});


