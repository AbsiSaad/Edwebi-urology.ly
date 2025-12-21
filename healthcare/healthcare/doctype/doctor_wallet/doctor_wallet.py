# -*- coding: utf-8 -*-
# Copyright (c) 2025, Healthcare and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint, flt, today


class DoctorWallet(Document):
	def before_insert(self):
		self.set_defaults_from_practitioner()
		self.sync_patient_details()

	def validate(self):
		self.set_defaults_from_practitioner()
		self.sync_patient_details()
		self.apply_commission_rule()
		self.calculate_commission()
		self.compute_net_payout()
		self.validate_duplicate_entry()

	def calculate_commission(self):
		"""Calculate commission amount based on service amount and chosen basis."""
		service_amount = flt(self.service_amount)
		basis = self.commission_basis or "Percentage"

		if basis == "Flat Amount":
			flat_amount = flt(self.flat_commission_amount or 0)
			if not flat_amount and self.commission_percentage:
				flat_amount = flt(service_amount * flt(self.commission_percentage) / 100, 2)

			self.commission_amount = flt(flat_amount, 2)
			return

		percentage = flt(self.commission_percentage or 0)
		if service_amount and percentage:
			self.commission_amount = flt(service_amount * percentage / 100, 2)
		else:
			self.commission_amount = 0

	def validate_duplicate_entry(self):
		"""Ensure commission is only generated once per service document"""
		if self.is_new():
			existing = frappe.db.exists(
				"Doctor Wallet",
				{
					"service_type": self.service_type,
					"service_reference": self.service_reference,
					"docstatus": ["!=", 2]
				}
			)
			if existing:
				frappe.throw(
					_("Commission entry already exists for {0} {1}").format(
						self.service_type, self.service_reference
					)
				)

	def on_update(self):
		"""Update status when payment entry is linked"""
		if self.payment_entry and self.status != "Paid":
			self.status = "Paid"
			if not self.paid_date:
				self.paid_date = today()

	@frappe.whitelist()
	def mark_as_paid(self, payment_entry=None):
		"""Mark wallet entry as paid"""
		self.status = "Paid"
		self.paid_date = today()
		if payment_entry:
			self.payment_entry = payment_entry
		self.save()
	
	def has_permission(self, permtype, user=None):
		"""Check if user has permission to access this document"""
		user = user or frappe.session.user
		
		# Healthcare Administrators have full access
		if "Healthcare Administrator" in frappe.get_roles(user):
			return True
		
		# Doctors can only see their own records
		if "Physician" in frappe.get_roles(user):
			# Get practitioner linked to user
			practitioner = frappe.db.get_value(
				"Healthcare Practitioner",
				{"user_id": user},
				"name"
			)
			if practitioner and self.doctor == practitioner:
				return True
		
		return False

	def set_defaults_from_practitioner(self):
		if not self.doctor:
			return

		practitioner_defaults = frappe.db.get_value(
			"Healthcare Practitioner",
			self.doctor,
			["company", "default_currency"],
			as_dict=True,
		)

		if practitioner_defaults:
			if practitioner_defaults.company and not self.company:
				self.company = practitioner_defaults.company
			if practitioner_defaults.default_currency and not self.currency:
				self.currency = practitioner_defaults.default_currency

		if not self.company:
			self.company = (
				frappe.db.get_single_value("Healthcare Settings", "company")
				or frappe.defaults.get_user_default("Company")
			)

		if self.company and not self.currency:
			self.currency = frappe.db.get_value("Company", self.company, "default_currency")

	def sync_patient_details(self):
		"""Sync patient and related details from service reference"""
		# If patient is already set, just sync name
		if self.patient and not self.patient_name:
			self.patient_name = frappe.db.get_value("Patient", self.patient, "patient_name")
		
		# If service_reference is set, try to fetch patient details from it
		# This should override existing values if service_reference is set
		if self.service_type and self.service_reference:
			if self.service_type == "Service Request":
				# Fetch details from Service Request - use get_doc for better access
				try:
					service_request_doc = frappe.get_doc("Service Request", self.service_reference)
					if service_request_doc:
						# Always update these fields from Service Request
						if service_request_doc.patient:
							self.patient = service_request_doc.patient
						if service_request_doc.patient_name:
							self.patient_name = service_request_doc.patient_name
						if service_request_doc.order_group:
							# Check if order_group is a Patient Encounter
							if frappe.db.exists("Patient Encounter", service_request_doc.order_group):
								self.encounter = service_request_doc.order_group
						if service_request_doc.practitioner:
							self.doctor = service_request_doc.practitioner
						if service_request_doc.company and not self.company:
							self.company = service_request_doc.company
						if service_request_doc.order_date and not self.date:
							self.date = service_request_doc.order_date
				except frappe.DoesNotExistError:
					# Service Request doesn't exist, skip
					pass
			elif self.service_type == "Patient Encounter":
				# Fetch details from Patient Encounter
				encounter = frappe.db.get_value(
					"Patient Encounter",
					self.service_reference,
					["patient", "patient_name", "appointment", "practitioner"],
					as_dict=True
				)
				if encounter:
					if not self.patient:
						self.patient = encounter.patient
					if not self.patient_name:
						self.patient_name = encounter.patient_name
					if not self.appointment:
						self.appointment = encounter.appointment
					if not self.encounter:
						self.encounter = self.service_reference
					if not self.doctor and encounter.practitioner:
						self.doctor = encounter.practitioner
			elif self.service_type == "Lab Test":
				# Fetch details from Lab Test
				lab_test = frappe.db.get_value(
					"Lab Test",
					self.service_reference,
					["patient", "patient_name", "practitioner"],
					as_dict=True
				)
				if lab_test:
					if not self.patient:
						self.patient = lab_test.patient
					if not self.patient_name:
						self.patient_name = lab_test.patient_name
					if not self.doctor and lab_test.practitioner:
						self.doctor = lab_test.practitioner
			elif self.service_type == "Clinical Procedure":
				# Fetch details from Clinical Procedure
				procedure = frappe.db.get_value(
					"Clinical Procedure",
					self.service_reference,
					["patient", "patient_name", "practitioner"],
					as_dict=True
				)
				if procedure:
					if not self.patient:
						self.patient = procedure.patient
					if not self.patient_name:
						self.patient_name = procedure.patient_name
					if not self.doctor and procedure.practitioner:
						self.doctor = procedure.practitioner
			elif self.service_type == "Therapy Session":
				# Fetch details from Therapy Session
				therapy = frappe.db.get_value(
					"Therapy Session",
					self.service_reference,
					["patient", "patient_name", "practitioner"],
					as_dict=True
				)
				if therapy:
					if not self.patient:
						self.patient = therapy.patient
					if not self.patient_name:
						self.patient_name = therapy.patient_name
					if not self.doctor and therapy.practitioner:
						self.doctor = therapy.practitioner
			elif self.service_type == "Patient Appointment":
				# Fetch details from Patient Appointment
				appointment = frappe.db.get_value(
					"Patient Appointment",
					self.service_reference,
					["patient", "patient_name", "practitioner", "appointment_date"],
					as_dict=True
				)
				if appointment:
					if not self.patient:
						self.patient = appointment.patient
					if not self.patient_name:
						self.patient_name = appointment.patient_name
					if not self.appointment:
						self.appointment = self.service_reference
					if not self.doctor and appointment.practitioner:
						self.doctor = appointment.practitioner
					if not self.date:
						self.date = appointment.appointment_date
			elif self.service_type == "Sales Invoice":
				# Fetch details from Sales Invoice
				sales_invoice = frappe.db.get_value(
					"Sales Invoice",
					self.service_reference,
					["patient", "customer"],
					as_dict=True
				)
				if sales_invoice and sales_invoice.patient:
					if not self.patient:
						self.patient = sales_invoice.patient
					if not self.patient_name:
						self.patient_name = frappe.db.get_value("Patient", sales_invoice.patient, "patient_name")

	def apply_commission_rule(self):
		if not self.doctor or not self.service_type or self.commission_rule:
			return

		rules = frappe.get_all(
			"Healthcare Practitioner Commission Rule",
			filters={
				"parent": self.doctor,
				"parenttype": "Healthcare Practitioner",
				"parentfield": "commission_rules",
				"service_type": self.service_type,
				"is_active": 1,
			},
			fields=[
				"name",
				"basis",
				"commission_percentage",
				"flat_amount",
				"auto_wallet_entry",
				"priority",
			],
			order_by="priority asc, modified asc",
		)

		if not rules:
			return

		rule = rules[0]
		self.commission_rule = rule.name
		if not self.commission_basis:
			self.commission_basis = rule.basis

		if rule.basis == "Percentage" and rule.commission_percentage is not None:
			self.commission_percentage = rule.commission_percentage
			self.flat_commission_amount = None
		elif rule.basis == "Flat Amount":
			self.flat_commission_amount = rule.flat_amount
			self.commission_percentage = 0

		if cint(rule.auto_wallet_entry):
			self.auto_created = 1

	def compute_net_payout(self):
		deductions = flt(self.deductions_amount or 0)
		net = flt(self.commission_amount) - deductions
		self.net_payout_amount = net if net > 0 else 0


