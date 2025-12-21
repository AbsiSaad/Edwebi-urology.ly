import frappe


def execute():
	mapping = {
		"Encounter": "Patient Encounter",
		"Procedure": "Clinical Procedure",
		"Therapy": "Therapy Session",
	}

	for old_value, new_value in mapping.items():
		frappe.db.sql(
			"""UPDATE `tabDoctor Wallet`
			SET service_type = %s
			WHERE service_type = %s""",
			(new_value, old_value),
		)

