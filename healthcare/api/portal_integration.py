import frappe
from frappe import _
from frappe.utils import getdate, get_time

from healthcare.api import patient_self_service as pss


def _validate_required(data, required_fields):
	missing = [field for field in required_fields if not data.get(field)]
	if missing:
		frappe.throw(_("Missing required values: {0}").format(", ".join(missing)))


def _prepare_patient_payload(data):
	return frappe._dict({
		"patient_name": data.get("patient_name") or data.get("full_name"),
		"phone": data.get("phone"),
		"gender": data.get("gender"),
		"birth_date": data.get("birth_date"),
	})


@frappe.whitelist(allow_guest=True)
def register_patient(**kwargs):
	data = frappe._dict(kwargs)
	data.patient_name = data.get("patient_name") or data.get("full_name")

	_validate_required(data, ["patient_name", "phone"])

	patient_id = pss._get_or_create_patient(_prepare_patient_payload(data))

	return {
		"status": "success",
		"patient_id": patient_id
	}


@frappe.whitelist(allow_guest=True)
def create_booking_request(**kwargs):
	data = frappe._dict(kwargs)
	data.patient_name = data.get("patient_name") or data.get("full_name")

	_validate_required(data, ["patient_name", "phone"])

	patient_id = pss._get_or_create_patient(_prepare_patient_payload(data))

	appointment = _create_patient_appointment(patient_id, data)

	response = {
		"status": "success",
		"patient_id": patient_id,
	}

	if appointment:
		response.update({
			"appointment_id": appointment.name,
			"appointment_status": appointment.status
		})

	return response


def _create_patient_appointment(patient, data):
	if not data.get("appointment_date"):
		return None

	time_value = data.get("appointment_time") or "10:00:00"
	company = pss._get_default_company()
	default_appointment_type = frappe.db.get_value("Appointment Type", {}, "name")

	appointment_data = {
		"doctype": "Patient Appointment",
		"patient": patient,
		"appointment_date": getdate(data.appointment_date),
		"appointment_time": str(get_time(time_value)),
		"status": "Open",
		"notes": data.get("description") or data.get("symptoms"),
		"source": data.get("source") or "Patient Portal",
	}

	if data.get("practitioner"):
		appointment_data["practitioner"] = data.practitioner
		appointment_data["appointment_for"] = "Practitioner"

	if data.get("appointment_type"):
		appointment_data["appointment_type"] = data.appointment_type
	elif default_appointment_type:
		appointment_data["appointment_type"] = default_appointment_type

	if company:
		appointment_data["company"] = company

	if data.get("department"):
		appointment_data["department"] = data.department

	doc = frappe.get_doc(appointment_data)
	doc.insert(ignore_permissions=True)

	return doc


@frappe.whitelist(allow_guest=True)
def get_practitioners():
	try:
		practitioners = frappe.get_all(
			"Healthcare Practitioner",
			fields=[
				"name",
				"practitioner_name",
				"department",
				"mobile",
				"status",
				"profile_photo",
				"speciality",
			],
			filters={"status": "Active"},
			order_by="practitioner_name asc"
		)

		return {
			"status": "success",
			"practitioners": practitioners
		}
	except Exception as err:
		frappe.log_error(frappe.get_traceback(), "Portal Integration - get_practitioners")
		return {
			"status": "error",
			"message": str(err)
		}


@frappe.whitelist(allow_guest=True)
def get_appointment_types():
	try:
		appointment_types = frappe.get_all(
			"Appointment Type",
			fields=["name", "appointment_type", "default_duration"],
			order_by="appointment_type asc",
			ignore_permissions=True
		)

		return {
			"status": "success",
			"appointment_types": appointment_types
		}
	except Exception as err:
		frappe.log_error(frappe.get_traceback(), "Portal Integration - get_appointment_types")
		return {
			"status": "error",
			"message": str(err)
		}


