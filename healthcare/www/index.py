import frappe
from frappe import _

no_cache = 1


def get_context(context):
	"""Get context for homepage"""
	context.title = _("Home") + " - " + _("Healthcare")
	context.no_cache = 1
	return context

