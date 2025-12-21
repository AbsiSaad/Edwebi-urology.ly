import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import frappe
from frappe import _
from frappe.model.document import Document


class AppointmentWhatsAppCenter(Document):
	"""Single DocType used as a control panel for WhatsApp reminders."""

	pass


def _format_phone_for_whatsapp(phone: Optional[str]) -> Optional[str]:
	if not phone:
		return None

	digits = "".join(filter(str.isdigit, phone))

	if digits.startswith("00"):
		digits = digits[2:]
	if digits.startswith("218"):
		digits = digits[3:]
	if digits.startswith("0"):
		digits = digits[1:]

	if len(digits) < 8 or len(digits) > 10:
		return None

	return f"218{digits}"


def _format_datetime_arabic(value: Optional[str], appointment_date: Optional[str], appointment_time: Optional[str]) -> str:
	if value:
		try:
			dt = datetime.fromisoformat(value.replace(" ", "T"))
			day_names = ["الإثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"]
			day_name = day_names[dt.weekday()]
			hour = dt.hour
			minute = dt.minute
			if hour < 12:
				time_str = f"{hour}:{minute:02d} صباحاً"
			else:
				display_hour = hour if hour <= 12 else hour - 12
				time_str = f"{display_hour}:{minute:02d} مساءً"
			return f"{day_name} {dt.day}/{dt.month}/{dt.year} الساعة {time_str}"
		except Exception:
			pass

	if appointment_date or appointment_time:
		display_date = appointment_date or ""
		display_time = appointment_time or ""
		return f"{display_date} {display_time}".strip()

	return ""


def _build_message(patient_name: str, practitioner_name: str, appointment_datetime_display: str, company: Optional[str]) -> str:
	clinic_name = company or frappe.db.get_single_value("Healthcare Settings", "default_healthcare_service_unit") or _("العيادة")
	return (
		f"مرحبًا {patient_name or _('المريض')}،\n\n"
		f"لديك موعد مع {practitioner_name or _('الطبيب')} بتاريخ {appointment_datetime_display} في {clinic_name}.\n\n"
		"شكرًا لك، ونتمنى لك يومًا طيبًا."
	)


def _replace_template_placeholders(template: str, patient_name: str, practitioner_name: str, appointment_datetime_display: str, company: Optional[str]) -> str:
	"""Replace placeholders in template with actual values."""
	clinic_name = company or frappe.db.get_single_value("Healthcare Settings", "default_healthcare_service_unit") or _("العيادة")
	
	replacements = {
		"{{patient_name}}": patient_name or _("المريض"),
		"{{practitioner_name}}": practitioner_name or _("الطبيب"),
		"{{appointment_datetime}}": appointment_datetime_display or "",
		"{{company}}": clinic_name,
	}
	
	message = template
	for placeholder, value in replacements.items():
		message = message.replace(placeholder, str(value))
	
	return message


def _validate_whatsapp_token() -> Tuple[bool, Optional[str]]:
	"""Validate WhatsApp token before sending messages."""
	try:
		settings = frappe.get_single("WhatsApp Settings")
		if not settings.enabled:
			return False, _("WhatsApp غير مفعّل في الإعدادات")
		
		if not settings.token:
			return False, _("لم يتم تعيين رمز الوصول في إعدادات WhatsApp")
		
		# Try to validate token by making a simple API call
		import requests
		
		token = settings.get_password("token")
		headers = {
			"authorization": f"Bearer {token}",
			"content-type": "application/json"
		}
		
		# Try to get phone number info to validate token
		url = f"{settings.url}/{settings.version}/{settings.phone_id}"
		try:
			response = requests.get(url, headers=headers, timeout=5)
			if response.status_code == 401:
				error_data = response.json().get("error", {})
				if "expired" in str(error_data).lower() or "invalid" in str(error_data).lower():
					return False, _("انتهت صلاحية رمز الوصول. يرجى تحديثه في إعدادات WhatsApp")
			elif response.status_code != 200:
				return False, _("فشل التحقق من رمز الوصول")
		except requests.exceptions.RequestException:
			# If validation fails, we'll still try to send and catch the error
			pass
		
		return True, None
	except Exception as e:
		# If validation fails, we'll still try to send
		return True, None


def _create_whatsapp_message(phone: str, message: str, appointment_name: str) -> Tuple[bool, Optional[str], Optional[str]]:
	formatted_phone = _format_phone_for_whatsapp(phone)
	if not formatted_phone:
		return False, None, _("رقم الهاتف غير صالح")

	doc = frappe.get_doc(
		{
			"doctype": "WhatsApp Message",
			"type": "Outgoing",
			"to": f"+{formatted_phone}",
			"use_template": 0,  # Explicitly set to not use template
			"content_type": "text",
			"message": message,
			"reference_doctype": "Patient Appointment",
			"reference_name": appointment_name,
		}
	)
	
	# Set message_type directly (read_only fields can be set programmatically)
	# Must be "Manual" or "Template", not "Text"
	doc.message_type = "Manual"

	try:
		doc.insert(ignore_permissions=True)
		return True, doc.name, None
	except Exception as exc:
		error_msg = str(exc)
		# Check for token expiration errors
		if "expired" in error_msg.lower() or "invalid" in error_msg.lower() or "access token" in error_msg.lower():
			return False, None, _("انتهت صلاحية رمز الوصول في WhatsApp. يرجى تحديثه في: إعدادات WhatsApp > Token")
		return False, None, error_msg


