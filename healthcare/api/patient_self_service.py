import frappe
from frappe import _
from frappe.utils import getdate, get_time


def _get_available_genders():
	"""Get list of available Gender values from ERPNext database."""
	try:
		genders = frappe.get_all("Gender", fields=["name"], order_by="name")
		return [g["name"] for g in genders] if genders else []
	except Exception:
		return []


def _normalize_gender(gender_value):
	"""Convert Arabic gender values to ERPNext Gender doctype values.
	
	Args:
		gender_value: Gender value in Arabic or English
		
	Returns:
		Valid Gender doctype name from ERPNext database or default
	"""
	# Handle None or empty values
	if not gender_value:
		frappe.log_error(f"_normalize_gender: Input is None or empty, returning default", "Gender Normalization")
		return _get_default_gender()
	
	# Convert to string and strip whitespace
	gender_value = str(gender_value).strip()
	
	# If empty after stripping, return default
	if not gender_value:
		frappe.log_error(f"_normalize_gender: Input is empty after strip, returning default", "Gender Normalization")
		return _get_default_gender()
	
	# Get available genders from ERPNext database
	available_genders = _get_available_genders()
	frappe.log_error(f"_normalize_gender: Input='{gender_value}', Available genders={available_genders}", "Gender Normalization")
	
	# If no genders exist in database, return default
	if not available_genders:
		frappe.log_error(f"_normalize_gender: No genders in DB, returning default", "Gender Normalization")
		return _get_default_gender()
	
	# Map Arabic values to common English equivalents
	arabic_to_english = {
		"ذكر": "Male",
		"ذكور": "Male",
		"رجل": "Male",
		"أنثى": "Female",
		"إناث": "Female",
		"امرأة": "Female",
		"بنت": "Female",
		"آخر": "Other",
		"أخرى": "Other",
	}
	
	# Check for exact Arabic match first
	if gender_value in arabic_to_english:
		english_equivalent = arabic_to_english[gender_value]
		frappe.log_error(f"_normalize_gender: Found Arabic match '{gender_value}' -> '{english_equivalent}'", "Gender Normalization")
		# Try to find matching gender in available genders (case-insensitive)
		for available in available_genders:
			if available.lower() == english_equivalent.lower():
				frappe.log_error(f"_normalize_gender: Found exact match '{available}'", "Gender Normalization")
				return available
		# If exact match not found, try to find any gender containing the word
		for available in available_genders:
			if english_equivalent.lower() in available.lower() or available.lower() in english_equivalent.lower():
				frappe.log_error(f"_normalize_gender: Found partial match '{available}'", "Gender Normalization")
				return available
		frappe.log_error(f"_normalize_gender: No match found for '{english_equivalent}', using default", "Gender Normalization")
		return available_genders[0] if available_genders else _get_default_gender()
	
	# Check if it's already a valid Gender in ERPNext (exact match)
	if gender_value in available_genders:
		frappe.log_error(f"_normalize_gender: Input is already valid gender '{gender_value}'", "Gender Normalization")
		return gender_value
	
	# Try case-insensitive match
	for available in available_genders:
		if available.lower() == gender_value.lower():
			frappe.log_error(f"_normalize_gender: Found case-insensitive match '{available}'", "Gender Normalization")
			return available
	
	# Map English values (case-insensitive) and try to match with available genders
	english_map = {
		"other": "Other",
		"male": "Male",
		"female": "Female",
	}
	
	try:
		lower_value = gender_value.lower()
		if lower_value in english_map:
			english_equivalent = english_map[lower_value]
			frappe.log_error(f"_normalize_gender: Found English map '{lower_value}' -> '{english_equivalent}'", "Gender Normalization")
			# Try to find matching gender in available genders
			for available in available_genders:
				if available.lower() == english_equivalent.lower():
					frappe.log_error(f"_normalize_gender: Found match '{available}'", "Gender Normalization")
					return available
			# Try partial match
			for available in available_genders:
				if english_equivalent.lower() in available.lower() or available.lower() in english_equivalent.lower():
					frappe.log_error(f"_normalize_gender: Found partial match '{available}'", "Gender Normalization")
					return available
	except Exception as e:
		frappe.log_error(f"_normalize_gender: Exception in English map: {str(e)}", "Gender Normalization")
		pass
	
	# Try common English abbreviations
	try:
		lower_value = gender_value.lower()
		if lower_value in ["m"]:
			# Try to find "Male" or similar
			for available in available_genders:
				if "male" in available.lower():
					frappe.log_error(f"_normalize_gender: Found abbreviation match '{available}'", "Gender Normalization")
					return available
		elif lower_value in ["f"]:
			# Try to find "Female" or similar
			for available in available_genders:
				if "female" in available.lower():
					frappe.log_error(f"_normalize_gender: Found abbreviation match '{available}'", "Gender Normalization")
					return available
	except Exception as e:
		frappe.log_error(f"_normalize_gender: Exception in abbreviations: {str(e)}", "Gender Normalization")
		pass
	
	# Return first available gender as default (usually "Male" or "Female")
	result = available_genders[0] if available_genders else _get_default_gender()
	frappe.log_error(f"_normalize_gender: No match found, returning default '{result}'", "Gender Normalization")
	return result


