# -*- coding: utf-8 -*-
# Copyright (c) 2025, Healthcare and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import cint, flt, getdate
from healthcare.healthcare.scripts.doctor_commission_utils import (
	create_doctor_wallet_entry,
	reverse_doctor_wallet_entry
)


def on_sales_invoice_submit(doc, method):
	"""Create commission entries when Sales Invoice is submitted"""
	try:
		if not doc.patient:
			# Only process healthcare-related invoices
			return
		
		if not doc.items:
			return
		
		frappe.logger().info(f"Processing Sales Invoice {doc.name} for doctor wallet entries")
	except Exception as e:
		frappe.log_error(f"Error in on_sales_invoice_submit: {str(e)}", "Sales Invoice Commission")
		return
	
	# Track if any entries were created
	entries_created = 0
	
	# Map of reference doctypes to service types
	service_type_map = {
		"Patient Encounter": "Patient Encounter",
		"Lab Test": "Lab Test",
		"Clinical Procedure": "Clinical Procedure",
		"Therapy Session": "Therapy Session",
		"Patient Appointment": "Patient Appointment",
		"Service Request": "Service Request",  # Service Request type
	}
	
	# Process each item
	for item in doc.items:
		try:
			# Check if item has practitioner field directly (for items without reference)
			item_practitioner = getattr(item, 'practitioner', None)
			
			if not item.reference_dt or not item.reference_dn:
				# No reference - check if item has practitioner directly
				if item_practitioner:
					# Direct item with practitioner - create entry with "Sales Invoice" service type
					_create_wallet_entry_for_item(
						doc=doc,
						item=item,
						practitioner=item_practitioner,
						service_type="Sales Invoice",
						reference_doc=None
					)
				else:
					# No reference and no practitioner in item - try to get from patient's recent activity
					if doc.patient:
						practitioner = _get_practitioner_from_patient_recent_activity(doc.patient, doc.posting_date)
						if practitioner:
							_create_wallet_entry_for_item(
								doc=doc,
								item=item,
								practitioner=practitioner,
								service_type="Sales Invoice",
								reference_doc=None
							)
				continue
			
			# Get service type
			service_type = service_type_map.get(item.reference_dt)
			if not service_type:
				continue
			
			# Get practitioner from the referenced document or item
			practitioner = None
			
			# First, try to get from item (sometimes set directly)
			if item_practitioner:
				practitioner = item_practitioner
			
			# If not in item, try to get from referenced document
			if not practitioner:
				practitioner = _get_practitioner_from_reference(item.reference_dt, item.reference_dn)
			
			# If still no practitioner, try to get from patient's recent encounter/appointment
			if not practitioner and doc.patient:
				practitioner = _get_practitioner_from_patient_recent_activity(doc.patient, doc.posting_date)
			
			if not practitioner:
				frappe.logger().info(f"No practitioner found for item {item.name} in Sales Invoice {doc.name}")
				# Truncate error message to avoid CharacterLengthExceededError (max 140 chars)
				error_msg = f"No practitioner for item {item.name} (ref: {item.reference_dt} {item.reference_dn}) in SI {doc.name}"
				if len(error_msg) > 140:
					error_msg = error_msg[:137] + "..."
				frappe.log_error(error_msg, "Sales Invoice Commission - No Practitioner")
				continue
			
			# Get reference document for additional context
			reference_doc = None
			valid_reference = True
			try:
				# Validate that the reference document exists
				if not frappe.db.exists(item.reference_dt, item.reference_dn):
					frappe.logger().warning(f"Reference document {item.reference_dt} {item.reference_dn} does not exist for item {item.name} in Sales Invoice {doc.name}")
					valid_reference = False
				else:
					reference_doc = frappe.get_doc(item.reference_dt, item.reference_dn)
			except Exception as e:
				frappe.logger().info(f"Could not load reference doc {item.reference_dt} {item.reference_dn}: {str(e)}")
				valid_reference = False
			
			# Skip if reference document is invalid
			if not valid_reference:
				frappe.logger().info(f"Skipping wallet entry for item {item.name} due to invalid reference {item.reference_dt} {item.reference_dn}")
				continue
			
			# Create wallet entry
			wallet_name = _create_wallet_entry_for_item(
				doc=doc,
				item=item,
				practitioner=practitioner,
				service_type=service_type,
				reference_doc=reference_doc
			)
			if wallet_name:
				entries_created += 1
		except Exception as e:
			# Truncate error message to avoid CharacterLengthExceededError (max 140 chars)
			error_msg = f"Error processing item {item.name} in SI {doc.name}: {str(e)}"
			if len(error_msg) > 140:
				error_msg = error_msg[:137] + "..."
			frappe.log_error(error_msg, "Sales Invoice Commission")
			continue
	
	# Log summary
	if entries_created > 0:
		frappe.logger().info(f"Created {entries_created} Doctor Wallet entry/entries for Sales Invoice {doc.name}")
	else:
		frappe.logger().info(f"No Doctor Wallet entries created for Sales Invoice {doc.name} (check practitioner settings and commission rules)")


