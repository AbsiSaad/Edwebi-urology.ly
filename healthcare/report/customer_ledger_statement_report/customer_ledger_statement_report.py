import frappe
from frappe.utils import getdate


def execute(filters=None):
    if not filters or not filters.get("customer"):
        frappe.throw("Please select a Customer")

    customer = filters.get("customer")
    from_date = filters.get("from_date")
    to_date = filters.get("to_date")

    result = frappe.call(
        method="custom_theme.api.erpnext_customer_statement_api.get_customer_statement",
        args={
            "customer": customer,
            "from_date": from_date,
            "to_date": to_date,
        },
    ).get("message")

    if not result:
        return [], []

    html = result["html"]
    data = result["data"]["rows"]

    frappe.msgprint(html)

    columns = [
        {"label": "Date", "fieldname": "posting_date", "fieldtype": "Data", "width": 100},
        {"label": "Voucher Type", "fieldname": "voucher_type", "fieldtype": "Data", "width": 130},
        {"label": "Voucher No", "fieldname": "voucher_no", "fieldtype": "Data", "width": 130},
        {"label": "Account", "fieldname": "account", "fieldtype": "Data", "width": 150},
        {"label": "Against", "fieldname": "against", "fieldtype": "Data", "width": 150},
        {"label": "Debit", "fieldname": "debit", "fieldtype": "Float", "width": 90},
        {"label": "Credit", "fieldname": "credit", "fieldtype": "Float", "width": 90},
        {"label": "Running Balance", "fieldname": "running_balance", "fieldtype": "Float", "width": 140},
    ]

    return columns, data