def _gender_exists(gender_name):
	"""Check if a Gender exists in ERPNext."""
	try:
		return frappe.db.exists("Gender", gender_name)
	except Exception:
		return False


def _get_default_gender():
	"""Get default gender value from ERPNext database."""
	# Get available genders from database
	available_genders = _get_available_genders()
	
	if available_genders:
		# Prefer "Male" if available, otherwise return first available
		for preferred in ["Male", "Female", "Other"]:
			for available in available_genders:
				if available.lower() == preferred.lower():
					return available
		# Return first available if no preferred match
		return available_genders[0]
	
	# If no genders exist, try to create "Male"
	try:
		if not _gender_exists("Male"):
			gender_doc = frappe.get_doc({
				"doctype": "Gender",
				"gender": "Male"
			})
			gender_doc.insert(ignore_permissions=True)
			frappe.db.commit()
			return "Male"
		return "Male"
	except Exception as e:
		frappe.log_error(f"Failed to create default Gender 'Male': {str(e)}", "Gender Creation Error")
		# If creation fails, try to get any existing gender
		try:
			existing = frappe.db.get_value("Gender", {}, "name")
			if existing:
				return existing
		except Exception:
			pass
	
	# Absolute last resort: return "Male" even if it doesn't exist
	# (ERPNext will throw an error, but at least we tried)
	return "Male"


@frappe.whitelist(allow_guest=True)
def get_active_practitioners():
	"""Get list of active healthcare practitioners for public access."""
	try:
		practitioners = frappe.get_all(
			"Healthcare Practitioner",
			fields=["name", "practitioner_name", "department"],
			filters={"status": "Active"},
			order_by="practitioner_name asc"
		)
		return {
			"status": "success",
			"doctors": practitioners
		}
	except Exception as e:
		frappe.log_error(f"Error fetching practitioners: {str(e)}")
		return {
			"status": "error",
			"message": str(e)
		}


@frappe.whitelist(allow_guest=True)
def get_appointment_types():
	"""Get list of available appointment types for public access."""
	try:
		# Get all appointment types - note: Appointment Type doctype doesn't have 'disabled' field
		# So we get all appointment types
		appointment_types = frappe.get_all(
			"Appointment Type",
			fields=["name", "appointment_type", "default_duration"],
			order_by="appointment_type asc",
			ignore_permissions=True
		)
		
		# Format the response
		formatted_types = [
			{
				"name": apt.get("name"),
				"appointment_type": apt.get("appointment_type") or apt.get("name"),
				"default_duration": apt.get("default_duration")
			}
			for apt in appointment_types
		]
		
		return {
			"status": "success",
			"appointment_types": formatted_types
		}
	except Exception as e:
		frappe.log_error(f"Error fetching appointment types: {str(e)}")
		return {
			"status": "error",
			"message": str(e)
		}


