# -*- coding: utf-8 -*-
# Copyright (c) 2020, earthians and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import json

from six import string_types

import frappe
from frappe import _
from frappe.model.mapper import get_mapped_doc
from frappe.utils import flt, getdate, now_datetime

from erpnext.stock.get_item_details import get_item_details

from healthcare.controllers.service_request_controller import ServiceRequestController
from healthcare.healthcare.doctype.healthcare_settings.healthcare_settings import (
	get_income_account,
	get_receivable_account,
)
from healthcare.healthcare.doctype.observation.observation import add_observation
from healthcare.healthcare.doctype.observation_template.observation_template import (
	get_observation_template_details,
)
from healthcare.healthcare.doctype.sample_collection.sample_collection import (
	set_component_observation_data,
)


class ServiceRequest(ServiceRequestController):
	def validate(self):
		super().validate()
		if self.template_dt and self.template_dn and not self.codification_table:
			template_doc = frappe.get_doc(self.template_dt, self.template_dn)
			for mcode in template_doc.codification_table:
				self.append("codification_table", (frappe.copy_doc(mcode)).as_dict())

	def set_title(self):
		if frappe.flags.in_import and self.title:
			return
		self.title = f"{self.patient_name} - {self.template_dn}"

	def before_insert(self):
		self.status = "draft-Request Status"

		if self.amended_from:
			frappe.db.set_value("Service Request", self.amended_from, "status", "revoked-Request Status")

		if self.template_dt == "Observation Template" and self.template_dn:
			self.sample_collection_required = frappe.db.get_value(
				"Observation Template", self.template_dn, "sample_collection_required"
			)

	def set_order_details(self):
		if not self.template_dt and not self.template_dn:
			frappe.throw(
				_("Order Template Type and Order Template are mandatory to create Service Request"),
				title=_("Missing Mandatory Fields"),
			)

		template = frappe.get_doc(self.template_dt, self.template_dn)
		# set item code
		self.item_code = template.get("item")

		if not self.patient_care_type and template.get("patient_care_type"):
			self.patient_care_type = template.patient_care_type

		if not self.staff_role and template.get("staff_role"):
			self.staff_role = template.staff_role

		if not self.intent:
			self.intent = frappe.db.get_single_value("Healthcare Settings", "default_intent")

		if not self.priority:
			self.priority = frappe.db.get_single_value("Healthcare Settings", "default_priority")

	def update_invoice_details(self, qty):
		"""
		updates qty_invoiced and set  billing status
		"""
		qty_invoiced = self.qty_invoiced + qty
		invoiced = 0
		if qty_invoiced == 0:
			status = "Pending"
		if qty_invoiced < self.quantity:
			status = "Partly Invoiced"
		else:
			invoiced = 1
			status = "Invoiced"

		self.db_set({"qty_invoiced": qty_invoiced, "billing_status": status})
		if self.template_dt == "Lab Test Template":
			dt = "Lab Test"
		elif self.template_dt == "Clinical Procedure Template":
			dt = "Clinical Procedure"
		elif self.template_dt == "Therapy Type":
			dt = "Therapy Session"
		elif self.template_dt == "Observation Template":
			dt = "Observation"
		dt_name = frappe.db.get_value(dt, {"service_request": self.name})
		frappe.db.set_value(dt, dt_name, "invoiced", invoiced)


def update_service_request_status(service_request, service_dt, service_dn, status=None, qty=1):
	# TODO: fix status updates from linked docs
	set_service_request_status(service_request, status)


@frappe.whitelist()
def set_service_request_status(service_request, status):
	frappe.db.set_value("Service Request", service_request, "status", status)


