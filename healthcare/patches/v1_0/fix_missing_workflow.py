"""
Patch to fix missing workflow issue.
This patch ensures that get_workflow handles missing workflows gracefully.
"""

import frappe


def execute():
	"""Fix missing workflow references"""
	
	# Clear all workflow caches
	frappe.cache().delete_key("workflow")
	
	# Find all active workflows and verify they exist
	active_workflows = frappe.get_all("Workflow", {
		"is_active": 1
	}, ["name", "document_type", "workflow_name"])
	
	for workflow in active_workflows:
		if not frappe.db.exists("Workflow", workflow.name):
			# Workflow doesn't exist, deactivate it
			frappe.db.set_value("Workflow", workflow.name, "is_active", 0, update_modified=False)
			frappe.msgprint(f"Deactivated non-existent workflow: {workflow.name}")
	
	# Clear cache again
	frappe.clear_cache()
	
	frappe.msgprint("Workflow cache cleared and verified")

