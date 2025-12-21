#!/usr/bin/env python3
"""
Script to fix the missing workflow issue for Patient Appointment.
This script will:
1. Clear the workflow cache
2. Check if there's an active workflow for Patient Appointment
3. If workflow doesn't exist, clear any stale references
"""

import frappe

def fix_workflow_issue():
	"""Fix the missing workflow issue for Patient Appointment doctype"""
	
	doctype = "Patient Appointment"
	
	# Clear workflow cache
	frappe.cache().hdel("workflow", doctype)
	
	# Check if there's an active workflow
	workflow_name = frappe.db.get_value("Workflow", {
		"document_type": doctype,
		"is_active": 1
	}, "name")
	
	if workflow_name:
		# Check if the workflow document actually exists
		if frappe.db.exists("Workflow", workflow_name):
			print(f"✓ Active workflow '{workflow_name}' found for {doctype}")
			# Reload cache with correct value
			frappe.cache().hset("workflow", doctype, workflow_name)
		else:
			print(f"✗ Workflow '{workflow_name}' referenced but doesn't exist. Clearing reference...")
			# Deactivate or delete the workflow reference
			frappe.db.set_value("Workflow", workflow_name, "is_active", 0, update_modified=False)
			frappe.cache().hset("workflow", doctype, "")
			print(f"✓ Cleared stale workflow reference")
	else:
		print(f"✓ No active workflow found for {doctype} - this is normal")
		frappe.cache().hset("workflow", doctype, "")
	
	# Clear all caches
	frappe.clear_cache()
	print("✓ Cleared all caches")
	
	# Also check for any custom fields that might have been created for workflow
	custom_fields = frappe.get_all("Custom Field", {
		"dt": doctype,
		"fieldtype": "Link",
		"options": "Workflow State"
	}, ["name", "fieldname"])
	
	if custom_fields:
		print(f"✓ Found {len(custom_fields)} workflow state custom field(s)")
		for cf in custom_fields:
			print(f"  - {cf.fieldname}")
	
	print("\n✓ Workflow issue fixed! Try creating an appointment now.")

if __name__ == "__main__":
	# This script should be run via bench console
	print("This script should be run via bench console:")
	print("bench --site <your-site> console")
	print("Then run: exec(open('fix_workflow_issue.py').read())")
	print("\nOr run directly:")
	print("bench --site <your-site> execute healthcare.fix_workflow_issue.fix_workflow_issue")