@frappe.whitelist()
def make_clinical_procedure(service_request):
	# Handle different input types: string (JSON or name), dict, or Document object
	if isinstance(service_request, string_types):
		# Try to parse as JSON, if it fails, treat as document name
		try:
			service_request = json.loads(service_request)
			service_request = frappe._dict(service_request)
		except (json.JSONDecodeError, TypeError, ValueError):
			# If parsing fails, assume it's a document name and fetch from DB
			service_request = frappe.get_doc("Service Request", service_request)
	elif isinstance(service_request, dict):
		# Convert dict to frappe._dict for easier attribute access
		service_request = frappe._dict(service_request)

	# Ensure we have a document object - fetch from DB if we only have a name
	if isinstance(service_request, frappe._dict) and service_request.get("name"):
		# If we have a name but missing fields, fetch the full document
		if not service_request.get("template_dn"):
			service_request = frappe.get_doc("Service Request", service_request.name)

	# Get billing_status - handle both dict and document objects
	if isinstance(service_request, frappe._dict):
		billing_status = service_request.get("billing_status")
		service_request_name = service_request.get("name")
	else:
		billing_status = getattr(service_request, "billing_status", None)
		service_request_name = getattr(service_request, "name", None)

	# Fetch billing_status from database if missing
	if not billing_status and service_request_name:
		billing_status = frappe.db.get_value(
			"Service Request", service_request_name, "billing_status"
		) or "Pending"

	# Check if invoicing is required
	if (
		frappe.db.get_single_value("Healthcare Settings", "process_service_request_only_if_paid")
		and billing_status != "Invoiced"
	):
		frappe.throw(
			_("Service Request need to be invoiced before proceeding"),
			title=_("Payment Required"),
		)

	# Helper function to get attribute value safely
	def get_attr(obj, attr, default=None):
		if isinstance(obj, frappe._dict):
			return obj.get(attr, default)
		return getattr(obj, attr, default)

	doc = frappe.new_doc("Clinical Procedure")
	doc.procedure_template = get_attr(service_request, "template_dn")
	doc.service_request = get_attr(service_request, "name")
	doc.company = get_attr(service_request, "company")
	doc.patient = get_attr(service_request, "patient")
	doc.patient_name = get_attr(service_request, "patient_name")
	doc.patient_sex = get_attr(service_request, "patient_gender")
	doc.patient_age = get_attr(service_request, "patient_age_data")
	doc.inpatient_record = get_attr(service_request, "inpatient_record")
	doc.practitioner = get_attr(service_request, "practitioner")
	doc.start_date = get_attr(service_request, "occurrence_date")
	doc.start_time = get_attr(service_request, "occurrence_time")
	doc.medical_department = get_attr(service_request, "medical_department")

	return doc


@frappe.whitelist()
def make_lab_test(service_request):
	if isinstance(service_request, string_types):
		# Try to parse as JSON, if it fails, treat as document name
		try:
			service_request = json.loads(service_request)
			service_request = frappe._dict(service_request)
		except (json.JSONDecodeError, TypeError, ValueError):
			# If parsing fails, assume it's a document name and fetch from DB
			service_request = frappe.get_doc("Service Request", service_request)

	# Get billing_status - handle both dict and document objects
	if isinstance(service_request, frappe._dict):
		billing_status = service_request.get("billing_status")
		if not billing_status and service_request.get("name"):
			billing_status = frappe.db.get_value(
				"Service Request", service_request.name, "billing_status"
			) or "Pending"
	else:
		billing_status = getattr(service_request, "billing_status", None)
		if not billing_status and hasattr(service_request, "name"):
			billing_status = frappe.db.get_value(
				"Service Request", service_request.name, "billing_status"
			) or "Pending"

	if (
		frappe.db.get_single_value("Healthcare Settings", "process_service_request_only_if_paid")
		and billing_status != "Invoiced"
	):
		frappe.throw(
			_("Service Request need to be invoiced before proceeding"),
			title=_("Payment Required"),
		)

	doc = frappe.new_doc("Lab Test")
	doc.template = service_request.template_dn
	doc.service_request = service_request.name
	doc.company = service_request.company
	doc.patient = service_request.patient
	doc.patient_name = service_request.patient_name
	doc.patient_sex = service_request.patient_gender
	doc.patient_age = service_request.patient_age_data
	doc.inpatient_record = service_request.inpatient_record
	doc.email = service_request.patient_email
	doc.mobile = service_request.patient_mobile
	doc.practitioner = service_request.practitioner
	doc.requesting_department = service_request.medical_department
	doc.date = service_request.occurrence_date
	doc.time = service_request.occurrence_time
	doc.invoiced = service_request.invoiced

	return doc