@frappe.whitelist()
def create_payment_entry(wallet_entries):
	"""Create Payment Entry for doctor commission payments
	Creates one payment entry per doctor (Payment Entry supports one party at a time)
	"""
	from erpnext.accounts.utils import get_account_currency
	
	if not wallet_entries:
		frappe.throw(_("No wallet entries provided"))
	
	# For now, handle only first doctor (single payment entry)
	# If multiple doctors selected, create separate payment entries
	if isinstance(wallet_entries, dict):
		doctor = wallet_entries.get("doctor")
		entries = wallet_entries.get("entries") or []
	else:
		entries = wallet_entries if isinstance(wallet_entries, list) else [wallet_entries]
		doctor = None
	
	if not entries:
		frappe.throw(_("No wallet entries selected"))

	first_entry = frappe.get_doc("Doctor Wallet", entries[0])
	if not doctor:
		doctor = first_entry.doctor
	
	if not doctor:
		frappe.throw(_("Doctor not found"))
	
	# Get company
	company = first_entry.company or frappe.db.get_value("Healthcare Practitioner", doctor, "company")
	if not company:
		company = frappe.defaults.get_user_default("Company")
	
	# Get expense account (or use default payable)
	expense_account = frappe.db.get_value("Company", company, "default_expense_account")
	if not expense_account:
		# Try to get from accounts settings
		expense_account = frappe.db.get_value("Company", company, "default_payable_account")
	if not expense_account:
		frappe.throw(_("Please set Default Expense Account in Company {0}").format(company))
	
	# Get supplier from doctor
	supplier = frappe.db.get_value("Healthcare Practitioner", doctor, "supplier")
	if not supplier:
		frappe.throw(_("Please set Supplier for Healthcare Practitioner {0}").format(doctor))
	
	# Calculate total commission for this doctor
	# Ensure entries is a list
	if not isinstance(entries, list):
		entries = [entries]
	
	# Use frappe.db.get_all for safer query
	wallet_entries = frappe.get_all(
		"Doctor Wallet",
		filters={
			"name": ["in", entries],
			"status": "Unpaid",
			"doctor": doctor
		},
		fields=["net_payout_amount", "commission_amount"]
	)
	
	doctor_total = sum(
		flt(entry.net_payout_amount or entry.commission_amount or 0)
		for entry in wallet_entries
	)
	
	if doctor_total <= 0:
		frappe.throw(_("No unpaid commission found for selected entries"))
	
	# Get supplier account
	supplier_account = frappe.db.get_value("Supplier", supplier, "default_payable_account")
	if not supplier_account:
		supplier_account = frappe.db.get_value("Company", company, "default_payable_account")
	
	# Create payment entry
	payment_entry = frappe.new_doc("Payment Entry")
	payment_entry.payment_type = "Pay"
	payment_entry.party_type = "Supplier"
	payment_entry.party = supplier
	payment_entry.company = company
	payment_entry.posting_date = today()
	payment_entry.paid_from = expense_account
	payment_entry.paid_from_account_currency = get_account_currency(expense_account)
	payment_entry.paid_to = supplier_account
	payment_entry.paid_to_account_currency = get_account_currency(supplier_account)
	payment_entry.paid_amount = doctor_total
	payment_entry.received_amount = doctor_total
	payment_entry.target_exchange_rate = 1
	payment_entry.source_exchange_rate = 1
	
	# Add reference (optional - for tracking)
	payment_entry.append("references", {
		"reference_doctype": "Supplier",
		"reference_name": supplier,
		"total_amount": doctor_total,
		"outstanding_amount": doctor_total,
		"allocated_amount": doctor_total
	})
	
	# Save payment entry
	payment_entry.insert()
	
	# Update wallet entries
	for name in entries:
		wallet_doc = frappe.get_doc("Doctor Wallet", name)
		if wallet_doc.status == "Unpaid":
			wallet_doc.mark_as_paid(payment_entry.name)
	
	return payment_entry.name


