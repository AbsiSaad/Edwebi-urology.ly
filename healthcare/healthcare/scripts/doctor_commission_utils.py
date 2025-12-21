# -*- coding: utf-8 -*-
# Copyright (c) 2025, Healthcare and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import cint, flt, today


def get_commission_rule(practitioner, service_type, reference_item=None, apply_on_amount="Bill Amount"):
	"""Get the best matching commission rule for a practitioner and service type"""
	if not practitioner:
		return None
	
	# Get practitioner doc
	practitioner_doc = frappe.get_doc("Healthcare Practitioner", practitioner)
	
	# Check if auto wallet entry is enabled
	if not cint(practitioner_doc.get("auto_wallet_entry", 0)):
		return None
	
	# Get commission rules from table
	rules = frappe.get_all(
		"Healthcare Practitioner Commission Rule",
		filters={
			"parent": practitioner,
			"parenttype": "Healthcare Practitioner",
			"parentfield": "commission_rules",
			"service_type": service_type,
			"is_active": 1,
		},
		fields=[
			"name",
			"basis",
			"commission_percentage",
			"flat_amount",
			"apply_on_amount",
			"reference_item",
			"priority",
			"auto_wallet_entry",
		],
		order_by="priority asc, modified asc",
	)
	
	if not rules:
		return None
	
	# Filter by reference_item if provided
	if reference_item:
		item_rules = [r for r in rules if r.reference_item == reference_item]
		if item_rules:
			rules = item_rules
	
	# Filter by apply_on_amount if provided
	if apply_on_amount:
		amount_rules = [r for r in rules if r.apply_on_amount == apply_on_amount]
		if amount_rules:
			rules = amount_rules
	
	# Return first matching rule
	return rules[0] if rules else None


def get_commission_percentage(practitioner, service_type):
	"""Get commission percentage for a practitioner and service type (legacy support)"""
	if not practitioner:
		return 0
	
	# Map service types to field names
	field_map = {
		"Encounter": "encounter_commission_percentage",
		"Patient Encounter": "encounter_commission_percentage",
		"Lab Test": "lab_commission_percentage",
		"Procedure": "procedure_commission_percentage",
		"Clinical Procedure": "procedure_commission_percentage",
		"Therapy": "therapy_commission_percentage",
		"Therapy Session": "therapy_commission_percentage",
		"Service Request": None,  # Service Request uses default or rules only
		"Sales Invoice": None,  # Sales Invoice uses default or rules only
		"Other": None,  # Other uses default or rules only
	}
	
	# Get practitioner doc
	practitioner_doc = frappe.get_doc("Healthcare Practitioner", practitioner)
	
	# Get service-specific commission
	field_name = field_map.get(service_type)
	if field_name:  # Only if field_name is not None
		service_commission = flt(practitioner_doc.get(field_name))
		if service_commission > 0:
			return service_commission
	
	# Fall back to default commission for all service types (including Service Request)
	default_commission = flt(practitioner_doc.get("default_commission_percentage", 0))
	return default_commission


def calculate_commission_amount(
	practitioner,
	service_type,
	service_amount,
	reference_item=None,
	apply_on_amount="Bill Amount"
):
	"""Calculate commission amount using rules or default settings"""
	if not practitioner or not service_amount or service_amount <= 0:
		return 0, None, None
	
	practitioner_doc = frappe.get_doc("Healthcare Practitioner", practitioner)
	
	# Try to get commission rule first
	rule = get_commission_rule(practitioner, service_type, reference_item, apply_on_amount)
	
	commission_basis = "Percentage"
	commission_percentage = 0
	flat_commission_amount = 0
	rule_name = None
	
	if rule:
		# Use rule
		rule_name = rule.name
		commission_basis = rule.basis
		
		if rule.basis == "Percentage":
			commission_percentage = flt(rule.commission_percentage or 0)
			commission_amount = flt(service_amount * commission_percentage / 100, 2)
		else:  # Flat Amount
			flat_commission_amount = flt(rule.flat_amount or 0)
			commission_amount = flat_commission_amount
	else:
		# Use default settings
		commission_basis = practitioner_doc.get("commission_basis") or "Percentage of Service"
		
		if commission_basis == "Rule Table Only":
			# No rule matched and basis is rule-only, skip
			return 0, None, None
		
		if commission_basis == "Flat Amount":
			# This shouldn't happen without a rule, but handle it
			commission_amount = 0
		else:
			# Percentage basis
			commission_percentage = get_commission_percentage(practitioner, service_type)
			if commission_percentage <= 0:
				return 0, None, None
			commission_amount = flt(service_amount * commission_percentage / 100, 2)
	
	# Apply minimum commission
	minimum_commission = flt(practitioner_doc.get("minimum_commission_amount") or 0)
	if minimum_commission > 0 and commission_amount < minimum_commission:
		commission_amount = minimum_commission
	
	# Apply commission cap
	commission_cap = flt(practitioner_doc.get("commission_cap_amount") or 0)
	if commission_cap > 0 and commission_amount > commission_cap:
		commission_amount = commission_cap
	
	return commission_amount, commission_basis, {
		"commission_percentage": commission_percentage,
		"flat_commission_amount": flat_commission_amount,
		"rule_name": rule_name,
	}


