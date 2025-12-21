# -*- coding: utf-8 -*-
# Copyright (c) 2025, Healthcare and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt
from healthcare.healthcare.scripts.doctor_commission_utils import (
	create_doctor_wallet_entry,
	reverse_doctor_wallet_entry
)


def on_therapy_session_submit(doc, method):
	"""Create commission entry when Therapy Session is submitted"""
	if not doc.practitioner:
		return
	
	# Get service amount from therapy session rate or invoice
	service_amount = 0
	reference_item = None
	
	# Try to get from therapy session rate
	if doc.rate:
		service_amount = flt(doc.rate)
	
	# If still no amount, try to get from therapy type item price
	if not service_amount and doc.therapy_type:
		therapy_type_doc = frappe.get_doc("Therapy Type", doc.therapy_type)
		if therapy_type_doc.item:
			reference_item = therapy_type_doc.item
			# Get item price
			price_list = frappe.db.get_value("Price List", {"selling": 1}, "name")
			if price_list:
				item_price = frappe.db.get_value(
					"Item Price",
					{"item_code": therapy_type_doc.item, "price_list": price_list},
					"price_list_rate"
				)
				if item_price:
					service_amount = flt(item_price)
	
	# If still no amount, try to get from sales invoice if invoiced
	if not service_amount and doc.invoiced:
		invoice_items = frappe.db.sql("""
			SELECT sii.rate, sii.qty, sii.item_code
			FROM `tabSales Invoice Item` sii
			INNER JOIN `tabSales Invoice` si ON si.name = sii.parent
			WHERE sii.reference_dt = 'Therapy Session'
			AND sii.reference_dn = %s
			AND si.docstatus = 1
			LIMIT 1
		""", (doc.name,), as_dict=True)
		
		if invoice_items:
			service_amount = invoice_items[0].rate * (invoice_items[0].qty or 1)
			reference_item = invoice_items[0].item_code
	
	# Create wallet entry
	if service_amount and service_amount > 0:
		create_doctor_wallet_entry(
			doctor=doc.practitioner,
			service_type="Therapy Session",
			service_reference=doc.name,
			service_amount=service_amount,
			date=doc.start_date,
			patient=doc.patient,
			appointment=doc.appointment,
			reference_item=reference_item
		)


def on_therapy_session_cancel(doc, method):
	"""Reverse commission entry when Therapy Session is cancelled"""
	reverse_doctor_wallet_entry("Therapy Session", doc.name)