def _get_practitioner_from_reference(reference_dt, reference_dn):
	"""Get practitioner from referenced document"""
	try:
		if reference_dt == "Patient Encounter":
			return frappe.db.get_value("Patient Encounter", reference_dn, "practitioner")
		elif reference_dt == "Lab Test":
			return frappe.db.get_value("Lab Test", reference_dn, "practitioner")
		elif reference_dt == "Clinical Procedure":
			return frappe.db.get_value("Clinical Procedure", reference_dn, "practitioner")
		elif reference_dt == "Therapy Session":
			return frappe.db.get_value("Therapy Session", reference_dn, "practitioner")
		elif reference_dt == "Patient Appointment":
			return frappe.db.get_value("Patient Appointment", reference_dn, "practitioner")
		elif reference_dt == "Service Request":
			return frappe.db.get_value("Service Request", reference_dn, "practitioner")
	except:
		pass
	return None


def _get_practitioner_from_patient_recent_activity(patient, posting_date=None):
	"""Get practitioner from patient's recent encounter or appointment"""
	try:
		# Try to get from most recent encounter
		encounter = frappe.db.get_value("Patient Encounter",
			{"patient": patient, "docstatus": 1},
			["name", "practitioner"],
			order_by="encounter_date desc, creation desc",
			as_dict=True
		)
		
		if encounter and encounter.practitioner:
			return encounter.practitioner
		
		# Try to get from most recent appointment
		appointment = frappe.db.get_value("Patient Appointment",
			{"patient": patient, "status": ["in", ["Open", "Scheduled", "Completed"]]},
			["name", "practitioner"],
			order_by="appointment_date desc, creation desc",
			as_dict=True
		)
		
		if appointment and appointment.practitioner:
			return appointment.practitioner
	except:
		pass
	return None


