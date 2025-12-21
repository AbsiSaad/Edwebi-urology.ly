import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
	filters = frappe._dict(filters or {})
	columns = get_columns()
	data = get_data(filters)
	summary = get_summary(data)
	chart = get_chart(data)

	return columns, data, None, chart, summary


def get_columns():
	return [
		{"label": _("Date"), "fieldname": "date", "fieldtype": "Date", "width": 100},
		{
			"label": _("Doctor"),
			"fieldname": "doctor",
			"fieldtype": "Link",
			"options": "Healthcare Practitioner",
			"width": 160,
		},
		{"label": _("Service Type"), "fieldname": "service_type", "fieldtype": "Data", "width": 140},
		{
			"label": _("Service Reference"),
			"fieldname": "service_reference",
			"fieldtype": "Dynamic Link",
			"options": "service_type",
			"width": 160,
		},
		{
			"label": _("Service Amount"),
			"fieldname": "service_amount",
			"fieldtype": "Currency",
			"width": 120,
		},
		{
			"label": _("Commission %"),
			"fieldname": "commission_percentage",
			"fieldtype": "Percent",
			"width": 110,
		},
		{
			"label": _("Commission Amount"),
			"fieldname": "commission_amount",
			"fieldtype": "Currency",
			"width": 130,
		},
		{"label": _("Debit"), "fieldname": "debit", "fieldtype": "Currency", "width": 110},
		{"label": _("Credit"), "fieldname": "credit", "fieldtype": "Currency", "width": 110},
		{
			"label": _("Running Balance"),
			"fieldname": "running_balance",
			"fieldtype": "Currency",
			"width": 140,
		},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 90},
		{
			"label": _("Payment Entry"),
			"fieldname": "payment_entry",
			"fieldtype": "Link",
			"options": "Payment Entry",
			"width": 150,
		},
	]


def get_conditions(filters):
	conditions = ["dw.docstatus != 2"]
	values = {}

	if filters.get("doctor"):
		conditions.append("dw.doctor = %(doctor)s")
		values["doctor"] = filters.doctor

	if filters.get("status"):
		conditions.append("dw.status = %(status)s")
		values["status"] = filters.status

	if filters.get("from_date"):
		conditions.append("dw.date >= %(from_date)s")
		values["from_date"] = filters.from_date

	if filters.get("to_date"):
		conditions.append("dw.date <= %(to_date)s")
		values["to_date"] = filters.to_date

	return " AND ".join(conditions), values


def get_data(filters):
	conditions, values = get_conditions(filters)
	query = f"""
		SELECT
			dw.name,
			dw.doctor,
			dw.date,
			dw.service_type,
			dw.service_reference,
			dw.service_amount,
			dw.commission_percentage,
			dw.commission_amount,
			dw.status,
			dw.payment_entry,
			dw.paid_date
		FROM `tabDoctor Wallet` dw
		WHERE {conditions}
		ORDER BY dw.doctor, dw.date, dw.creation
	"""

	entries = frappe.db.sql(query, values, as_dict=True)
	running_balances = {}
	ledger = []

	for entry in entries:
		doctor = entry.doctor
		running_balances.setdefault(doctor, 0)

		debit = flt(entry.commission_amount)
		credit = debit if entry.status == "Paid" else 0

		running_balances[doctor] += debit - credit

		ledger.append(
			{
				"date": entry.date,
				"doctor": doctor,
				"service_type": entry.service_type,
				"service_reference": entry.service_reference,
				"service_amount": entry.service_amount,
				"commission_percentage": entry.commission_percentage,
				"commission_amount": entry.commission_amount,
				"debit": debit,
				"credit": credit,
				"running_balance": running_balances[doctor],
				"status": entry.status,
				"payment_entry": entry.payment_entry,
			}
		)

	return ledger


def get_summary(data):
	total_debit = sum(flt(row.get("debit")) for row in data)
	total_credit = sum(flt(row.get("credit")) for row in data)
	outstanding = total_debit - total_credit

	return [
		{"label": _("Total Commission"), "value": total_debit, "indicator": "blue"},
		{"label": _("Total Paid"), "value": total_credit, "indicator": "green"},
		{"label": _("Outstanding"), "value": outstanding, "indicator": "orange"},
	]


def get_chart(data):
	if not data:
		return None

	outstanding = {}
	for row in data:
		doctor = row.get("doctor")
		outstanding.setdefault(doctor, 0)
		outstanding[doctor] = row.get("running_balance") or 0

	return {
		"data": {
			"labels": list(outstanding.keys()),
			"datasets": [{"name": _("Outstanding"), "values": list(outstanding.values())}],
		},
		"type": "bar",
		"colors": ["#2490ef"],
	}