@frappe.whitelist()
def make_therapy_session(service_request):
	if isinstance(service_request, string_types):
		# Try to parse as JSON, if it fails, treat as document name
		try:
			service_request = json.loads(service_request)
			service_request = frappe._dict(service_request)
		except (json.JSONDecodeError, TypeError, ValueError):
			# If parsing fails, assume it's a document name and fetch from DB
			service_request = frappe.get_doc("Service Request", service_request)

	# Get billing_status - handle both dict and document objects
	if isinstance(service_request, frappe._dict):
		billing_status = service_request.get("billing_status")
		if not billing_status and service_request.get("name"):
			billing_status = frappe.db.get_value(
				"Service Request", service_request.name, "billing_status"
			) or "Pending"
	else:
		billing_status = getattr(service_request, "billing_status", None)
		if not billing_status and hasattr(service_request, "name"):
			billing_status = frappe.db.get_value(
				"Service Request", service_request.name, "billing_status"
			) or "Pending"

	if (
		frappe.db.get_single_value("Healthcare Settings", "process_service_request_only_if_paid")
		and billing_status != "Invoiced"
	):
		frappe.throw(
			_("Service Request need to be invoiced before proceeding"),
			title=_("Payment Required"),
		)

	doc = frappe.new_doc("Therapy Session")
	doc.therapy_type = service_request.template_dn
	doc.service_request = service_request.name
	doc.company = service_request.company
	doc.patient = service_request.patient
	doc.patient_name = service_request.patient_name
	doc.gender = service_request.patient_gender
	doc.patient_age = service_request.patient_age_data
	doc.practitioner = service_request.practitioner
	doc.department = service_request.medical_department
	doc.start_date = service_request.occurrence_date
	doc.start_time = service_request.occurrence_time
	doc.invoiced = service_request.invoiced

	return doc


