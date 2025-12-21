#!/usr/bin/env python3
"""
Script to fix the missing workflow issue for Patient Appointment.
This script will:
1. Clear the workflow cache
2. Check if there's an active workflow for Patient Appointment
3. If workflow doesn't exist, clear any stale references
"""

import frappe


@frappe.whitelist()
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
		try:
			if frappe.db.exists("Workflow", workflow_name):
				frappe.msgprint(f"Active workflow '{workflow_name}' found for {doctype}")
				# Reload cache with correct value
				frappe.cache().hset("workflow", doctype, workflow_name)
			else:
				frappe.msgprint(f"Workflow '{workflow_name}' referenced but doesn't exist. Deactivating...")
				# Try to deactivate - but if it doesn't exist, just clear cache
				try:
					frappe.db.set_value("Workflow", workflow_name, "is_active", 0, update_modified=False)
				except:
					pass
				frappe.cache().hset("workflow", doctype, "")
				frappe.msgprint("Cleared stale workflow reference")
		except Exception as e:
			frappe.msgprint(f"Error checking workflow: {str(e)}")
			frappe.cache().hset("workflow", doctype, "")
	else:
		frappe.msgprint(f"No active workflow found for {doctype} - this is normal")
		frappe.cache().hset("workflow", doctype, "")
	
	# Also check for workflows with Arabic name "موعد المريض"
	arabic_workflow = frappe.db.get_value("Workflow", {
		"workflow_name": "موعد المريض"
	}, "name")
	
	if arabic_workflow:
		frappe.msgprint(f"Found workflow with Arabic name 'موعد المريض'. Checking if it exists...")
		if frappe.db.exists("Workflow", arabic_workflow):
			# Check if it's for Patient Appointment
			doc_type = frappe.db.get_value("Workflow", arabic_workflow, "document_type")
			if doc_type == doctype:
				frappe.msgprint(f"Workflow '{arabic_workflow}' is configured for {doctype}. Deactivating it...")
				frappe.db.set_value("Workflow", arabic_workflow, "is_active", 0, update_modified=False)
				frappe.cache().hset("workflow", doctype, "")
			else:
				frappe.msgprint(f"Workflow '{arabic_workflow}' is for {doc_type}, not {doctype}")
		else:
			frappe.msgprint(f"Workflow '{arabic_workflow}' doesn't exist. Clearing any references...")
			frappe.cache().hset("workflow", doctype, "")
	
	# Clear all caches
	frappe.clear_cache()
	frappe.msgprint("Cleared all caches")
	
	# Also check for any custom fields that might have been created for workflow
	custom_fields = frappe.get_all("Custom Field", {
		"dt": doctype,
		"fieldtype": "Link",
		"options": "Workflow State"
	}, ["name", "fieldname"])
	
	if custom_fields:
		frappe.msgprint(f"Found {len(custom_fields)} workflow state custom field(s)")
		for cf in custom_fields:
			frappe.msgprint(f"  - {cf.fieldname}")
	
	frappe.msgprint("Workflow issue fixed! Try creating an appointment now.")
	return "Success"