@frappe.whitelist()
def bulk_mark_as_paid(filters=None, payment_entry=None):
	"""Bulk mark Doctor Wallet entries as paid based on filters
	
	Args:
		filters: Dictionary of filters (doctor, date_from, date_to, company, service_type, status)
		payment_entry: Optional Payment Entry name to link
	
	Returns:
		Dictionary with count of updated records
	"""
	import json
	from frappe.utils import getdate, today
	
	# Parse filters if it's a JSON string
	if isinstance(filters, str):
		try:
			filters = json.loads(filters)
		except json.JSONDecodeError:
			frappe.throw(_("Invalid filters format"))
	
	# Ensure filters is a dictionary
	if filters is None:
		filters = {}
	
	if not isinstance(filters, dict):
		frappe.throw(_("Filters must be a dictionary"))
	
	# Build query filters
	query_filters = {
		"status": "Unpaid",
		"docstatus": ["!=", 2]  # Not cancelled
	}
	
	# Apply filters (only if not None/empty)
	if filters.get("doctor"):
		query_filters["doctor"] = filters["doctor"]
	
	if filters.get("company"):
		query_filters["company"] = filters["company"]
	
	if filters.get("service_type"):
		query_filters["service_type"] = filters["service_type"]
	
	# Date range filter
	if filters.get("date_from") or filters.get("date_to"):
		if filters.get("date_from") and filters.get("date_to"):
			query_filters["date"] = ["between", [getdate(filters["date_from"]), getdate(filters["date_to"])]]
		elif filters.get("date_from"):
			query_filters["date"] = [">=", getdate(filters["date_from"])]
		elif filters.get("date_to"):
			query_filters["date"] = ["<=", getdate(filters["date_to"])]
	
	# Get all matching unpaid entries
	wallet_entries = frappe.get_all(
		"Doctor Wallet",
		filters=query_filters,
		fields=["name", "doctor", "status"],
		limit=10000  # Reasonable limit
	)
	
	if not wallet_entries:
		frappe.msgprint(_("No unpaid entries found matching the filters"))
		return {"count": 0, "updated": []}
	
	# Update each entry
	updated_count = 0
	updated_names = []
	paid_date = today()
	
	for entry in wallet_entries:
		try:
			wallet_doc = frappe.get_doc("Doctor Wallet", entry.name)
			if wallet_doc.status == "Unpaid":
				wallet_doc.status = "Paid"
				wallet_doc.paid_date = paid_date
				if payment_entry:
					wallet_doc.payment_entry = payment_entry
				wallet_doc.save(ignore_permissions=True)
				updated_count += 1
				updated_names.append(entry.name)
		except Exception as e:
			frappe.log_error(
				f"Error updating Doctor Wallet {entry.name}: {str(e)}",
				"Doctor Wallet Bulk Update"
			)
	
	frappe.msgprint(
		_("Successfully marked {0} entries as paid").format(updated_count),
		alert=True
	)
	
	return {
		"count": updated_count,
		"updated": updated_names
	}