@frappe.whitelist(allow_guest=True)
def book_patient_appointment(**kwargs):
	"""Allow patients to book an appointment using basic contact information.
	
	Accepts data as keyword arguments (from JSON body or form data).
	"""
	
	# Get data from kwargs (Frappe automatically converts JSON/form data to kwargs)
	data = frappe._dict(
		{
			"patient_name": (kwargs.get("patient_name") or "").strip(),
			"phone": (kwargs.get("phone") or "").strip(),
			"gender": (kwargs.get("gender") or "").strip(),
			"practitioner": (kwargs.get("practitioner") or "").strip(),
			"appointment_type": (kwargs.get("appointment_type") or "").strip(),
			"appointment_date": kwargs.get("appointment_date"),
			"appointment_time": kwargs.get("appointment_time"),
			"birth_date": kwargs.get("birth_date"),
			"symptoms": (kwargs.get("symptoms") or "").strip(),
		}
	)

	_validate_required_fields(data)

	patient = _get_or_create_patient(data)
	appointment = _create_patient_appointment(patient, data)

	result = {
		"status": "success",
		"patient_id": patient,
	}
	
	if appointment:
		result["appointment_id"] = appointment.name
	
	return result


def _validate_required_fields(data):
	# Only patient_name and phone are strictly required
	required = ["patient_name", "phone"]
	missing = [field for field in required if not data.get(field)]
	if missing:
		field_labels = ", ".join(frappe.unscrub(field).title() for field in missing)
		frappe.throw(_("Missing required values: {0}").format(field_labels))
	
	# If appointment is being booked, validate appointment fields
	if data.get("appointment_date") or data.get("appointment_time"):
		if not data.get("practitioner"):
			# Allow booking without practitioner - will be assigned later
			pass
		if not data.get("appointment_date"):
			frappe.throw(_("Appointment date is required when booking an appointment"))
		if not data.get("appointment_time"):
			# Set default time if not provided
			data["appointment_time"] = "10:00:00"


