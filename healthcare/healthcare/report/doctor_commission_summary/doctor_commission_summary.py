# -*- coding: utf-8 -*-
# Copyright (c) 2025, Healthcare and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{
			"fieldname": "doctor",
			"label": _("Doctor"),
			"fieldtype": "Link",
			"options": "Healthcare Practitioner",
			"width": 200
		},
		{
			"fieldname": "total_services",
			"label": _("Total Services"),
			"fieldtype": "Int",
			"width": 120
		},
		{
			"fieldname": "total_amount",
			"label": _("Total Amount"),
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"fieldname": "total_commission",
			"label": _("Total Commission"),
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"fieldname": "unpaid_commission",
			"label": _("Unpaid Commission"),
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"fieldname": "paid_commission",
			"label": _("Paid Commission"),
			"fieldtype": "Currency",
			"width": 150
		}
	]


def get_data(filters):
	if not filters:
		filters = {}
	conditions = get_conditions(filters)
	
	query = """
		SELECT
			dw.doctor,
			hp.practitioner_name as doctor_name,
			COUNT(DISTINCT dw.name) as total_services,
			SUM(dw.service_amount) as total_amount,
			SUM(dw.commission_amount) as total_commission,
			SUM(CASE WHEN dw.status = 'Unpaid' THEN dw.commission_amount ELSE 0 END) as unpaid_commission,
			SUM(CASE WHEN dw.status = 'Paid' THEN dw.commission_amount ELSE 0 END) as paid_commission
		FROM
			`tabDoctor Wallet` dw
		LEFT JOIN
			`tabHealthcare Practitioner` hp ON dw.doctor = hp.name
		WHERE
			dw.docstatus != 2
			{conditions}
		GROUP BY
			dw.doctor, hp.practitioner_name
		ORDER BY
			dw.doctor
	""".format(conditions=conditions)
	
	data = frappe.db.sql(query, filters, as_dict=True)
	
	return data


def get_conditions(filters):
	conditions = []
	
	# Add row-level permission for doctors
	user = frappe.session.user
	if "Physician" in frappe.get_roles(user) and "Healthcare Administrator" not in frappe.get_roles(user):
		# Get practitioner linked to user
		practitioner = frappe.db.get_value(
			"Healthcare Practitioner",
			{"user_id": user},
			"name"
		)
		if practitioner:
			conditions.append("dw.doctor = %(practitioner)s")
			if not filters:
				filters = {}
			filters["practitioner"] = practitioner
	
	if filters.get("doctor"):
		conditions.append("dw.doctor = %(doctor)s")
	
	if filters.get("status"):
		conditions.append("dw.status = %(status)s")
	
	if filters.get("from_date"):
		conditions.append("dw.date >= %(from_date)s")
	
	if filters.get("to_date"):
		conditions.append("dw.date <= %(to_date)s")
	
	return " AND " + " AND ".join(conditions) if conditions else ""

