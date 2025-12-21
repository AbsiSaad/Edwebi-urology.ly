import frappe
from frappe import _
from frappe.website.utils import build_response
from frappe.utils import getdate, nowdate, cint

no_cache = 1


def get_context(context):
	"""Get context for patient registration page"""
	context.title = _("Patient Registration")
	context.no_cache = 1
	context.today = nowdate()
	
	# Get gender options
	try:
		genders = frappe.get_all("Gender", fields=["name"], order_by="name")
		context.genders = genders if genders else [
			{"name": "Male"},
			{"name": "Female"},
			{"name": "Other"}
		]
	except Exception:
		# Fallback if Gender doctype doesn't exist
		context.genders = [
			{"name": "Male"},
			{"name": "Female"},
			{"name": "Other"}
		]
	
	# Get appointment types
	try:
		appointment_types = frappe.get_all(
			"Appointment Type",
			fields=["name", "appointment_type", "allow_booking_for"],
			order_by="appointment_type"
		)
		# Filter out disabled appointment types if the field exists
		context.appointment_types = [
			apt for apt in appointment_types 
			if not frappe.db.get_value("Appointment Type", apt.name, "disabled", ignore=True)
		] if appointment_types else []
	except Exception:
		context.appointment_types = []
	
	# Get healthcare practitioners
	try:
		practitioners = frappe.get_all(
			"Healthcare Practitioner",
			fields=["name", "practitioner_name"],
			filters={"status": "Active"},
			order_by="practitioner_name"
		)
		context.practitioners = practitioners if practitioners else []
	except Exception:
		context.practitioners = []
	
	# Get medical departments
	try:
		departments = frappe.get_all(
			"Medical Department",
			fields=["name", "department"],
			order_by="department"
		)
		context.departments = departments if departments else []
	except Exception:
		context.departments = []
	
	# Get service units
	try:
		service_units = frappe.get_all(
			"Healthcare Service Unit",
			fields=["name", "healthcare_service_unit_name"],
			filters={"allow_appointments": 1, "is_group": 0},
			order_by="healthcare_service_unit_name"
		)
		context.service_units = service_units if service_units else []
	except Exception:
		context.service_units = []
	
	return context


@frappe.whitelist(allow_guest=True)
def register_patient(**kwargs):
	"""Register a new patient and create appointment if appointment data is provided"""
	try:
		# For form-encoded POST requests, data is in frappe.form_dict
		# For JSON requests or direct calls, data is in kwargs
		if hasattr(frappe, 'form_dict') and frappe.form_dict:
			data = frappe.form_dict
		else:
			data = kwargs
		
		# Validate required fields
		if not data.get("first_name"):
			return {
				"success": False,
				"message": _("First Name is required")
			}
		
		if not data.get("last_name"):
			return {
				"success": False,
				"message": _("Last Name is required")
			}
		
		if not data.get("sex"):
			return {
				"success": False,
				"message": _("Gender is required")
			}
		
		if not data.get("mobile"):
			return {
				"success": False,
				"message": _("Mobile Number is required")
			}

		# Create Patient document
		patient = frappe.get_doc({
			"doctype": "Patient",
			"first_name": data.get("first_name", "").strip(),
			"last_name": data.get("last_name", "").strip(),
			"sex": data.get("sex"),
			"dob": data.get("dob") or None,
			"mobile": data.get("mobile", "").strip(),
			"email": data.get("email", "").strip() or None,
		})

		# Insert patient
		patient.insert(ignore_permissions=True)

		# Create appointment if appointment data is provided
		appointment_created = False
		appointment_name = None
		
		if data.get("appointment_type") and data.get("appointment_date"):
			try:
				# Get appointment type details
				appointment_type_doc = frappe.get_doc("Appointment Type", data.get("appointment_type"))
				appointment_for = appointment_type_doc.allow_booking_for
				
				# Get default company
				company = frappe.db.get_single_value("Global Defaults", "default_company")
				if not company:
					# Try to get from Healthcare Settings or use first available company
					company = frappe.db.get_single_value("Healthcare Settings", "company")
					if not company:
						companies = frappe.get_all("Company", limit=1)
						if companies:
							company = companies[0].name
				
				if not company:
					raise frappe.ValidationError(_("No company found. Please set up a company first."))
				
				# Validate appointment fields based on appointment_for
				if appointment_for == "Practitioner":
					if not data.get("practitioner"):
						raise frappe.ValidationError(_("Practitioner is required for this appointment type"))
					if not data.get("appointment_time"):
						raise frappe.ValidationError(_("Appointment time is required for practitioner appointments"))
				elif appointment_for == "Department":
					if not data.get("department"):
						raise frappe.ValidationError(_("Department is required for this appointment type"))
				elif appointment_for == "Service Unit":
					if not data.get("service_unit"):
						raise frappe.ValidationError(_("Service Unit is required for this appointment type"))
				
				# Create Patient Appointment
				appointment_doc = {
					"doctype": "Patient Appointment",
					"patient": patient.name,
					"appointment_type": data.get("appointment_type"),
					"appointment_date": data.get("appointment_date"),
					"company": company,
					"notes": data.get("appointment_notes") or None,
				}
				
				# Add fields based on appointment_for
				if appointment_for == "Practitioner":
					appointment_doc["practitioner"] = data.get("practitioner")
					appointment_doc["appointment_time"] = data.get("appointment_time")
				elif appointment_for == "Department":
					appointment_doc["department"] = data.get("department")
				elif appointment_for == "Service Unit":
					appointment_doc["service_unit"] = data.get("service_unit")
				
				appointment = frappe.get_doc(appointment_doc)
				appointment.insert(ignore_permissions=True)
				appointment_created = True
				appointment_name = appointment.name
				
			except Exception as e:
				# Log error but don't fail patient creation
				frappe.log_error(f"Error creating appointment for patient {patient.name}: {str(e)}", "Appointment Creation Error")
				# Continue with patient registration even if appointment fails

		# Commit the transaction
		frappe.db.commit()

		if appointment_created:
			return {
				"success": True,
				"message": _("Patient {0} registered and appointment {1} booked successfully!").format(patient.name, appointment_name),
				"patient_id": patient.name,
				"appointment_id": appointment_name,
				"redirect_url": "/patient-registration-page"
			}
		else:
			return {
				"success": True,
				"message": _("Patient {0} registered successfully!").format(patient.name),
				"patient_id": patient.name,
				"redirect_url": "/patient-registration-page"
			}

	except frappe.exceptions.ValidationError as e:
		frappe.db.rollback()
		return {
			"success": False,
			"message": str(e)
		}
	except frappe.exceptions.DuplicateEntryError:
		frappe.db.rollback()
		return {
			"success": False,
			"message": _("A patient with this information already exists. Please check your details.")
		}
	except Exception as e:
		frappe.db.rollback()
		import traceback
		error_message = f"Error registering patient: {str(e)}\n{traceback.format_exc()}"
		frappe.log_error(error_message, "Patient Registration Error")
		return {
			"success": False,
			"message": _("An error occurred while registering the patient: {0}").format(str(e))
		}

