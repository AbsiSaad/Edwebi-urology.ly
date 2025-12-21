import frappe


def get_context(context):
	context.no_cache = 1
	context.show_sidebar = False
	context.practitioners = frappe.get_all(
		"Healthcare Practitioner",
		filters={"status": "Active"},
		fields=["name", "practitioner_name"],
		order_by="practitioner_name asc",
	)
	context.gender_options = ["Male", "Female", "Other"]