def create_doctor_wallet_entry(
	doctor,
	service_type,
	service_reference,
	service_amount,
	commission_percentage=None,
	date=None,
	patient=None,
	appointment=None,
	encounter=None,
	sales_invoice=None,
	reference_item=None,
	apply_on_amount="Bill Amount"
):
	"""Create a Doctor Wallet entry for commission with enhanced rule support"""
	
	# Check if entry already exists
	existing = frappe.db.exists(
		"Doctor Wallet",
		{
			"service_type": service_type,
			"service_reference": service_reference,
			"docstatus": ["!=", 2]
		}
	)
	
	if existing:
		# Entry already exists, skip
		return None
	
	# Get practitioner doc to check auto_wallet_entry
	practitioner_doc = frappe.get_doc("Healthcare Practitioner", doctor)
	if not cint(practitioner_doc.get("auto_wallet_entry", 0)):
		# Auto wallet entry disabled, skip
		return None
	
	# Calculate commission using new rules
	commission_amount, commission_basis, commission_details = calculate_commission_amount(
		doctor,
		service_type,
		service_amount,
		reference_item,
		apply_on_amount
	)
	
	# Skip if no commission
	if not commission_amount or commission_amount <= 0:
		return None
	
	# Skip if no service amount
	if not service_amount or service_amount <= 0:
		return None
	
	# Create wallet entry
	wallet = frappe.new_doc("Doctor Wallet")
	wallet.doctor = doctor
	wallet.date = date or today()
	wallet.service_type = service_type
	wallet.service_reference = service_reference
	wallet.service_amount = flt(service_amount)
	
	# Set commission details
	if commission_details:
		wallet.commission_basis = commission_basis.replace(" of Service", "")
		wallet.commission_rule = commission_details.get("rule_name")
		if commission_details.get("commission_percentage"):
			wallet.commission_percentage = flt(commission_details["commission_percentage"])
		if commission_details.get("flat_commission_amount"):
			wallet.flat_commission_amount = flt(commission_details["flat_commission_amount"])
	else:
		# Legacy support
		if commission_percentage is None:
			commission_percentage = get_commission_percentage(doctor, service_type)
		wallet.commission_percentage = flt(commission_percentage)
		wallet.commission_basis = "Percentage"
	
	# Set context fields
	if patient:
		wallet.patient = patient
	if appointment:
		wallet.appointment = appointment
	if encounter:
		wallet.encounter = encounter
	if sales_invoice:
		wallet.sales_invoice = sales_invoice
	
	wallet.status = "Unpaid"
	wallet.auto_created = 1
	
	# Save will trigger validation and calculation
	wallet.insert(ignore_permissions=True)
	frappe.db.commit()
	
	return wallet.name


def reverse_doctor_wallet_entry(service_type, service_reference):
	"""Cancel/reverse a Doctor Wallet entry when service is cancelled"""
	wallet_name = frappe.db.get_value(
		"Doctor Wallet",
		{
			"service_type": service_type,
			"service_reference": service_reference,
			"docstatus": ["!=", 2]
		},
		"name"
	)
	
	if wallet_name:
		try:
			wallet = frappe.get_doc("Doctor Wallet", wallet_name)
			if wallet.status == "Unpaid":
				# Check if wallet entry is submitted (docstatus = 1)
				if wallet.docstatus == 1:
					# Submitted document - can be cancelled
					wallet.cancel()
					frappe.db.commit()
					frappe.logger().info(f"Cancelled Doctor Wallet entry {wallet_name} for {service_type} {service_reference}")
				elif wallet.docstatus == 0:
					# Draft document - delete it instead of cancelling
					frappe.delete_doc("Doctor Wallet", wallet_name, ignore_permissions=True, force=True)
					frappe.db.commit()
					frappe.logger().info(f"Deleted draft Doctor Wallet entry {wallet_name} for {service_type} {service_reference}")
			else:
				frappe.msgprint(
					_("Cannot cancel wallet entry {0} as it is already paid").format(wallet_name),
					indicator="orange"
				)
		except Exception as e:
			# Truncate error message to avoid CharacterLengthExceededError (max 140 chars)
			error_msg = f"Error cancelling wallet {wallet_name} for {service_type} {service_reference}: {str(e)}"
			if len(error_msg) > 140:
				error_msg = error_msg[:137] + "..."
			frappe.log_error(error_msg, "Doctor Wallet Reverse")


