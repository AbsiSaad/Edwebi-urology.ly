# -*- coding: utf-8 -*-
# Copyright (c) 2025, Healthcare and contributors
# For license information, please see license.txt

import frappe
from healthcare.healthcare.scripts.doctor_commission_utils import (
	create_doctor_wallet_entry,
	reverse_doctor_wallet_entry
)


def on_clinical_procedure_submit(doc, method):
	"""Create commission entry when Clinical Procedure is submitted"""
	if not doc.practitioner:
		return
	
	# Get service amount from procedure template or invoice
	service_amount = 0
	
	# Try to get from template item price
	if doc.procedure_template:
		template_doc = frappe.get_doc("Clinical Procedure Template", doc.procedure_template)
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
			WHERE sii.reference_dt = 'Clinical Procedure'
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
		if doc.procedure_template:
			template_doc = frappe.get_doc("Clinical Procedure Template", doc.procedure_template)
			reference_item = template_doc.item
		
		create_doctor_wallet_entry(
			doctor=doc.practitioner,
			service_type="Clinical Procedure",
			service_reference=doc.name,
			service_amount=service_amount,
			date=doc.start_date,
			patient=doc.patient,
			appointment=doc.appointment,
			reference_item=reference_item
		)


def on_clinical_procedure_cancel(doc, method):
	"""Reverse commission entry when Clinical Procedure is cancelled"""
	reverse_doctor_wallet_entry("Clinical Procedure", doc.name)