@frappe.whitelist()
def make_observation(service_request):
	if isinstance(service_request, string_types):
		# Try to parse as JSON, if it fails, treat as document name
		try:
			service_request = json.loads(service_request)
			service_request = frappe._dict(service_request)
		except (json.JSONDecodeError, TypeError, ValueError):
			# If parsing fails, assume it's a document name and fetch from DB
			service_request = frappe.get_doc("Service Request", service_request)

	# Get billing_status - handle both dict and document objects
	if isinstance(service_request, frappe._dict):
		billing_status = service_request.get("billing_status")
		if not billing_status and service_request.get("name"):
			billing_status = frappe.db.get_value(
				"Service Request", service_request.name, "billing_status"
			) or "Pending"
	else:
		billing_status = getattr(service_request, "billing_status", None)
		if not billing_status and hasattr(service_request, "name"):
			billing_status = frappe.db.get_value(
				"Service Request", service_request.name, "billing_status"
			) or "Pending"

	if (
		frappe.db.get_single_value("Healthcare Settings", "process_service_request_only_if_paid")
		and billing_status != "Invoiced"
	):
		frappe.throw(
			_("Service Request need to be invoiced before proceeding"),
			title=_("Payment Required"),
		)

	patient = frappe.get_doc("Patient", service_request.patient)
	template = frappe.get_doc("Observation Template", service_request.template_dn)

	sample_collection = ""
	name_ref_in_child = check_observation_sample_exist(service_request)

	if name_ref_in_child:
		return name_ref_in_child[0], name_ref_in_child[1], "New"
	else:
		exist_sample_collection = frappe.db.exists(
			"Sample Collection",
			{
				"reference_name": service_request.order_group,
				"docstatus": 0,
				"patient": service_request.patient,
			},
		)

	if template.has_component:
		if exist_sample_collection:
			sample_collection = frappe.get_doc("Sample Collection", exist_sample_collection)
		else:
			sample_collection = create_sample_collection(patient, service_request)

		# parent
		observation = create_observation(service_request)

		save_sample_collection = False
		(
			sample_reqd_component_obs,
			non_sample_reqd_component_obs,
		) = get_observation_template_details(service_request.template_dn)
		if len(non_sample_reqd_component_obs) > 0:
			for comp in non_sample_reqd_component_obs:
				add_observation(
					patient=service_request.patient,
					template=comp,
					doc="Patient Encounter",
					docname=service_request.order_group,
					parent=observation.name,
				)

		if len(sample_reqd_component_obs) > 0:
			save_sample_collection = True
			obs_template = frappe.get_doc("Observation Template", service_request.template_dn)
			data = set_component_observation_data(service_request.template_dn)
			# append parent template
			sample_collection.append(
				"observation_sample_collection",
				{
					"observation_template": service_request.template_dn,
					"sample": obs_template.sample,
					"sample_type": obs_template.sample_type,
					"container_closure_color": frappe.db.get_value(
						"Observation Template",
						service_request.template_dn,
						"container_closure_color",
					),
					"component_observations": json.dumps(data),
					"uom": obs_template.uom,
					"status": "Open",
					"sample_qty": obs_template.sample_qty,
					"component_observation_parent": observation.name,
					"service_request": service_request.name,
				},
			)

		if save_sample_collection:
			sample_collection.save(ignore_permissions=True)

	else:
		if template.get("sample_collection_required"):
			if exist_sample_collection:
				sample_collection = frappe.get_doc("Sample Collection", exist_sample_collection)
				sample_collection.append(
					"observation_sample_collection",
					{
						"observation_template": service_request.template_dn,
						"sample": template.sample,
						"sample_type": template.sample_type,
						"container_closure_color": frappe.db.get_value(
							"Observation Template",
							service_request.template_dn,
							"container_closure_color",
						),
						"uom": template.uom,
						"status": "Open",
						"sample_qty": template.sample_qty,
						"service_request": service_request.name,
					},
				)
				sample_collection.save(ignore_permissions=True)
			else:
				sample_collection = create_sample_collection(patient, service_request, template)
				sample_collection.save(ignore_permissions=True)
		else:
			observation = create_observation(service_request)

	diagnostic_report = frappe.db.exists(
		"Diagnostic Report", {"docname": service_request.order_group}
	)
	if not diagnostic_report:
		insert_diagnostic_report(service_request, sample_collection.name if sample_collection else None)

	if sample_collection:
		if diagnostic_report and not frappe.db.get_value(
			"Diagnostic Report", diagnostic_report, "sample_collection"
		):
			frappe.db.set_value(
				"Diagnostic Report", diagnostic_report, "sample_collection", sample_collection.name
			)
		return sample_collection.name, "Sample Collection"
	elif observation:
		return observation.name, "Observation"


def create_sample_collection(patient, service_request, template=None):
	sample_collection = frappe.new_doc("Sample Collection")
	sample_collection.patient = patient.name
	sample_collection.patient_age = patient.get_age()
	sample_collection.patient_sex = patient.sex
	sample_collection.company = service_request.company
	sample_collection.reference_doc = service_request.source_doc
	sample_collection.reference_name = service_request.order_group
	if template:
		sample_collection.append(
			"observation_sample_collection",
			{
				"observation_template": service_request.template_dn,
				"sample": template.sample,
				"sample_type": template.sample_type,
				"container_closure_color": frappe.db.get_value(
					"Observation Template", service_request.template_dn, "container_closure_color"
				),
				"uom": template.uom,
				"sample_qty": template.sample_qty,
				"service_request": service_request.name,
			},
		)
		sample_collection.save(ignore_permissions=True)
	return sample_collection


def create_observation(service_request):
	doc = frappe.new_doc("Observation")
	doc.posting_datetime = now_datetime()
	doc.patient = service_request.patient
	doc.observation_template = service_request.template_dn
	doc.reference_doctype = "Patient Encounter"
	doc.reference_docname = service_request.order_group
	doc.service_request = service_request.name
	doc.insert()
	return doc


