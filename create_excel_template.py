#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create Excel template for Healthcare Master Data Input
"""

try:
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    from openpyxl.utils import get_column_letter
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False
    print("openpyxl not installed. Creating CSV files instead.")

def create_excel_template():
    """Create Excel template with multiple sheets"""
    
    if not HAS_OPENPYXL:
        print("Creating CSV files instead of Excel...")
        return
    
    wb = Workbook()
    
    # Remove default sheet
    if 'Sheet' in wb.sheetnames:
        wb.remove(wb['Sheet'])
    
    # Define header style
    header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=11)
    required_fill = PatternFill(start_color="FFE699", end_color="FFE699", fill_type="solid")
    
    # Sheet 1: Medical Department
    ws1 = wb.create_sheet("Medical Department")
    ws1.append(["Department Name*", "Patient Care Type", "Notes"])
    ws1.append(["Cardiology", "Outpatient", "Example - Required field marked with *"])
    ws1.append(["Orthopedics", "Outpatient", ""])
    ws1.append(["Pediatrics", "Outpatient", ""])
    ws1.append(["General Medicine", "Outpatient", ""])
    ws1.append(["Surgery", "Outpatient", ""])
    format_sheet(ws1, header_fill, header_font, required_fill)
    
    # Sheet 2: Healthcare Practitioner
    ws2 = wb.create_sheet("Healthcare Practitioner")
    ws2.append(["Practitioner Name*", "Practitioner Type*", "Medical Department*", "Designation", 
                "Mobile No", "Email ID", "OP Consulting Charge", "Inpatient Visit Charge", "Notes"])
    ws2.append(["Dr. Ahmed Ali", "Internal", "Cardiology", "Consultant", 
                "0123456789", "ahmed@hospital.com", "100", "200", "Example"])
    format_sheet(ws2, header_fill, header_font, required_fill)
    
    # Sheet 3: Appointment Type
    ws3 = wb.create_sheet("Appointment Type")
    ws3.append(["Appointment Type*", "Default Duration (Minutes)*", "Allow Booking For*", 
                "Color", "Price List", "Notes"])
    ws3.append(["General Consultation", "30", "Practitioner", "#4285F4", "Standard Selling", "Example"])
    ws3.append(["Follow-up", "15", "Practitioner", "#34A853", "Standard Selling", ""])
    ws3.append(["Emergency", "60", "Practitioner", "#EA4335", "Standard Selling", ""])
    format_sheet(ws3, header_fill, header_font, required_fill)
    
    # Sheet 4: Healthcare Service Unit Type
    ws4 = wb.create_sheet("Service Unit Type")
    ws4.append(["Service Unit Type*", "Allow Appointments", "Overlap Appointments", 
                "Service Unit Capacity", "Is Billable", "Item Code", "Rate", "Notes"])
    ws4.append(["OPD Room", "Yes", "No", "1", "Yes", "OPD-ROOM-001", "50", "Example"])
    ws4.append(["Ward", "No", "No", "10", "Yes", "WARD-001", "100", ""])
    ws4.append(["ICU", "No", "No", "5", "Yes", "ICU-001", "500", ""])
    format_sheet(ws4, header_fill, header_font, required_fill)
    
    # Sheet 5: Healthcare Service Unit
    ws5 = wb.create_sheet("Service Unit")
    ws5.append(["Service Unit*", "Service Unit Type*", "Company*", "Is Group", 
                "Allow Appointments", "Overlap Appointments", "Warehouse", "Parent Service Unit", "Notes"])
    ws5.append(["OPD Room 1", "OPD Room", "Your Company", "No", "Yes", "No", "Stores - YC", "", "Example"])
    ws5.append(["OPD Room 2", "OPD Room", "Your Company", "No", "Yes", "No", "Stores - YC", "", ""])
    ws5.append(["Ward A", "Ward", "Your Company", "No", "No", "No", "Stores - YC", "", ""])
    format_sheet(ws5, header_fill, header_font, required_fill)
    
    # Sheet 6: Practitioner Schedule
    ws6 = wb.create_sheet("Practitioner Schedule")
    ws6.append(["Schedule Name*", "Practitioner*", "Day*", "From Time*", 
                "To Time*", "Allow Video Conferencing", "Notes"])
    ws6.append(["Dr. Ahmed - Weekdays", "Dr. Ahmed Ali", "Sunday", "09:00:00", 
                "17:00:00", "Yes", "Example - Time format: HH:MM:SS"])
    ws6.append(["Dr. Ahmed - Weekdays", "Dr. Ahmed Ali", "Monday", "09:00:00", "17:00:00", "Yes", ""])
    format_sheet(ws6, header_fill, header_font, required_fill)
    
    # Sheet 7: Lab Test Template
    ws7 = wb.create_sheet("Lab Test Template")
    ws7.append(["Lab Test Name*", "Lab Test Group", "Department*", "Sample*", 
                "Sample UOM", "Test Type", "Is Billable", "Item Code", "Notes"])
    ws7.append(["Complete Blood Count (CBC)", "Hematology", "Pathology", "Blood", 
                "mL", "Single", "Yes", "CBC-001", "Example"])
    ws7.append(["Blood Glucose", "Biochemistry", "Pathology", "Blood", "mL", "Single", "Yes", "GLU-001", ""])
    format_sheet(ws7, header_fill, header_font, required_fill)
    
    # Sheet 8: Medication
    ws8 = wb.create_sheet("Medication")
    ws8.append(["Generic Name*", "Medication Class*", "Strength*", "Strength UOM*", 
                "Dosage Form*", "Is Combination", "Item Code", "Default Prescription Dosage", "Notes"])
    ws8.append(["Paracetamol", "Analgesics", "500", "mg", "Tablet", "No", "PARA-500", "1-1-1", "Example"])
    ws8.append(["Amoxicillin", "Antibiotics", "500", "mg", "Capsule", "No", "AMOX-500", "1-1-1", ""])
    format_sheet(ws8, header_fill, header_font, required_fill)
    
    # Sheet 9: Clinical Procedure Template
    ws9 = wb.create_sheet("Clinical Procedure")
    ws9.append(["Procedure Template*", "Medical Department*", "Item Code", "Is Billable", 
                "Consume Stock", "Warehouse", "Estimated Duration (Minutes)", "Description", "Notes"])
    ws9.append(["X-Ray Chest", "Radiology", "XRAY-CHEST", "Yes", "No", "", "15", "Chest X-Ray", "Example"])
    ws9.append(["ECG", "Cardiology", "ECG-001", "Yes", "No", "", "10", "Electrocardiogram", ""])
    format_sheet(ws9, header_fill, header_font, required_fill)
    
    # Sheet 10: Diagnosis
    ws10 = wb.create_sheet("Diagnosis")
    ws10.append(["Diagnosis*", "Medical Coding", "Notes"])
    ws10.append(["Hypertension", "", "Example"])
    ws10.append(["Diabetes Mellitus Type 2", "", ""])
    ws10.append(["Upper Respiratory Tract Infection", "", ""])
    format_sheet(ws10, header_fill, header_font, required_fill)
    
    # Sheet 11: Complaint
    ws11 = wb.create_sheet("Complaint")
    ws11.append(["Complaint*", "Notes"])
    ws11.append(["Fever", "Example"])
    ws11.append(["Headache", ""])
    ws11.append(["Cough", ""])
    ws11.append(["Chest Pain", ""])
    format_sheet(ws11, header_fill, header_font, required_fill)
    
    # Save file
    filename = "healthcare_master_data_template.xlsx"
    wb.save(filename)
    print(f"Excel file created: {filename}")
    return filename

def format_sheet(ws, header_fill, header_font, required_fill):
    """Format worksheet with styles"""
    # Format header row
    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        if "*" in str(cell.value):
            cell.fill = required_fill
    
    # Auto-adjust column widths
    for column in ws.columns:
        max_length = 0
        column_letter = get_column_letter(column[0].column)
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = min(max_length + 2, 50)
        ws.column_dimensions[column_letter].width = adjusted_width
    
    # Freeze first row
    ws.freeze_panes = "A2"

if __name__ == "__main__":
    if HAS_OPENPYXL:
        create_excel_template()
    else:
        print("Please install openpyxl: pip install openpyxl")
        print("Or use the CSV file: healthcare_master_data_template.csv")