def _get_or_create_patient(data):
	"""
	Get existing patient or create new one.
	Checks for existing patient by phone number (normalized) and name.
	"""
	# Normalize phone number for comparison (remove spaces, dashes, etc.)
	normalized_phone = data.phone.strip().replace(" ", "").replace("-", "").replace("_", "")
	
	# Try to find existing patient by phone number (exact match)
	existing = frappe.db.get_value("Patient", {"mobile": data.phone}, "name")
	if existing:
		frappe.log_error(f"Found existing patient by exact phone match: {existing}", "Patient Lookup")
		# Update dob if birth_date is provided and different from existing
		if data.birth_date:
			try:
				existing_dob = frappe.db.get_value("Patient", existing, "dob")
				new_dob = getdate(data.birth_date)
				if new_dob and (not existing_dob or existing_dob != new_dob):
					frappe.db.set_value("Patient", existing, "dob", new_dob)
					frappe.log_error(f"Updated existing patient '{existing}' DOB from '{existing_dob}' to '{new_dob}'", "Patient DOB Update")
			except Exception as e:
				frappe.log_error(f"Error updating DOB for existing patient '{existing}': {str(e)}", "Patient DOB Update")
		return existing
	
	# Try to find by normalized phone (in case phone is stored differently)
	if normalized_phone != data.phone:
		# Search for patients with similar phone numbers
		patients = frappe.get_all(
			"Patient",
			fields=["name", "mobile", "patient_name"],
			filters={"mobile": ["like", f"%{normalized_phone[-9:]}%"]}  # Last 9 digits
		)
		if patients:
			# Check if any patient has matching normalized phone
			for patient in patients:
				if patient.mobile:
					patient_phone_normalized = patient.mobile.strip().replace(" ", "").replace("-", "").replace("_", "")
				if patient_phone_normalized == normalized_phone:
					frappe.log_error(f"Found existing patient by normalized phone match: {patient.name}", "Patient Lookup")
					# Update dob if birth_date is provided and different from existing
					if data.birth_date:
						try:
							existing_dob = frappe.db.get_value("Patient", patient.name, "dob")
							new_dob = getdate(data.birth_date)
							if new_dob and (not existing_dob or existing_dob != new_dob):
								frappe.db.set_value("Patient", patient.name, "dob", new_dob)
								frappe.log_error(f"Updated existing patient '{patient.name}' DOB from '{existing_dob}' to '{new_dob}'", "Patient DOB Update")
						except Exception as e:
							frappe.log_error(f"Error updating DOB for existing patient '{patient.name}': {str(e)}", "Patient DOB Update")
					return patient.name
	
	# Try to find by name and phone combination (more strict check)
	if data.patient_name and data.phone:
		# Use get_all for complex filters with LIKE
		matching_patients = frappe.get_all(
			"Patient",
			fields=["name", "mobile", "patient_name"],
			filters=[
				["patient_name", "like", f"%{data.patient_name}%"],
				["mobile", "like", f"%{normalized_phone[-9:]}%"]
			]
		)
		if matching_patients:
			# Verify the match is good (normalized phone should match)
			for patient in matching_patients:
				if patient.mobile:
					patient_phone_normalized = patient.mobile.strip().replace(" ", "").replace("-", "").replace("_", "")
					if patient_phone_normalized == normalized_phone:
						frappe.log_error(f"Found existing patient by name and phone combination: {patient.name}", "Patient Lookup")
						# Update dob if birth_date is provided and different from existing
						if data.birth_date:
							try:
								existing_dob = frappe.db.get_value("Patient", patient.name, "dob")
								new_dob = getdate(data.birth_date)
								if new_dob and (not existing_dob or existing_dob != new_dob):
									frappe.db.set_value("Patient", patient.name, "dob", new_dob)
									frappe.log_error(f"Updated existing patient '{patient.name}' DOB from '{existing_dob}' to '{new_dob}'", "Patient DOB Update")
							except Exception as e:
								frappe.log_error(f"Error updating DOB for existing patient '{patient.name}': {str(e)}", "Patient DOB Update")
						return patient.name
	
	# If no existing patient found, proceed to create new one
	frappe.log_error(f"No existing patient found for phone: {data.phone}, name: {data.patient_name}. Creating new patient.", "Patient Lookup")

	# Normalize gender value to valid ERPNext Gender doctype value
	# This will always return a valid gender (defaults to "Male" if needed)
	original_gender = data.gender
	
	# Get available genders for logging
	available_genders = _get_available_genders()
	frappe.log_error(f"Available genders in DB: {available_genders}, Input gender: '{original_gender}'", "Gender Normalization")
	
	# Normalize the gender
	normalized_gender = _normalize_gender(data.gender)
	
	# Log for debugging
	frappe.log_error(f"Gender normalization: '{original_gender}' -> '{normalized_gender}'", "Gender Normalization")
	
	# Verify normalized_gender exists in database
	if normalized_gender and _gender_exists(normalized_gender):
		frappe.log_error(f"Gender '{normalized_gender}' verified in database", "Gender Normalization")
	else:
		frappe.log_error(f"Gender '{normalized_gender}' NOT found in database, getting default", "Gender Normalization")
		normalized_gender = _get_default_gender()
		frappe.log_error(f"Using default gender: '{normalized_gender}'", "Gender Normalization")
	
	# Final validation: ensure we have a valid gender that exists in database
	if not normalized_gender:
		normalized_gender = _get_default_gender()
		frappe.log_error(f"Gender is None, using default: '{normalized_gender}'", "Gender Normalization")
	
	if not _gender_exists(normalized_gender):
		# Get first available gender from database
		if available_genders:
			normalized_gender = available_genders[0]
			frappe.log_error(f"Default gender not found, using first available: '{normalized_gender}'", "Gender Normalization")
		else:
			normalized_gender = "Male"
			frappe.log_error(f"No genders in DB, forcing 'Male'", "Gender Normalization")
	
	# Final check: ensure normalized_gender is a valid string and exists
	if not isinstance(normalized_gender, str) or not normalized_gender.strip():
		normalized_gender = available_genders[0] if available_genders else "Male"
		frappe.log_error(f"Invalid gender format, using: '{normalized_gender}'", "Gender Normalization")
	
	# Verify one more time that it exists
	if not _gender_exists(normalized_gender):
		# Use first available gender
		normalized_gender = available_genders[0] if available_genders else "Male"
		frappe.log_error(f"Final check failed, using: '{normalized_gender}'", "Gender Normalization")
	
	frappe.log_error(f"Final gender value: '{normalized_gender}' (exists: {_gender_exists(normalized_gender)})", "Gender Normalization")
	
	# Build patient document
	# Note: sex field is required in Patient doctype, so normalized_gender should always be set
	patient_data = {
		"doctype": "Patient",
		"first_name": data.patient_name,
		"patient_name": data.patient_name,
		"mobile": data.phone,
		"sex": normalized_gender,  # Always set, as _normalize_gender returns a default
	}
	
	# Add date of birth if provided
	if data.birth_date:
		try:
			# getdate() can handle YYYY-MM-DD format strings
			dob_value = getdate(data.birth_date)
			if dob_value:
				patient_data["dob"] = dob_value
				frappe.log_error(f"Successfully set DOB: input='{data.birth_date}' -> output='{dob_value}' (type: {type(dob_value).__name__})", "Patient DOB Setting")
			else:
				frappe.log_error(f"getdate() returned None for birth_date '{data.birth_date}'", "Patient DOB Parsing")
		except Exception as e:
			frappe.log_error(f"Error parsing birth_date '{data.birth_date}': {str(e)}\nTraceback: {frappe.get_traceback()}", "Patient DOB Parsing")
			# Continue without DOB if parsing fails
	else:
		frappe.log_error(f"No birth_date provided in data. Available keys: {list(data.keys()) if hasattr(data, 'keys') else 'N/A'}, data type: {type(data).__name__}", "Patient DOB Missing")
	
	patient_doc = frappe.get_doc(patient_data)
	
	# Verify dob was set before inserting
	if "dob" in patient_data:
		frappe.log_error(f"DOB in patient_data before insert: '{patient_data['dob']}'", "Patient DOB Verification")
		frappe.log_error(f"DOB in patient_doc before insert: '{patient_doc.dob}'", "Patient DOB Verification")
	
	patient_doc.insert(ignore_permissions=True)
	
	# Verify dob was saved after inserting
	if hasattr(patient_doc, 'dob') and patient_doc.dob:
		frappe.log_error(f"DOB successfully saved to Patient '{patient_doc.name}': '{patient_doc.dob}'", "Patient DOB Success")
	else:
		frappe.log_error(f"WARNING: DOB not found in Patient '{patient_doc.name}' after insert. patient_doc.dob = '{getattr(patient_doc, 'dob', 'NOT SET')}'", "Patient DOB Warning")
	
	# Return the patient ID (name field) - this will be either naming series ID or patient name
	# depending on Healthcare Settings
	patient_id = patient_doc.name
	
	# If patient_id is the same as patient_name, it means naming series is not being used
	# In this case, we should still return it, but the frontend will filter it out
	return patient_id


