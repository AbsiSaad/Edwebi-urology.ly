# -*- coding: utf-8 -*-
# Copyright (c) 2025, Healthcare and contributors
# For license information, please see license.txt

import frappe
from healthcare.healthcare.scripts.doctor_commission_utils import (
	create_doctor_wallet_entry,
	reverse_doctor_wallet_entry
)


def on_lab_test_submit(doc, method):
	"""Create commission entry when Lab Test is submitted"""
	# Get practitioner - can be from lab_test_created_by, practitioner, or service_request
	practitioner = None
	
	if doc.practitioner:
		practitioner = doc.practitioner
	elif doc.lab_test_created_by:
		# Try to get practitioner from user
		practitioner = frappe.db.get_value("User", doc.lab_test_created_by, "name")
		# If user is linked to practitioner
		practitioner = frappe.db.get_value(
			"Healthcare Practitioner",
			{"user_id": doc.lab_test_created_by},
			"name"
		)
	
	if not practitioner and doc.service_request:
		# Get practitioner from service request
		practitioner = frappe.db.get_value("Service Request", doc.service_request, "practitioner")
	
	if not practitioner:
		return
	
	# Get service amount from lab test template or invoice
	service_amount = 0
	
	# Try to get from template item price
	if doc.template:
		template_doc = frappe.get_doc("Lab Test Template", doc.template)
		if template_doc.item:
			# Get item price
			price_list = frappe.db.get_value("Price List", {"selling": 1}, "name")
			if price_list:
				item_price = frappe.db.get_value(
					"Item Price",
					{"item_code": template_doc.item, "price_list": price_list},
					"price_list_rate"
				)
				if item_price:
					service_amount = item_price
	
	# If still no amount, try to get from sales invoice if invoiced
	if not service_amount and doc.invoiced:
		invoice_items = frappe.db.sql("""
			SELECT sii.rate, sii.qty
			FROM `tabSales Invoice Item` sii
			INNER JOIN `tabSales Invoice` si ON si.name = sii.parent
			WHERE sii.reference_dt = 'Lab Test'
			AND sii.reference_dn = %s
			AND si.docstatus = 1
			LIMIT 1
		""", (doc.name,), as_dict=True)
		
		if invoice_items:
			service_amount = invoice_items[0].rate * (invoice_items[0].qty or 1)
	
	# Create wallet entry
	if service_amount and service_amount > 0:
		# Get reference item from template
		reference_item = None
		if doc.template:
			template_doc = frappe.get_doc("Lab Test Template", doc.template)
			reference_item = template_doc.item
		
		create_doctor_wallet_entry(
			doctor=practitioner,
			service_type="Lab Test",
			service_reference=doc.name,
			service_amount=service_amount,
			date=doc.date or doc.submitted_date,
			patient=doc.patient,
			reference_item=reference_item
		)


def on_lab_test_cancel(doc, method):
	"""Reverse commission entry when Lab Test is cancelled"""
	reverse_doctor_wallet_entry("Lab Test", doc.name)


