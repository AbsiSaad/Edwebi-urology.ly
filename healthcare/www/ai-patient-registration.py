"""
Web Page Renderer for AI Patient Registration
"""
import frappe

no_cache = 1

def get_context(context):
	"""Add context for AI Patient Registration page"""
	context.no_cache = 1
	context.title = "تسجيل المريض - الذكاء الاصطناعي"
	
	# Set ERPNext config values
	try:
		context.site_name = frappe.form_dict.get('site', '') if hasattr(frappe, 'form_dict') and frappe.form_dict else ''
		if not context.site_name and hasattr(frappe, 'boot') and frappe.boot:
			context.site_name = getattr(frappe.boot, 'sitename', '')
	except:
		context.site_name = ''
	
	try:
		context.csrf_token = frappe.session.csrf_token if hasattr(frappe, 'session') and frappe.session else ''
	except:
		context.csrf_token = ''
	
	try:
		context.ai_backend_url = frappe.conf.get('ai_backend_url', 'http://102.213.183.187:8001')
	except:
		context.ai_backend_url = 'http://102.213.183.187:8001'
	
	return context