@frappe.whitelist()
def get_service_details(service_type, service_reference):
	"""Get service details for auto-populating Doctor Wallet fields"""
	if not service_type or not service_reference:
		return {}
	
	result = {}
	
	if service_type == "Service Request":
		# Get full Service Request document to access all fields
		try:
			service_request_doc = frappe.get_doc("Service Request", service_reference)
			if service_request_doc:
				result = {
					"patient": service_request_doc.patient,
					"patient_name": service_request_doc.patient_name,
					"doctor": service_request_doc.practitioner,
					"company": service_request_doc.company,
					"date": service_request_doc.order_date
				}
				# Check if order_group is a Patient Encounter
				if service_request_doc.order_group and frappe.db.exists("Patient Encounter", service_request_doc.order_group):
					result["encounter"] = service_request_doc.order_group
				
				# Try to get service amount from related Sales Invoice (most accurate)
				sales_invoice_items = frappe.db.get_all(
					"Sales Invoice Item",
					filters={
						"reference_dt": "Service Request",
						"reference_dn": service_reference
					},
					fields=["rate", "qty", "amount", "parent"],
					limit=1
				)
				if sales_invoice_items:
					item = sales_invoice_items[0]
					# Use amount if available, otherwise calculate from rate * qty
					if item.amount:
						result["service_amount"] = item.amount
					elif item.rate and item.qty:
						result["service_amount"] = flt(item.rate) * flt(item.qty)
					elif item.rate:
						result["service_amount"] = item.rate
				else:
					# Try to get from Service Request item_code and quantity
					if service_request_doc.item_code:
						from erpnext.stock.get_item_details import get_item_details
						
						# Get customer for pricing
						customer = None
						if service_request_doc.patient:
							customer = frappe.db.get_value("Patient", service_request_doc.patient, "customer")
						
						# Get price list
						price_list_data = frappe.db.get_values(
							"Price List", {"selling": 1}, ["name", "currency"]
						)
						price_list = price_list_data[0][0] if price_list_data else None
						
						if customer and price_list:
							try:
								args = {
									"doctype": "Sales Invoice",
									"item_code": service_request_doc.item_code,
									"company": service_request_doc.company,
									"customer": customer,
									"selling_price_list": price_list,
									"price_list_currency": price_list_data[0][1] if price_list_data[0][1] else frappe.get_cached_value("Company", service_request_doc.company, "default_currency"),
									"plc_conversion_rate": 1.0,
									"conversion_rate": 1.0,
								}
								item_details = get_item_details(args)
								if item_details and item_details.get("price_list_rate"):
									qty = flt(service_request_doc.quantity) or 1
									result["service_amount"] = flt(item_details.get("price_list_rate")) * qty
							except Exception:
								# Fallback to simple item price lookup
								price_data = frappe.db.get_all(
									"Item Price",
									filters={"item_code": service_request_doc.item_code, "selling": 1},
									fields=["price_list_rate"],
									limit=1,
									order_by="valid_from desc"
								)
								if price_data and price_data[0].price_list_rate:
									qty = flt(service_request_doc.quantity) or 1
									result["service_amount"] = flt(price_data[0].price_list_rate) * qty
		except frappe.DoesNotExistError:
			frappe.throw(_("Service Request {0} does not exist").format(service_reference))
		except Exception as e:
			frappe.log_error(f"Error fetching Service Request details: {str(e)}", "Doctor Wallet Service Request")
	
	elif service_type == "Patient Encounter":
		encounter = frappe.db.get_value(
			"Patient Encounter",
			service_reference,
			["patient", "patient_name", "appointment", "practitioner", "company", "encounter_date"],
			as_dict=True
		)
		if encounter:
			result = {
				"patient": encounter.patient,
				"patient_name": encounter.patient_name,
				"doctor": encounter.practitioner,
				"appointment": encounter.appointment,
				"encounter": service_reference,
				"company": encounter.company,
				"date": encounter.encounter_date
			}
	
	elif service_type == "Lab Test":
		lab_test = frappe.db.get_value(
			"Lab Test",
			service_reference,
			["patient", "patient_name", "practitioner", "company", "test_date"],
			as_dict=True
		)
		if lab_test:
			result = {
				"patient": lab_test.patient,
				"patient_name": lab_test.patient_name,
				"doctor": lab_test.practitioner,
				"company": lab_test.company,
				"date": lab_test.test_date
			}
	
	elif service_type == "Clinical Procedure":
		procedure = frappe.db.get_value(
			"Clinical Procedure",
			service_reference,
			["patient", "patient_name", "practitioner", "company", "start_date"],
			as_dict=True
		)
		if procedure:
			result = {
				"patient": procedure.patient,
				"patient_name": procedure.patient_name,
				"doctor": procedure.practitioner,
				"company": procedure.company,
				"date": procedure.start_date
			}
	
	elif service_type == "Therapy Session":
		therapy = frappe.db.get_value(
			"Therapy Session",
			service_reference,
			["patient", "patient_name", "practitioner", "company", "start_date"],
			as_dict=True
		)
		if therapy:
			result = {
				"patient": therapy.patient,
				"patient_name": therapy.patient_name,
				"doctor": therapy.practitioner,
				"company": therapy.company,
				"date": therapy.start_date
			}
	
	elif service_type == "Patient Appointment":
		appointment = frappe.db.get_value(
			"Patient Appointment",
			service_reference,
			["patient", "patient_name", "practitioner", "appointment_date", "company"],
			as_dict=True
		)
		if appointment:
			result = {
				"patient": appointment.patient,
				"patient_name": appointment.patient_name,
				"doctor": appointment.practitioner,
				"appointment": service_reference,
				"company": appointment.company,
				"date": appointment.appointment_date
			}
			# Try to get service amount from related Sales Invoice
			sales_invoice_items = frappe.db.get_all(
				"Sales Invoice Item",
				filters={
					"reference_dt": "Patient Appointment",
					"reference_dn": service_reference
				},
				fields=["rate", "qty", "amount"],
				limit=1
			)
			if sales_invoice_items:
				item = sales_invoice_items[0]
				if item.amount:
					result["service_amount"] = item.amount
				elif item.rate and item.qty:
					result["service_amount"] = flt(item.rate) * flt(item.qty)
				elif item.rate:
					result["service_amount"] = item.rate
	
	elif service_type == "Sales Invoice":
		sales_invoice = frappe.db.get_value(
			"Sales Invoice",
			service_reference,
			["patient", "company", "posting_date"],
			as_dict=True
		)
		if sales_invoice and sales_invoice.patient:
			result = {
				"patient": sales_invoice.patient,
				"patient_name": frappe.db.get_value("Patient", sales_invoice.patient, "patient_name"),
				"company": sales_invoice.company,
				"date": sales_invoice.posting_date
			}
	
	return result

