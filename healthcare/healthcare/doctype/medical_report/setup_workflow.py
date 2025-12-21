# -*- coding: utf-8 -*-
"""
Setup Workflow for Medical Report
Run this script to create the workflow states, actions, and workflow
"""

import frappe


def setup_medical_report_workflow():
	"""Create workflow states, actions, and workflow for Medical Report"""
	
	# Create Workflow States
	states = [
		{"name": "Draft", "style": "Secondary"},
		{"name": "Waiting for Doctor Approval", "style": "Warning"},
		{"name": "Approved", "style": "Success"},
		{"name": "Rejected", "style": "Danger"}
	]
	
	for state in states:
		if not frappe.db.exists("Workflow State", state["name"]):
			frappe.get_doc({
				"doctype": "Workflow State",
				"workflow_state_name": state["name"],
				"style": state["style"]
			}).insert(ignore_permissions=True)
	
	# Create Workflow Actions
	actions = [
		{"name": "Request Approval", "action_type": "Action"},
		{"name": "Approve", "action_type": "Action"},
		{"name": "Reject", "action_type": "Action"}
	]
	
	for action in actions:
		if not frappe.db.exists("Workflow Action Master", action["name"]):
			frappe.get_doc({
				"doctype": "Workflow Action Master",
				"workflow_action_name": action["name"]
			}).insert(ignore_permissions=True)
	
	# Create Workflow
	workflow_name = "Medical Report Workflow"
	
	if frappe.db.exists("Workflow", workflow_name):
		frappe.delete_doc("Workflow", workflow_name, force=1)
	
	workflow = frappe.get_doc({
		"doctype": "Workflow",
		"workflow_name": workflow_name,
		"document_type": "Medical Report",
		"workflow_state_field": "workflow_state",
		"is_active": 1,
		"override_status": 0,
		"send_email_alert": 0,
		"states": [
			{
				"state": "Draft",
				"doc_status": "0",
				"update_field": "status",
				"update_value": "Draft",
				"allow_edit": "Healthcare Administrator"
			},
			{
				"state": "Waiting for Doctor Approval",
				"doc_status": "0",
				"update_field": "status",
				"update_value": "Waiting for Doctor Approval",
				"allow_edit": "Physician"
			},
			{
				"state": "Approved",
				"doc_status": "0",
				"update_field": "status",
				"update_value": "Approved",
				"allow_edit": "Physician"
			},
			{
				"state": "Rejected",
				"doc_status": "0",
				"update_field": "status",
				"update_value": "Rejected",
				"allow_edit": "Physician"
			}
		],
		"transitions": [
			{
				"state": "Draft",
				"action": "Request Approval",
				"next_state": "Waiting for Doctor Approval",
				"allowed": "Healthcare Administrator",
				"allow_self_approval": 0
			},
			{
				"state": "Waiting for Doctor Approval",
				"action": "Approve",
				"next_state": "Approved",
				"allowed": "Physician",
				"allow_self_approval": 1
			},
			{
				"state": "Waiting for Doctor Approval",
				"action": "Reject",
				"next_state": "Rejected",
				"allowed": "Physician",
				"allow_self_approval": 1
			}
		]
	})
	
	workflow.insert(ignore_permissions=True)
	frappe.db.commit()
	
	print(f"Workflow '{workflow_name}' created successfully!")


if __name__ == "__main__":
	setup_medical_report_workflow()


