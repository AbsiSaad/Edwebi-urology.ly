# -*- coding: utf-8 -*-
# Copyright (c) 2025, Healthcare and contributors
# For license information, please see license.txt

import frappe

def on_patient_encounter_submit(doc, method):
	"""Doctor wallet entries are disabled for patient encounters."""
	frappe.logger("healthcare").info(
		"Skipping doctor wallet creation for Patient Encounter %s", doc.name
	)


def on_patient_encounter_cancel(doc, method):
	"""Doctor wallet entries were disabled; nothing to reverse."""
	frappe.logger("healthcare").info(
		"Skipping doctor wallet reversal for Patient Encounter %s", doc.name
	)