def _create_patient_appointment(patient, data):
	# Only create appointment if appointment_date is provided
	if not data.get("appointment_date"):
		return None
	
	time_value = str(get_time(data.appointment_time)) if data.appointment_time else "10:00:00"
	company = _get_default_company()
	default_appointment_type = frappe.db.get_value("Appointment Type", {}, "name")

	appointment_data = {
		"doctype": "Patient Appointment",
		"patient": patient,
		"appointment_date": getdate(data.appointment_date),
		"appointment_time": time_value,
		"status": "Open",
		"notes": data.symptoms,
	}
	
	# Only add practitioner if provided
	if data.get("practitioner"):
		appointment_data["practitioner"] = data.practitioner
		appointment_data["appointment_for"] = "Practitioner"
	else:
		# If no practitioner, set appointment_for to Department or leave empty
		# You may need to set a default department here
		appointment_data["appointment_for"] = "Practitioner"

	appointment_doc = frappe.get_doc(appointment_data)

	# Use provided appointment_type or default
	if data.get("appointment_type"):
		appointment_doc.appointment_type = data.appointment_type
	elif default_appointment_type:
		appointment_doc.appointment_type = default_appointment_type

	if company:
		appointment_doc.company = company

	appointment_doc.insert(ignore_permissions=True)
	appointment_doc.flags.ignore_permissions = True
	appointment_doc.submit()

	return appointment_doc


def _get_default_company():
	company = None

	try:
		meta = frappe.get_meta("Healthcare Settings")
		if meta and meta.has_field("default_company"):
			company = frappe.db.get_single_value("Healthcare Settings", "default_company")
	except Exception:
		company = None

	if company:
		return company

	company = frappe.defaults.get_defaults().get("company")
	if company:
		return company

	return frappe.db.get_single_value("Global Defaults", "default_company")
