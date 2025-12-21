import frappe
from frappe.utils.pdf import get_pdf


@frappe.whitelist()
def download_pdf(customer, from_date, to_date):
    data = frappe.get_attr(
        'custom_theme.api.erpnext_customer_statement_api.get_customer_statement'
    )(customer, from_date, to_date)
    pdf = get_pdf(data['html'])
    file_name = f"Customer-Ledger-{frappe.utils.now_datetime().strftime('%Y%m%d%H%M')}.pdf"
    file_doc = frappe.get_doc({
        'doctype': 'File',
        'file_name': file_name + '.pdf',
        'is_private': 1,
        'content': pdf,
    })
    file_doc.save(ignore_permissions=True)
    return file_doc.file_url