def insert_diagnostic_report(doc, sample_collection=None):
	diagnostic_report = frappe.new_doc("Diagnostic Report")
	diagnostic_report.company = doc.company
	diagnostic_report.patient = doc.patient
	diagnostic_report.ref_doctype = doc.source_doc
	diagnostic_report.docname = doc.order_group
	diagnostic_report.practitioner = doc.practitioner
	diagnostic_report.sample_collection = sample_collection
	diagnostic_report.save(ignore_permissions=True)


def check_observation_sample_exist(service_request):
	name_ref_in_child = frappe.db.get_value(
		"Observation Sample Collection",
		{
			"service_request": service_request.name,
			"parenttype": "Sample Collection",
			"docstatus": ["!=", 2],
		},
		"parent",
	)
	if name_ref_in_child:
		return name_ref_in_child, "Sample Collection"
	else:
		exist_observation = frappe.db.exists(
			"Observation",
			{
				"service_request": service_request.name,
				"parent_observation": "",
				"docstatus": ["!=", 2],
			},
		)
		if exist_observation:
			return exist_observation, "Observation"


@frappe.whitelist()
def make_appointment(source_name, target_doc=None, ignore_permissions=False):
	def postprocess(source, target):
		set_missing_values(source, target)

	def set_missing_values(source, target):
		target.department = frappe.db.get_value(
			"Healthcare Practitioner", source.referred_to_practitioner, "department"
		)

	doclist = get_mapped_doc(
		"Service Request",
		source_name,
		{
			"Service Request": {
				"doctype": "Patient Appointment",
				"field_map": {
					"name": "service_request",
					"referred_to_practitioner": "practitioner",
					"template_dn": "appointment_type",
					"source_doc": "reference_doctype",
					"order_group": "reference_docname",
				},
				"field_no_map": ["naming_series", "status"],
			},
		},
		target_doc,
		postprocess,
		ignore_permissions=ignore_permissions,
	)

	return doclist


