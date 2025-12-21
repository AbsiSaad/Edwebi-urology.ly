// Copyright (c) 2025, Edwebi Urology and contributors
// For license information, please see license.txt

frappe.ui.form.on('Medical Report', {
	refresh: function(frm) {
		// Add button to print based on report type
		if (!frm.is_new() && frm.doc.status === 'Approved') {
			if (frm.doc.report_requested_for) {
				let print_format = 'Medical Report General';
				
				if (frm.doc.report_requested_for.includes('Sick Leave') || frm.doc.report_requested_for.includes('إجازة')) {
					print_format = 'Medical Report Sick Leave';
				} else if (frm.doc.report_requested_for.includes('Insurance') || frm.doc.report_requested_for.includes('تأمين')) {
					print_format = 'Medical Report Insurance';
				}
				
				frm.add_custom_button(__('Print Report'), function() {
					frappe.print.print_format = print_format;
					frappe.print.print(frm.doctype, frm.doc.name);
				}, __('Print'));
			}
		}
		
		// Add workflow action buttons
		if (frm.doc.workflow_state === 'Draft') {
			frm.add_custom_button(__('Request Approval'), function() {
				frm.call('request_approval').then(() => {
					frm.reload_doc();
				});
			}, __('Actions'));
		}
		
		if (frm.doc.workflow_state === 'Waiting for Doctor Approval') {
			if (frappe.user.has_role('Physician')) {
				frm.add_custom_button(__('Approve'), function() {
					frm.call('approve_report').then(() => {
						frm.reload_doc();
					});
				}, __('Actions'));
				
				frm.add_custom_button(__('Reject'), function() {
					frm.call('reject_report').then(() => {
						frm.reload_doc();
					});
				}, __('Actions'));
			}
		}
	},
	
	patient: function(frm) {
		if (frm.doc.patient) {
			frm.set_patient_details();
		}
	},
	
	visit_encounter: function(frm) {
		if (frm.doc.visit_encounter) {
			// Update all patient and doctor details from encounter
			frm.call('update_from_encounter').then((r) => {
				if (r.message) {
					// Update form fields with values from encounter
					if (r.message.patient) frm.set_value('patient', r.message.patient);
					if (r.message.patient_name) frm.set_value('patient_name', r.message.patient_name);
					if (r.message.gender) frm.set_value('gender', r.message.gender);
					if (r.message.age) frm.set_value('age', r.message.age);
					if (r.message.file_number) frm.set_value('file_number', r.message.file_number);
					if (r.message.doctor) frm.set_value('doctor', r.message.doctor);
					if (r.message.doctor_name) frm.set_value('doctor_name', r.message.doctor_name);
					if (r.message.report_date) frm.set_value('report_date', r.message.report_date);
				}
			});
		}
	},
	
	doctor: function(frm) {
		if (frm.doc.doctor) {
			frm.set_doctor_details();
		}
	},
	
	sick_leave_from: function(frm) {
		if (frm.doc.sick_leave_from && frm.doc.sick_leave_to) {
			frm.calculate_duration();
		}
	},
	
	sick_leave_to: function(frm) {
		if (frm.doc.sick_leave_from && frm.doc.sick_leave_to) {
			frm.calculate_duration();
		}
	}
});