@frappe.whitelist()
def fetch_appointments(appointment_date: str, practitioner: Optional[str] = None, general_template: Optional[str] = None) -> List[Dict]:
	if not appointment_date:
		frappe.throw(_("يرجى اختيار تاريخ الموعد"))

	filters = [
		["Patient Appointment", "appointment_date", "=", appointment_date],
		["Patient Appointment", "status", "!=", "Cancelled"],
	]
	if practitioner:
		filters.append(["Patient Appointment", "practitioner", "=", practitioner])

	appointments = frappe.get_all(
		"Patient Appointment",
		filters=filters,
		fields=[
			"name",
			"patient",
			"patient_name",
			"practitioner",
			"practitioner_name",
			"appointment_time",
			"appointment_datetime",
			"company",
		],
		order_by="appointment_time asc",
	)

	results = []
	for appointment in appointments:
		patient = frappe.db.get_value(
			"Patient", appointment.patient, ["patient_name", "mobile", "phone"], as_dict=True
		)
		phone_number = (patient or {}).get("mobile") or (patient or {}).get("phone")
		if not phone_number:
			continue

		# Format appointment datetime
		display_datetime = _format_datetime_arabic(
			appointment.appointment_datetime,
			appointment_date,
			appointment.appointment_time,
		)
		
		# Use general template if provided, otherwise use default
		if general_template and general_template.strip():
			default_message = _replace_template_placeholders(
				general_template,
				appointment.patient_name,
				appointment.practitioner_name,
				display_datetime,
				appointment.company,
			)
		else:
			default_message = _build_message(
				appointment.patient_name,
				appointment.practitioner_name,
				display_datetime,
				appointment.company,
			)

		results.append(
			{
				"patient": appointment.patient,
				"patient_name": appointment.patient_name,
				"phone": phone_number,
				"company": appointment.company,
				"practitioner_name": appointment.practitioner_name,
				"appointment_time": appointment.appointment_time,
				"appointment_datetime": appointment.appointment_datetime,
				"message": default_message,  # Include default message
				"status": "Pending",
				"last_message": "",
				"appointment_name": appointment.name,
			}
		)

	return results


@frappe.whitelist()
def send_whatsapp_messages(appointment_date: str, practitioner: Optional[str] = None, recipients_data: Optional[List[Dict]] = None) -> Dict:
	"""
	Send WhatsApp messages to recipients.
	
	Args:
		appointment_date: Date to filter appointments
		practitioner: Optional practitioner filter
		recipients_data: Optional list of recipients with custom messages from the form
	"""
	# Validate WhatsApp token before sending
	token_valid, token_error = _validate_whatsapp_token()
	if not token_valid and token_error:
		return {
			"status": "error",
			"message": token_error,
			"sent": 0,
			"failed": 0,
			"details": [],
		}
	
	# If recipients_data is provided, use it (from form with custom messages)
	# Otherwise, fetch from appointments
	if recipients_data:
		recipients = recipients_data
	else:
		recipients = fetch_appointments(appointment_date, practitioner)
	
	if not recipients:
		return {
			"status": "empty",
			"message": _("لا توجد مواعيد صالحة في هذا التاريخ."),
			"sent": 0,
			"failed": 0,
			"details": [],
		}

	sent = 0
	failed = 0
	details = []
	token_expired = False

	# Get general template from form if available
	general_template = None
	try:
		center_doc = frappe.get_single("Appointment WhatsApp Center")
		general_template = center_doc.get("general_message_template")
	except:
		pass

	for row in recipients:
		# Use custom message if provided, otherwise use general template or build default
		custom_message = row.get("message")
		if custom_message and custom_message.strip():
			message = custom_message.strip()
		elif general_template and general_template.strip():
			# Use general template with placeholders
			display_datetime = _format_datetime_arabic(
				row.get("appointment_datetime"),
				appointment_date,
				row.get("appointment_time"),
			)
			message = _replace_template_placeholders(
				general_template,
				row.get("patient_name"),
				row.get("practitioner_name"),
				display_datetime,
				row.get("company"),
			)
		else:
			# Build default message
			display_datetime = _format_datetime_arabic(
				row.get("appointment_datetime"),
				appointment_date,
				row.get("appointment_time"),
			)
			message = _build_message(
				row.get("patient_name"),
				row.get("practitioner_name"),
				display_datetime,
				row.get("company"),
			)

		# Get appointment_name from row (could be from recipients_data or from fetch_appointments)
		appointment_name = row.get("appointment_name") or row.get("name") or ""
		
		success, docname, error = _create_whatsapp_message(
			row.get("phone"), message, appointment_name
		)

		if success:
			sent += 1
			details.append(
				{
					"appointment": row.get("appointment_name"),
					"patient": row.get("patient_name"),
					"phone": row.get("phone"),
					"status": "Sent",
					"message_doc": docname,
				}
			)
		else:
			failed += 1
			# Check if error is token-related
			if error and ("expired" in error.lower() or "access token" in error.lower()):
				token_expired = True
			details.append(
				{
					"appointment": row.get("appointment_name"),
					"patient": row.get("patient_name"),
					"phone": row.get("phone"),
					"status": "Failed",
					"reason": error or _("فشل الإرسال"),
				}
			)
	
	# If token expired, add helpful message
	message = _("تمت محاولة إرسال الرسائل.")
	if token_expired:
		message = _("انتهت صلاحية رمز الوصول. يرجى تحديثه في: إعدادات WhatsApp > Token")

	return {
		"status": "complete",
		"message": message,
		"sent": sent,
		"failed": failed,
		"details": details,
	}


