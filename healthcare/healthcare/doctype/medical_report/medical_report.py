# -*- coding: utf-8 -*-
# Copyright (c) 2025, Edwebi Urology and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import date_diff, getdate


class MedicalReport(Document):
	def __setup__(self):
		"""Called after document initialization to clean up removed fields"""
		self._cleanup_removed_fields()

	def __getattribute__(self, name):
		"""Intercept all attribute access to handle removed fields"""
		if name == "signs_symptoms":
			# Return None for removed field instead of raising AttributeError
			return None
		# For all other attributes, use normal lookup
		return super().__getattribute__(name)

	def get(self, key, filters=None, limit=None, default=None):
		"""Override get to handle removed fields"""
		if key == "signs_symptoms":
			return default if default is not None else None
		# Call parent get method
		return super().get(key, filters=filters, limit=limit, default=default)

	def set(self, key, value, as_value=False):
		"""Override set to ignore removed fields"""
		# Ignore signs_symptoms field if it's being set
		if key == "signs_symptoms":
			return
		# Call parent set method
		super().set(key, value, as_value=as_value)

	def before_insert(self):
		self.set_default_status()
		self._cleanup_removed_fields()

	def before_validate(self):
		self._cleanup_removed_fields()

	def _cleanup_removed_fields(self):
		"""Remove fields that have been removed from doctype but might still exist in document"""
		# Remove signs_symptoms field if it exists (field was removed from doctype)
		try:
			# Check if field exists in meta - if not, it was removed
			meta = frappe.get_meta(self.doctype)
			if not meta.has_field("signs_symptoms"):
				# Field was removed from doctype, clean it up from document
				# Access __dict__ directly to avoid triggering __getattribute__
				doc_dict = object.__getattribute__(self, '__dict__')
				if 'signs_symptoms' in doc_dict:
					del doc_dict['signs_symptoms']
		except Exception:
			# Silently handle any errors during cleanup
			pass

	def validate(self):
		self.set_patient_details()
		self.set_doctor_details()
		self.calculate_duration()
		self.validate_dates()

	def on_update(self):
		self.update_status()

	def set_default_status(self):
		if not self.status:
			self.status = "Draft"

	def set_patient_details(self):
		"""Fetch patient details from Encounter (priority) or Patient"""
		# If encounter is provided, fetch all details from encounter first
		if self.visit_encounter:
			encounter = frappe.get_doc("Patient Encounter", self.visit_encounter)
			
			# Set patient from encounter
			if encounter.patient:
				self.patient = encounter.patient
			
			# Set all patient info from encounter
			if encounter.patient_name:
				self.patient_name = encounter.patient_name
			if encounter.patient_sex:
				self.gender = encounter.patient_sex
			if encounter.patient_age:
				self.age = encounter.patient_age
			if encounter.patient:
				self.file_number = encounter.patient
			
			# Set doctor from encounter if not set
			if encounter.practitioner and not self.doctor:
				self.doctor = encounter.practitioner
			
			# Set report date from encounter if not set
			if encounter.encounter_date and not self.report_date:
				self.report_date = encounter.encounter_date
			
			# Auto-fill diagnosis from encounter if available
			if hasattr(encounter, 'diagnosis') and encounter.diagnosis and not self.diagnosis:
				diagnosis_list = []
				try:
					# Handle diagnosis as a list/table
					if isinstance(encounter.diagnosis, (list, tuple)):
						for diag in encounter.diagnosis:
							if isinstance(diag, dict):
								diagnosis_name = diag.get("diagnosis")
							elif hasattr(diag, "diagnosis"):
								diagnosis_name = diag.diagnosis
							else:
								diagnosis_name = str(diag)
							if diagnosis_name:
								diagnosis_list.append(diagnosis_name)
					
					if diagnosis_list:
						self.diagnosis = "<br>".join(diagnosis_list)
				except (AttributeError, TypeError) as e:
					# Silently handle errors when processing diagnosis
					frappe.log_error(f"Error processing diagnosis from encounter: {str(e)}", "Medical Report Diagnosis Error")
			
		
		# If no encounter or encounter doesn't have all info, fetch from Patient
		if self.patient:
			patient = frappe.get_doc("Patient", self.patient)
			# Only set fields that are not already set from encounter
			if not self.patient_name:
				self.patient_name = patient.patient_name
			if not self.gender:
				self.gender = patient.sex
			if not self.age:
				self.age = str(patient.age) if patient.age else ""
			if not self.file_number:
				self.file_number = patient.name

	def set_doctor_details(self):
		"""Fetch doctor details"""
		if self.doctor:
			practitioner = frappe.get_doc("Healthcare Practitioner", self.doctor)
			self.doctor_name = practitioner.practitioner_name or practitioner.name
			
			# Try to get license number from custom field if exists
			if not self.license_number:
				# Check if license_number field exists in Healthcare Practitioner doctype
				meta = frappe.get_meta("Healthcare Practitioner")
				if meta.has_field("license_number"):
					license_number = frappe.db.get_value(
						"Healthcare Practitioner",
						self.doctor,
						"license_number"
					)
					if license_number:
						self.license_number = license_number

	def calculate_duration(self):
		"""Calculate sick leave duration in days"""
		if self.sick_leave_from and self.sick_leave_to:
			from_date = getdate(self.sick_leave_from)
			to_date = getdate(self.sick_leave_to)
			
			if to_date >= from_date:
				days = date_diff(to_date, from_date) + 1
				self.duration = f"{days} {_('days')} / {days} {_('أيام')}"
			else:
				frappe.throw(_("Sick Leave To date must be greater than or equal to Sick Leave From date"))
		elif self.sick_leave_from and not self.sick_leave_to:
			self.duration = ""
		else:
			self.duration = ""

	def validate_dates(self):
		"""Validate date logic"""
		if self.sick_leave_from and self.sick_leave_to:
			if getdate(self.sick_leave_to) < getdate(self.sick_leave_from):
				frappe.throw(_("Sick Leave To date cannot be before Sick Leave From date"))
		
		if self.return_to_work_date and self.sick_leave_to:
			if getdate(self.return_to_work_date) < getdate(self.sick_leave_to):
				frappe.throw(_("Return to Work date should be after Sick Leave To date"))

	def update_status(self):
		"""Update status based on workflow state"""
		if self.workflow_state:
			state_map = {
				"Draft": "Draft",
				"Waiting for Doctor Approval": "Waiting for Doctor Approval",
				"Approved": "Approved",
				"Rejected": "Rejected"
			}
			if self.workflow_state in state_map:
				self.status = state_map[self.workflow_state]

	@frappe.whitelist()
	def request_approval(self):
		"""Request doctor approval"""
		if self.status == "Draft":
			self.status = "Waiting for Doctor Approval"
			self.save()
			frappe.msgprint(_("Medical Report sent for doctor approval"))
		else:
			frappe.throw(_("Only Draft reports can be sent for approval"))

	@frappe.whitelist()
	def approve_report(self):
		"""Approve the medical report"""
		if self.status == "Waiting for Doctor Approval":
			self.status = "Approved"
			self.save()
			frappe.msgprint(_("Medical Report approved"))
		else:
			frappe.throw(_("Only reports waiting for approval can be approved"))

	@frappe.whitelist()
	def reject_report(self):
		"""Reject the medical report"""
		if self.status == "Waiting for Doctor Approval":
			self.status = "Rejected"
			self.save()
			frappe.msgprint(_("Medical Report rejected"))
		else:
			frappe.throw(_("Only reports waiting for approval can be rejected"))

	@frappe.whitelist()
	def update_from_encounter(self):
		"""Update all fields from selected encounter"""
		if self.visit_encounter:
			self.set_patient_details()
			self.set_doctor_details()
			return {
				"patient": self.patient,
				"patient_name": self.patient_name,
				"gender": self.gender,
				"age": self.age,
				"file_number": self.file_number,
				"doctor": self.doctor,
				"doctor_name": self.doctor_name,
				"report_date": self.report_date
			}


@frappe.whitelist()
def create_medical_report_from_encounter(encounter_name):
	"""Create Medical Report from Patient Encounter"""
	encounter = frappe.get_doc("Patient Encounter", encounter_name)
	
	medical_report = frappe.new_doc("Medical Report")
	medical_report.patient = encounter.patient
	medical_report.visit_encounter = encounter_name
	medical_report.doctor = encounter.practitioner
	medical_report.report_date = encounter.encounter_date
	
	# Set patient details
	medical_report.set_patient_details()
	
	# Set doctor details
	medical_report.set_doctor_details()
	
	medical_report.insert(ignore_permissions=True)
	
	return medical_report


@frappe.whitelist()
def create_medical_report_from_patient(patient_name):
	"""Create Medical Report from Patient"""
	medical_report = frappe.new_doc("Medical Report")
	medical_report.patient = patient_name
	medical_report.set_patient_details()
	
	medical_report.insert(ignore_permissions=True)
	
	return medical_report