@frappe.whitelist(allow_guest=True)
def get_practitioner_schedule(practitioner, appointment_date=None):
	"""
	Get practitioner schedule with time slots for a specific date.
	
	Args:
		practitioner: Healthcare Practitioner name/ID
		appointment_date: Optional date in YYYY-MM-DD format to filter by day
		
	Returns:
		Dictionary with schedule information and time slots
	"""
	from datetime import datetime
	
	if not practitioner:
		return {
			"status": "error",
			"message": "Practitioner is required"
		}
	
	try:
		# Get practitioner document
		practitioner_doc = frappe.get_doc("Healthcare Practitioner", practitioner)
		
		if not practitioner_doc.practitioner_schedules:
			return {
				"status": "success",
				"schedule_name": None,
				"time_slots": [],
				"disabled": True,
				"message": "No schedule configured for this practitioner"
			}
		
		# Get the first active schedule
		schedule_name = None
		for ps in practitioner_doc.practitioner_schedules:
			if hasattr(ps, 'schedule') and ps.schedule:
				schedule_name = ps.schedule
				break
		
		if not schedule_name:
			return {
				"status": "success",
				"schedule_name": None,
				"time_slots": [],
				"disabled": True
			}
		
		# Get schedule document
		schedule_doc = frappe.get_doc("Practitioner Schedule", schedule_name)
		
		# Convert time slots to list of dicts
		all_time_slots = []
		for slot in schedule_doc.time_slots:
			slot_data = {
				"day": slot.day,
				"from_time": str(slot.from_time) if slot.from_time else None,
				"to_time": str(slot.to_time) if slot.to_time else None,
				"duration": slot.duration if slot.duration and slot.duration > 0 else None,
				"maximum_appointments": slot.maximum_appointments if slot.maximum_appointments else 1
			}
			
			# Calculate duration from time difference if not set
			if not slot_data["duration"] and slot_data["from_time"] and slot_data["to_time"]:
				try:
					from_dt = datetime.strptime(slot_data["from_time"], "%H:%M:%S")
					to_dt = datetime.strptime(slot_data["to_time"], "%H:%M:%S")
					if to_dt < from_dt:
						to_dt = to_dt.replace(day=to_dt.day + 1) if hasattr(to_dt, 'day') else to_dt
					duration_minutes = (to_dt - from_dt).total_seconds() / 60
					slot_data["duration"] = int(duration_minutes) if duration_minutes > 0 else 30
				except:
					slot_data["duration"] = 30
			
			all_time_slots.append(slot_data)
		
		# Filter by day if appointment_date provided
		time_slots = all_time_slots
		if appointment_date:
			try:
				date_obj = datetime.strptime(appointment_date, "%Y-%m-%d")
				days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
				day_name = days[date_obj.weekday()]
				time_slots = [slot for slot in all_time_slots if slot["day"] == day_name]
			except:
				pass
		
		return {
			"status": "success",
			"schedule_name": schedule_name,
			"time_slots": time_slots,
			"all_time_slots": all_time_slots,
			"disabled": schedule_doc.disabled or 0,
			"is_working_day": len(time_slots) > 0 if appointment_date else None
		}
	except frappe.DoesNotExistError:
		return {
			"status": "error",
			"message": f"Practitioner {practitioner} not found"
		}
	except Exception as e:
		frappe.log_error(f"Error getting practitioner schedule: {str(e)}", "Get Practitioner Schedule")
		return {
			"status": "error",
			"message": str(e)
		}


