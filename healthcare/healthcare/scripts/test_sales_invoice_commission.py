# -*- coding: utf-8 -*-
# Test script for Sales Invoice Commission

import frappe

def test_sales_invoice_commission():
	"""Test the sales invoice commission functionality"""
	
	# Find a Sales Invoice with patient
	si_list = frappe.get_all("Sales Invoice", 
		filters={"patient": ["!=", ""], "docstatus": 1},
		fields=["name", "patient"],
		limit=1
	)
	
	if not si_list:
		print("No Sales Invoices with patients found")
		return
	
	si_name = si_list[0].name
	print(f"Testing with Sales Invoice: {si_name}")
	
	# Get the Sales Invoice doc
	si_doc = frappe.get_doc("Sales Invoice", si_name)
	print(f"Patient: {si_doc.patient}")
	print(f"Items count: {len(si_doc.items)}")
	
	# Check patient's recent encounters
	encounters = frappe.get_all("Patient Encounter",
		{"patient": si_doc.patient, "docstatus": 1},
		["name", "practitioner", "encounter_date"],
		order_by="encounter_date desc",
		limit=3
	)
	print(f"\nPatient's recent encounters: {len(encounters)}")
	for enc in encounters:
		print(f"  - {enc.name}: Practitioner={enc.practitioner}, Date={enc.encounter_date}")
	
	# Check if practitioners have auto_wallet_entry enabled
	if encounters:
		practitioners = [enc.practitioner for enc in encounters if enc.practitioner]
		for practitioner in practitioners:
			auto_entry = frappe.db.get_value("Healthcare Practitioner", practitioner, "auto_wallet_entry")
			commission = frappe.db.get_value("Healthcare Practitioner", practitioner, "default_commission_percentage")
			print(f"\nPractitioner {practitioner}:")
			print(f"  - auto_wallet_entry: {auto_entry}")
			print(f"  - default_commission_percentage: {commission}")
	
	# Check items
	for idx, item in enumerate(si_doc.items[:5], 1):  # First 5 items
		print(f"\nItem {idx}:")
		print(f"  - Item Code: {item.item_code}")
		print(f"  - Reference DT: {item.reference_dt}")
		print(f"  - Reference DN: {item.reference_dn}")
		print(f"  - Amount: {item.amount}")
		if hasattr(item, 'practitioner'):
			print(f"  - Practitioner: {item.practitioner}")
	
	# Test the function
	try:
		from healthcare.healthcare.scripts.sales_invoice_commission import on_sales_invoice_submit, _get_practitioner_from_patient_recent_activity
		print("\n✓ Function imported successfully")
		
		# Test getting practitioner from patient
		if si_doc.patient:
			practitioner = _get_practitioner_from_patient_recent_activity(si_doc.patient, si_doc.posting_date)
			print(f"\nPractitioner from patient recent activity: {practitioner}")
		
		print("Testing on_sales_invoice_submit...")
		
		# Call the function
		on_sales_invoice_submit(si_doc, "on_submit")
		
		print("✓ Function executed successfully")
		
		# Check if wallet entries were created
		wallet_entries = frappe.get_all("Doctor Wallet",
			filters={"sales_invoice": si_name},
			fields=["name", "doctor", "service_type", "service_amount", "commission_amount", "status"]
		)
		
		if wallet_entries:
			print(f"\n✓ Found {len(wallet_entries)} wallet entries:")
			for entry in wallet_entries:
				print(f"  - {entry.name}: Doctor={entry.doctor}, Type={entry.service_type}, Amount={entry.service_amount}, Commission={entry.commission_amount}, Status={entry.status}")
		else:
			print("\n⚠ No wallet entries created")
			print("  Possible reasons:")
			print("  - No practitioner found for items")
			print("  - Practitioner has auto_wallet_entry disabled")
			print("  - Practitioner has no commission percentage configured")
			print("  - Service amount is 0")
			
	except Exception as e:
		import traceback
		print(f"\n✗ Error: {e}")
		traceback.print_exc()

if __name__ == "__main__":
	test_sales_invoice_commission()