def _create_wallet_entry_for_item(doc, item, practitioner, service_type, reference_doc=None):
	"""Create a wallet entry for a Sales Invoice item"""
	try:
		# Determine the service reference to use
		if item.reference_dt and item.reference_dn:
			# Validate that the reference document exists (Dynamic Link field requires valid document)
			if not frappe.db.exists(item.reference_dt, item.reference_dn):
				# Invalid reference - skip creating wallet entry
				frappe.logger().warning(f"Invalid service_reference {item.reference_dt} {item.reference_dn} for item {item.name} in Sales Invoice {doc.name}. Skipping wallet entry.")
				return None
			service_reference = item.reference_dn
		else:
			# When there's no reference document, service_reference must be a valid document name
			# for the service_type. Since service_type is "Sales Invoice" in this case,
			# use the Sales Invoice name itself (Dynamic Link field validation requires this)
			service_reference = doc.name
		
		# Check if entry already exists for this service reference
		existing_entry = frappe.db.exists(
			"Doctor Wallet",
			{
				"service_type": service_type,
				"service_reference": service_reference,
				"docstatus": ["!=", 2]
			}
		)
		
		# Also check if there's an entry linked to this Sales Invoice
		existing_si_entry = frappe.db.exists(
			"Doctor Wallet",
			{
				"service_type": service_type,
				"sales_invoice": doc.name,
				"service_reference": service_reference,
				"docstatus": ["!=", 2]
			}
		)
		
		if existing_entry or existing_si_entry:
			# Entry already exists, update it to link to this Sales Invoice if not already linked
			entry_name = existing_entry or existing_si_entry
			try:
				wallet = frappe.get_doc("Doctor Wallet", entry_name)
				if not wallet.sales_invoice:
					wallet.sales_invoice = doc.name
					# Update service amount if it's different (in case invoice amount differs)
					item_amount = flt(item.amount or item.rate * (item.qty or 1))
					if item_amount > 0 and wallet.service_amount != item_amount:
						wallet.service_amount = item_amount
						# Recalculate commission with new amount
						wallet.save(ignore_permissions=True)
						frappe.db.commit()
					else:
						wallet.save(ignore_permissions=True)
						frappe.db.commit()
			except:
				pass
			return
		
		# Get service amount from item
		service_amount = flt(item.amount or item.rate * (item.qty or 1))
		
		if not service_amount or service_amount <= 0:
			return
		
		# Get additional context
		patient = doc.patient
		appointment = None
		encounter = None
		reference_item = item.item_code
		
		# Extract context from reference document if available
		if reference_doc:
			if hasattr(reference_doc, 'patient') and reference_doc.patient:
				patient = reference_doc.patient
			if hasattr(reference_doc, 'appointment') and reference_doc.appointment:
				appointment = reference_doc.appointment
			if service_type == "Patient Encounter":
				encounter = reference_doc.name
			elif service_type == "Patient Appointment":
				# For Patient Appointment, set appointment to the reference document name
				appointment = reference_doc.name
			elif service_type == "Service Request":
				# For Service Request, check if order_group is a Patient Encounter
				if hasattr(reference_doc, 'order_group') and reference_doc.order_group:
					if frappe.db.exists("Patient Encounter", reference_doc.order_group):
						encounter = reference_doc.order_group
			elif service_type in ["Lab Test", "Clinical Procedure", "Therapy Session"]:
				if hasattr(reference_doc, 'patient_encounter') and reference_doc.patient_encounter:
					encounter = reference_doc.patient_encounter
		
		# Create wallet entry
		wallet_name = create_doctor_wallet_entry(
			doctor=practitioner,
			service_type=service_type,
			service_reference=service_reference,  # Use service document name or SI-Item
			service_amount=service_amount,
			date=doc.posting_date or getdate(),
			patient=patient,
			appointment=appointment,
			encounter=encounter,
			sales_invoice=doc.name,
			reference_item=reference_item
		)
		
		if wallet_name:
			frappe.logger().info(f"Created Doctor Wallet entry {wallet_name} for practitioner {practitioner} from Sales Invoice {doc.name}")
			return wallet_name
		else:
			# Log why entry wasn't created
			practitioner_doc = frappe.get_doc("Healthcare Practitioner", practitioner)
			auto_enabled = cint(practitioner_doc.get("auto_wallet_entry", 0))
			if not auto_enabled:
				frappe.logger().info(f"Auto wallet entry disabled for practitioner {practitioner}")
			else:
				# Check commission
				from healthcare.healthcare.scripts.doctor_commission_utils import calculate_commission_amount
				service_amount = flt(item.amount or item.rate * (item.qty or 1))
				comm_amount, _, _ = calculate_commission_amount(
					practitioner, service_type, service_amount, item.item_code
				)
				if comm_amount <= 0:
					frappe.logger().info(f"No commission calculated for practitioner {practitioner}, service_type {service_type}, amount {service_amount}")
				else:
					frappe.logger().info(f"Commission calculated but wallet entry not created for unknown reason")
			return None
	except Exception as e:
		# Truncate error message to avoid CharacterLengthExceededError (max 140 chars)
		error_msg = f"Error creating wallet entry for item {item.name} in SI {doc.name}: {str(e)}"
		if len(error_msg) > 140:
			error_msg = error_msg[:137] + "..."
		frappe.log_error(error_msg, "Sales Invoice Commission")


def on_sales_invoice_cancel(doc, method):
	"""Reverse commission entries when Sales Invoice is cancelled"""
	if not doc.patient:
		return
	
	if not doc.items:
		return
	
	# Find and cancel all wallet entries linked to this Sales Invoice
	wallet_entries = frappe.get_all(
		"Doctor Wallet",
		filters={
			"sales_invoice": doc.name,
			"docstatus": ["!=", 2]  # Not cancelled
		},
		fields=["name", "status", "docstatus"]
	)
	
	for wallet_entry in wallet_entries:
		if wallet_entry.status == "Unpaid":
			try:
				wallet = frappe.get_doc("Doctor Wallet", wallet_entry.name)
				
				# Check if wallet entry is submitted (docstatus = 1)
				if wallet.docstatus == 1:
					# Submitted document - can be cancelled
					wallet.cancel()
					frappe.db.commit()
					frappe.logger().info(f"Cancelled Doctor Wallet entry {wallet_entry.name} for Sales Invoice {doc.name}")
				elif wallet.docstatus == 0:
					# Draft document - delete it instead of cancelling
					frappe.delete_doc("Doctor Wallet", wallet_entry.name, ignore_permissions=True, force=True)
					frappe.db.commit()
					frappe.logger().info(f"Deleted draft Doctor Wallet entry {wallet_entry.name} for Sales Invoice {doc.name}")
			except Exception as e:
				# Truncate error message to avoid CharacterLengthExceededError (max 140 chars)
				error_msg = f"Error cancelling wallet {wallet_entry.name} for SI {doc.name}: {str(e)}"
				if len(error_msg) > 140:
					error_msg = error_msg[:137] + "..."
				frappe.log_error(error_msg, "Sales Invoice Commission Cancel")
		else:
			# Already paid, just log a message
			frappe.logger().info(f"Cannot cancel wallet entry {wallet_entry.name} as it is already paid")
			frappe.msgprint(
				frappe._("Cannot cancel wallet entry {0} as it is already paid").format(wallet_entry.name),
				indicator="orange"
			)