@frappe.whitelist()
def create_sales_invoice_from_service_request(service_request):
	"""Create Sales Invoice from Service Request"""
	if isinstance(service_request, string_types):
		# Try to parse as JSON, if it fails, treat as document name
		try:
			service_request = json.loads(service_request)
			service_request = frappe._dict(service_request)
		except (json.JSONDecodeError, TypeError, ValueError):
			# If parsing fails, assume it's a document name and fetch from DB
			service_request = frappe.get_doc("Service Request", service_request)
	elif isinstance(service_request, dict):
		# Convert dict to frappe._dict for easier attribute access
		service_request = frappe._dict(service_request)

	# Ensure we have a document object - fetch from DB if we only have a name
	if isinstance(service_request, frappe._dict) and service_request.get("name"):
		# If we have a name but missing fields, fetch the full document
		if not service_request.get("template_dn"):
			service_request = frappe.get_doc("Service Request", service_request.name)

	# Helper function to get attribute value safely
	def get_attr(obj, attr, default=None):
		if isinstance(obj, frappe._dict):
			return obj.get(attr, default)
		return getattr(obj, attr, default)

	# Validate required fields
	if not get_attr(service_request, "item_code"):
		frappe.throw(
			_("Service Request {0} does not have an item_code. Please set the item code in the template.").format(
				get_attr(service_request, "name", "")
			),
			title=_("Missing Item Code"),
		)

	# Get customer from patient
	patient = get_attr(service_request, "patient")
	if not patient:
		frappe.throw(
			_("Service Request {0} does not have a patient").format(
				get_attr(service_request, "name", "")
			),
			title=_("Missing Patient"),
		)

	customer = frappe.db.get_value("Patient", patient, "customer")
	if not customer:
		frappe.throw(
			_("Patient {0} is not linked to a customer. Please link a customer to the patient.").format(patient),
			title=_("Customer Not Found"),
		)

	# Check if item is billable
	template_dt = get_attr(service_request, "template_dt")
	template_dn = get_attr(service_request, "template_dn")
	if template_dt and template_dn:
		is_billable = frappe.db.get_value(template_dt, template_dn, "is_billable")
		if not is_billable:
			frappe.throw(
				_("The template {0} is not billable. Cannot create Sales Invoice.").format(template_dn),
				title=_("Not Billable"),
			)

	# Create Sales Invoice
	sales_invoice = frappe.new_doc("Sales Invoice")
	sales_invoice.patient = patient
	sales_invoice.customer = customer
	sales_invoice.due_date = getdate()
	company = get_attr(service_request, "company")
	sales_invoice.company = company
	sales_invoice.debit_to = get_receivable_account(company)

	# Get item details
	price_list, price_list_currency = frappe.db.get_values(
		"Price List", {"selling": 1}, ["name", "currency"]
	)[0] or [None, None]

	item_code = get_attr(service_request, "item_code")
	args = {
		"doctype": "Sales Invoice",
		"item_code": item_code,
		"company": company,
		"customer": customer,
		"selling_price_list": price_list,
		"price_list_currency": price_list_currency or frappe.get_cached_value("Company", company, "default_currency"),
		"plc_conversion_rate": 1.0,
		"conversion_rate": 1.0,
	}
	item_details = get_item_details(args)

	# Add item to invoice
	item = sales_invoice.append("items", {})
	item.item_code = item_code
	item.qty = get_attr(service_request, "quantity") or 1
	item.rate = item_details.get("price_list_rate", 0) if item_details else 0
	item.amount = flt(item.rate) * flt(item.qty)
	item.reference_dt = "Service Request"
	item.reference_dn = get_attr(service_request, "name")
	practitioner = get_attr(service_request, "practitioner")
	item.income_account = get_income_account(practitioner, company)

	# Set description from template if available
	if template_dt and template_dn:
		template_doc = frappe.get_doc(template_dt, template_dn)
		if hasattr(template_doc, "description") and template_doc.description:
			item.description = template_doc.description
		elif hasattr(template_doc, "lab_test_description") and template_doc.lab_test_description:
			item.description = template_doc.lab_test_description
		elif hasattr(template_doc, "order_description") and template_doc.order_description:
			item.description = template_doc.order_description

	# Get default mode of payment - try to get any enabled mode of payment
	default_mode_of_payment = frappe.db.get_value("Mode of Payment", {"enabled": 1}, "name", order_by="creation desc")
	if not default_mode_of_payment:
		# If no enabled mode found, try to get "Cash" or any mode
		default_mode_of_payment = frappe.db.get_value("Mode of Payment", "Cash", "name")
		if not default_mode_of_payment:
			# Get any mode of payment as last resort
			default_mode_of_payment = frappe.db.get_value("Mode of Payment", {}, "name", order_by="creation desc")
			if not default_mode_of_payment:
				# If no mode of payment exists at all, we can't create POS invoice
				frappe.throw(
					_("No Mode of Payment found. Please create at least one Mode of Payment to create paid invoices."),
					title=_("Mode of Payment Required")
				)

	# Calculate totals first to get the amount
	sales_invoice.set_missing_values(for_validate=True)
	
	# Make it a POS invoice and add payment to make it paid automatically
	sales_invoice.is_pos = 1
	payment = sales_invoice.append("payments", {})
	payment.mode_of_payment = default_mode_of_payment
	# Set initial payment amount (will be updated to exact grand_total after calculation)
	# Use item total as initial estimate
	estimated_total = item.amount
	payment.amount = estimated_total
	
	sales_invoice.flags.ignore_mandatory = True
	sales_invoice.save(ignore_permissions=True)
	
	# Now update payment amount to exact grand total to make it fully paid
	payment.amount = sales_invoice.grand_total
	sales_invoice.save(ignore_permissions=True)
	sales_invoice.submit()

	# Update Service Request billing status
	if isinstance(service_request, frappe._dict):
		service_request_doc = frappe.get_doc("Service Request", service_request.name)
	else:
		service_request_doc = service_request
	
	service_request_doc.update_invoice_details(item.qty)

	return {
		"sales_invoice": sales_invoice.name,
		"paid_amount": sales_invoice.grand_total
	}