@frappe.whitelist(allow_guest=True)
def get_appointments_for_date(practitioner, appointment_date):
	"""
	Get all appointments for a practitioner on a specific date.
	
	Args:
		practitioner: Healthcare Practitioner name/ID
		appointment_date: Date in YYYY-MM-DD format
		
	Returns:
		Dictionary with list of appointments (time and duration)
	"""
	from datetime import datetime, timedelta
	
	if not practitioner or not appointment_date:
		return {
			"status": "error",
			"message": "Practitioner and appointment_date are required"
		}
	
	try:
		appointments = frappe.get_all(
			"Patient Appointment",
			filters={
				"practitioner": practitioner,
				"appointment_date": appointment_date,
				"status": ["!=", "Cancelled"],
				"docstatus": ["<", 2]  # Include Draft (0) and Submitted (1)
			},
			fields=["appointment_time", "duration"]
		)
		
		# Normalize appointment times to HH:MM:SS format
		normalized_appointments = []
		for apt in appointments:
			apt_time = apt.get("appointment_time")
			if apt_time:
				# Handle timedelta objects
				if isinstance(apt_time, timedelta):
					total_seconds = int(apt_time.total_seconds())
					hours = total_seconds // 3600
					minutes = (total_seconds % 3600) // 60
					seconds = total_seconds % 60
					time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
				else:
					# Convert to string and normalize
					time_str = str(apt_time)
					if ':' in time_str:
						parts = time_str.split(':')
						if len(parts) >= 2:
							hour = parts[0].zfill(2)
							minute = parts[1].zfill(2)
							second = parts[2].zfill(2) if len(parts) > 2 else "00"
							time_str = f"{hour}:{minute}:{second}"
						else:
							continue
					else:
						continue
				
				duration = apt.get("duration", 30)
				if not duration or duration == 0:
					duration = 30
				
				normalized_appointments.append({
					"appointment_time": time_str,
					"duration": duration
				})
		
		return {
			"status": "success",
			"appointments": normalized_appointments,
			"count": len(normalized_appointments)
		}
	except Exception as e:
		frappe.log_error(f"Error getting appointments: {str(e)}", "Get Appointments for Date")
		return {
			"status": "error",
			"message": str(e)
		}


@frappe.whitelist(allow_guest=True)
def get_medical_content(limit=10):
	try:
		limit = frappe.utils.cint(limit) or 10

		posts = frappe.get_all(
			"Blog Post",
			fields=["name", "title", "published_on", "content", "route", "blog_category"],
			filters={"published": 1},
			order_by="published_on desc",
			limit_page_length=limit
		)

		return {
			"status": "success",
			"posts": posts
		}
	except Exception as err:
		frappe.log_error(frappe.get_traceback(), "Portal Integration - get_medical_content")
		return {
			"status": "error",
			"message": str(err)
		}


