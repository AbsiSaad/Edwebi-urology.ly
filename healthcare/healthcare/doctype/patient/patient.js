// Copyright (c) 2016, ESS LLP and contributors
// For license information, please see license.txt
{% include 'healthcare/regional/india/abdm/js/patient.js' %}

frappe.ui.form.on('Patient', {
	refresh: function (frm) {
		frm.set_query('patient', 'patient_relation', function () {
			return {
				filters: [
					['Patient', 'name', '!=', frm.doc.name]
				]
			};
		});
		frm.set_query('customer_group', {'is_group': 0});
		frm.set_query('default_price_list', { 'selling': 1});

		if (frappe.defaults.get_default('patient_name_by') != 'Naming Series') {
			frm.toggle_display('naming_series', false);
		} else {
			erpnext.toggle_naming_series();
		}

		if (frappe.defaults.get_default('collect_registration_fee') && frm.doc.status == 'Disabled') {
			frm.add_custom_button(__('Invoice Patient Registration'), function () {
				invoice_registration(frm);
			});
		}

		if (frm.doc.patient_name && frappe.user.has_role('Physician')) {
			frm.add_custom_button(__('Patient Progress'), function() {
				frappe.route_options = {'patient': frm.doc.name};
				frappe.set_route('patient-progress');
			}, __('View'));

			frm.add_custom_button(__('Patient History'), function() {
				frappe.route_options = {'patient': frm.doc.name};
				frappe.set_route('patient_history');
			}, __('View'));
		}

		frappe.dynamic_link = {doc: frm.doc, fieldname: 'name', doctype: 'Patient'};
		frm.toggle_display(['address_html', 'contact_html'], !frm.is_new());

		if (!frm.is_new()) {
			if ((frappe.user.has_role('Nursing User') || frappe.user.has_role('Physician'))) {
				frm.add_custom_button(__('Medical Record'), function () {
					create_medical_record(frm);
				}, __('Create'));
				frm.toggle_enable(['customer'], 0);
			}
			
			// Add Medical Report button
			if (frappe.user.has_role('Healthcare Administrator') || frappe.user.has_role('Physician')) {
				frm.add_custom_button(__('Medical Report'), function () {
					create_medical_report(frm);
				}, __('Create'));
			}
			
			frappe.contacts.render_address_and_contact(frm);
			erpnext.utils.set_party_dashboard_indicators(frm);
		} else {
			frappe.contacts.clear_address_and_contact(frm);
		}
	},

	onload: function (frm) {
		if (frm.doc.dob) {
			$(frm.fields_dict['age_html'].wrapper).html(`${__('AGE')} : ${get_age(frm.doc.dob)}`);
		} else {
			$(frm.fields_dict['age_html'].wrapper).html('');
		}
	},

	create_appointment_btn: function(frm) {
		if (frm.is_new()) {
			frappe.msgprint(__('Please save the patient before creating an appointment.'));
			return;
		}
		open_appointment_dialog(frm);
	}
});

frappe.ui.form.on('Patient', 'dob', function(frm) {
	if (frm.doc.dob) {
		let today = new Date();
		let birthDate = new Date(frm.doc.dob);
		if (today < birthDate) {
			frappe.msgprint(__('Please select a valid Date'));
			frappe.model.set_value(frm.doctype,frm.docname, 'dob', '');
		} else {
			let age_str = get_age(frm.doc.dob);
			$(frm.fields_dict['age_html'].wrapper).html(`${__('AGE')} : ${age_str}`);
		}
	} else {
		$(frm.fields_dict['age_html'].wrapper).html('');
	}
});

frappe.ui.form.on('Patient Relation', {
	patient_relation_add: function(frm){
		frm.fields_dict['patient_relation'].grid.get_field('patient').get_query = function(doc){
			let patient_list = [];
			if(!doc.__islocal) patient_list.push(doc.name);
			$.each(doc.patient_relation, function(idx, val){
				if (val.patient) patient_list.push(val.patient);
			});
			return { filters: [['Patient', 'name', 'not in', patient_list]] };
		};
	}
});

