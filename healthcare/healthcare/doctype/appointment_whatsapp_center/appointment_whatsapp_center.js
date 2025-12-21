frappe.ui.form.on('Appointment WhatsApp Center', {
	refresh(frm) {
		frm.disable_save();

		frm.add_custom_button(__('Fetch Appointments'), () => {
			fetchAppointments(frm);
		}, __('Actions'));

		frm.add_custom_button(__('Send WhatsApp Messages'), () => {
			sendMessages(frm);
		}, __('Actions'));

		// Add button to open WhatsApp Settings
		frm.add_custom_button(__('WhatsApp Settings'), () => {
			frappe.set_route('Form', 'WhatsApp Settings', 'WhatsApp Settings');
		}, __('Setup'));
	}
});

function fetchAppointments(frm) {
	if (!frm.doc.appointment_date) {
		frappe.msgprint(__('Please pick an appointment date.'));
		return;
	}

	frappe.call({
		method: 'healthcare.healthcare.doctype.appointment_whatsapp_center.appointment_whatsapp_center.fetch_appointments',
		args: {
			appointment_date: frm.doc.appointment_date,
			practitioner: frm.doc.practitioner,
			general_template: frm.doc.general_message_template  // Pass general template
		},
		freeze: true,
		freeze_message: __('Loading appointments...'),
		callback: (r) => {
			frm.clear_table('recipients');
			(r.message || []).forEach(row => {
				const child = frm.add_child('recipients');
				child.patient = row.patient;
				child.patient_name = row.patient_name;
				child.phone = row.phone;
				child.company = row.company;
				child.practitioner_name = row.practitioner_name;
				child.appointment_time = row.appointment_time;
				child.appointment_datetime = row.appointment_datetime;
				child.message = row.message || '';  // Populate default message
				child.status = row.status || 'Pending';
				child.last_message = row.last_message || '';
				child.appointment_name = row.appointment_name;  // Store for reference
			});
			frm.refresh_field('recipients');

			frappe.msgprint({
				title: __('Appointments Loaded'),
				message: __('Fetched {0} appointments.', [(r.message || []).length]),
				indicator: 'green'
			});
		}
	});
}

function sendMessages(frm) {
	if (!frm.doc.appointment_date) {
		frappe.msgprint(__('Please pick an appointment date.'));
		return;
	}

	// Prepare recipients data with custom messages from the form
	const recipients_data = (frm.doc.recipients || []).map(row => ({
		patient: row.patient,
		patient_name: row.patient_name,
		phone: row.phone,
		company: row.company,
		practitioner_name: row.practitioner_name,
		appointment_time: row.appointment_time,
		appointment_datetime: row.appointment_datetime,
		message: row.message || '',  // Include custom message
		appointment_name: row.appointment_name || row.patient,  // Use stored appointment_name if available
		status: row.status
	}));

	frappe.call({
		method: 'healthcare.healthcare.doctype.appointment_whatsapp_center.appointment_whatsapp_center.send_whatsapp_messages',
		args: {
			appointment_date: frm.doc.appointment_date,
			practitioner: frm.doc.practitioner,
			recipients_data: recipients_data  // Send recipients with custom messages
		},
		freeze: true,
		freeze_message: __('Sending WhatsApp messages...'),
		callback: (r) => {
			const data = r.message || {};
			const sent = data.sent || 0;
			const failed = data.failed || 0;
			const status = data.status || 'complete';
			const message = data.message || __('تمت محاولة إرسال الرسائل.');

			// Check if token expired
			const hasTokenError = message.includes('انتهت صلاحية') || message.includes('expired') || 
				status === 'error' || (data.details && data.details.some(d => 
					d.reason && (d.reason.includes('expired') || d.reason.includes('انتهت صلاحية'))));

			if (hasTokenError) {
				frappe.msgprint({
					title: __('انتهت صلاحية رمز الوصول'),
					message: __('<p>انتهت صلاحية رمز الوصول في WhatsApp.</p>' +
						'<p>يرجى تحديثه في: <a href="/app/whatsapp-settings" target="_blank">إعدادات WhatsApp</a> > Token</p>' +
						'<p>للحصول على رمز جديد، اذهب إلى: <a href="https://developers.facebook.com/apps" target="_blank">Meta for Developers</a></p>'),
					indicator: 'red'
				});
			} else {
				frappe.msgprint({
					title: __('WhatsApp Status'),
					message: __('<p>{0}</p><p>Sent: {1}<br>Failed: {2}</p>', [message, sent, failed]),
					indicator: failed > 0 ? 'orange' : 'green'
				});
			}

			if (Array.isArray(data.details)) {
				const rows = frm.doc.recipients || [];
				data.details.forEach(detail => {
					const match = rows.find(r => 
						(r.appointment_name === detail.appointment || r.patient_name === detail.patient) && 
						r.phone === detail.phone
					);
					if (match) {
						match.status = detail.status;
						match.last_message = detail.reason || detail.message_doc || '';
					}
				});
				frm.refresh_field('recipients');
			}
		},
		error: (r) => {
			frappe.msgprint({
				title: __('Error'),
				message: r.message || __('حدث خطأ أثناء إرسال الرسائل'),
				indicator: 'red'
			});
		}
	});
}