@frappe.whitelist(allow_guest=True)
def get_day_summary(practitioner, date):
	"""
	Get day summary for a practitioner showing booked vs available appointments.
	
	Args:
		practitioner: Healthcare Practitioner name/ID
		date: Date in YYYY-MM-DD format
		
	Returns:
		Dictionary with:
		- practitioner: Practitioner ID
		- date: Date
		- booked_count: Number of booked appointments
		- available_count: Number of available time slots
		- booked_list: List of booked appointments with details
		- available_slots: List of available time slots
		- comparison: Summary comparison
	"""
	from datetime import datetime, timedelta
	
	if not practitioner or not date:
		return {
			"status": "error",
			"message": "Practitioner and date are required"
		}
	
	try:
		# 1. Get booked appointments
		booked_appointments = frappe.get_all(
			"Patient Appointment",
			filters={
				"practitioner": practitioner,
				"appointment_date": date,
				"status": ["!=", "Cancelled"],
				"docstatus": ["<", 2]  # Include Draft (0) and Submitted (1)
			},
			fields=["name", "appointment_time", "duration", "patient", "status"]
		)
		
		# Normalize booked appointments
		booked_list = []
		normalized_booked_times = []
		for apt in booked_appointments:
			apt_time = apt.get("appointment_time")
			if apt_time:
				# Handle timedelta objects
				if isinstance(apt_time, timedelta):
					total_seconds = int(apt_time.total_seconds())
					hours = total_seconds // 3600
					minutes = (total_seconds % 3600) // 60
					seconds = total_seconds % 60
					time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
				else:
					time_str = str(apt_time)
					if ':' in time_str:
						parts = time_str.split(':')
						if len(parts) >= 2:
							hour = parts[0].zfill(2)
							minute = parts[1].zfill(2)
							second = parts[2].zfill(2) if len(parts) > 2 else "00"
							time_str = f"{hour}:{minute}:{second}"
					else:
						continue
				
				duration = apt.get("duration", 30) or 30
				booked_list.append({
					"name": apt.get("name"),
					"appointment_time": time_str,
					"duration": duration,
					"patient": apt.get("patient"),
					"status": apt.get("status")
				})
				normalized_booked_times.append({
					"appointment_time": time_str,
					"duration": duration
				})
		
		booked_count = len(booked_list)
		
		# 2. Get practitioner schedule
		schedule_result = get_practitioner_schedule(practitioner, date)
		if schedule_result.get("status") != "success":
			return {
				"status": "error",
				"message": f"Could not get schedule: {schedule_result.get('message', 'Unknown error')}"
			}
		
		working_slots = schedule_result.get("time_slots", [])
		is_working_day = schedule_result.get("is_working_day", False)
		
		if not is_working_day or not working_slots:
			return {
				"status": "success",
				"practitioner": practitioner,
				"date": date,
				"booked_count": booked_count,
				"available_count": 0,
				"booked_list": booked_list,
				"available_slots": [],
				"comparison": {
					"is_working_day": False,
					"message": "This is not a working day for the practitioner"
				}
			}
		
		# 3. Generate all possible time slots from schedule
		all_slots = []
		schedule_duration = working_slots[0].get("duration", 15) if working_slots else 15
		
		for slot in working_slots:
			from_time_str = slot.get("from_time", "")
			to_time_str = slot.get("to_time", "")
			duration = slot.get("duration", schedule_duration) or schedule_duration
			
			if not from_time_str or not to_time_str:
				continue
			
			try:
				# Parse times
				from_dt = datetime.strptime(from_time_str, "%H:%M:%S")
				to_dt = datetime.strptime(to_time_str, "%H:%M:%S")
				
				# Generate slots every 'duration' minutes
				current = from_dt
				while current < to_dt:
					slot_time = current.strftime("%H:%M:%S")
					all_slots.append(slot_time)
					current = current + timedelta(minutes=duration)
			except:
				continue
		
		# 4. Filter out booked slots
		available_slots = []
		for slot_time in all_slots:
			# Check if this slot overlaps with any booked appointment
			is_available = True
			
			# Normalize slot_time
			if len(slot_time) == 5:  # HH:MM
				parts = slot_time.split(':')
				slot_time = f"{parts[0].zfill(2)}:{parts[1].zfill(2)}:00"
			elif len(slot_time) == 8:  # HH:MM:SS
				parts = slot_time.split(':')
				slot_time = f"{parts[0].zfill(2)}:{parts[1].zfill(2)}:{parts[2].zfill(2)}"
			
			# Check overlap with booked appointments
			for booked in normalized_booked_times:
				booked_time = booked.get("appointment_time")
				booked_duration = booked.get("duration", 30)
				
				try:
					slot_dt = datetime.strptime(slot_time, "%H:%M:%S")
					slot_start = datetime.combine(datetime.today(), slot_dt.time())
					slot_end = slot_start + timedelta(minutes=schedule_duration)
					
					booked_dt = datetime.strptime(booked_time, "%H:%M:%S")
					booked_start = datetime.combine(datetime.today(), booked_dt.time())
					booked_end = booked_start + timedelta(minutes=booked_duration)
					
					# Check for overlap
					if slot_end > booked_start and slot_start < booked_end:
						is_available = False
						break
				except:
					continue
			
			if is_available:
				available_slots.append(slot_time)
		
		available_count = len(available_slots)
		
		# 5. Prepare comparison summary
		comparison = {
			"is_working_day": True,
			"total_slots": len(all_slots),
			"booked_slots": booked_count,
			"available_slots": available_count,
			"utilization_percentage": round((booked_count / len(all_slots) * 100), 2) if all_slots else 0,
			"has_availability": available_count > 0,
			"message": f"{available_count} slots available" if available_count > 0 else "No slots available (day is full)"
		}
		
		return {
			"status": "success",
			"practitioner": practitioner,
			"date": date,
			"booked_count": booked_count,
			"available_count": available_count,
			"booked_list": booked_list,
			"available_slots": available_slots,
			"comparison": comparison
		}
		
	except Exception as e:
		frappe.log_error(f"Error getting day summary: {str(e)}\n{frappe.get_traceback()}", "Get Day Summary")
		return {
			"status": "error",
			"message": str(e)
		}