let create_medical_record = function (frm) {
	frappe.route_options = {
		'patient': frm.doc.name,
		'status': 'Open',
		'reference_doctype': 'Patient Medical Record',
		'reference_owner': frm.doc.owner
	};
	frappe.new_doc('Patient Medical Record');
};

let create_medical_report = function (frm) {
	frappe.call({
		method: 'healthcare.healthcare.healthcare.doctype.medical_report.medical_report.create_medical_report_from_patient',
		args: {
			patient_name: frm.doc.name
		},
		callback: function(r) {
			if (!r.exc && r.message) {
				frappe.set_route('Form', 'Medical Report', r.message.name);
			}
		}
	});
};

let get_age = function (birth) {
	let birth_moment = moment(birth);
	let current_moment = moment(Date());
	let diff = moment.duration(current_moment.diff(birth_moment));
	return `${diff.years()} ${__('Year(s)')} ${diff.months()} ${__('Month(s)')} ${diff.days()} ${__('Day(s)')}`
};

let create_vital_signs = function (frm) {
	if (!frm.doc.name) {
		frappe.throw(__('Please save the patient first'));
	}
	frappe.route_options = {
		'patient': frm.doc.name,
	};
	frappe.new_doc('Vital Signs');
};

let create_encounter = function (frm) {
	if (!frm.doc.name) {
		frappe.throw(__('Please save the patient first'));
	}
	frappe.route_options = {
		'patient': frm.doc.name,
	};
	frappe.new_doc('Patient Encounter');
};

let invoice_registration = function (frm) {
	frappe.call({
		doc: frm.doc,
		method: 'invoice_patient_registration',
		callback: function(data) {
			if (!data.exc) {
				if (data.message.invoice) {
					frappe.set_route('Form', 'Sales Invoice', data.message.invoice);
				}
				cur_frm.reload_doc();
			}
		}
	});
};

let appointmentDialog = null;
const open_appointment_dialog = (frm) => {
	if (!appointmentDialog) {
		appointmentDialog = new frappe.ui.Dialog({
			title: __('Create Appointment'),
			fields: [
				{
					fieldname: 'patient_display',
					label: __('Patient'),
					fieldtype: 'Data',
					read_only: 1
				},
				{
					fieldname: 'practitioner',
					label: __('Healthcare Practitioner'),
					fieldtype: 'Link',
					options: 'Healthcare Practitioner',
					reqd: 1
				},
				{
					fieldname: 'appointment_type',
					label: __('Appointment Type'),
					fieldtype: 'Link',
					options: 'Appointment Type',
					reqd: 1
				},
				{
					fieldname: 'appointment_date',
					label: __('Appointment Date'),
					fieldtype: 'Date',
					reqd: 1
				},
				{
					fieldname: 'appointment_time',
					label: __('Appointment Time'),
					fieldtype: 'Time',
					reqd: 1
				},
				{
					fieldname: 'notes',
					label: __('Notes'),
					fieldtype: 'Small Text'
				}
			],
			primary_action_label: __('Create'),
			primary_action(values) {
				if (!values) return;
				const payload = {
					doctype: 'Patient Appointment',
					patient: frm.doc.name,
					patient_name: frm.doc.patient_name,
					practitioner: values.practitioner,
					appointment_type: values.appointment_type,
					appointment_date: values.appointment_date,
					appointment_time: values.appointment_time,
					status: 'Open',
					notes: values.notes
				};

				frappe.call({
					method: 'frappe.client.insert',
					args: { doc: payload },
					freeze: true,
					freeze_message: __('Creating appointment...'),
					callback: (r) => {
						if (!r.exc) {
							frappe.msgprint(__('Appointment {0} created successfully.', [r.message.name]));
							appointmentDialog.hide();
							appointmentDialog.set_values({
								practitioner: '',
								appointment_type: '',
								appointment_date: '',
								appointment_time: '',
								notes: ''
							});
							frappe.set_route('Form', 'Patient Appointment', r.message.name);
						}
					}
				});
			}
		});
	}

	appointmentDialog.set_values({
		patient_display: frm.doc.patient_name || frm.doc.name,
		patient: frm.doc.name
	});
	appointmentDialog.show();
};
