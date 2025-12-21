# Fix Workflow Issue for Patient Appointment

## Problem
When trying to create a Patient Appointment, you get the error:
```
Workflow موعد المريض not found
404 (NOT FOUND)
```

This happens when a workflow is configured for Patient Appointment but the workflow document doesn't exist in the database.

## Solution

### Option 1: Run the fix script via Bench Console (Recommended)

1. Open bench console:
```bash
cd /home/frappe-user/frappe-bench
bench --site <your-site-name> console
```

2. Run the fix script:
```python
from healthcare.healthcare.fix_workflow_issue import fix_workflow_issue
fix_workflow_issue()
```

### Option 2: Run via Bench Execute

```bash
cd /home/frappe-user/frappe-bench
bench --site <your-site-name> execute healthcare.healthcare.fix_workflow_issue.fix_workflow_issue
```

### Option 3: Manual Fix via Bench Console

1. Open bench console:
```bash
cd /home/frappe-user/frappe-bench
bench --site <your-site-name> console
```

2. Run these commands:
```python
import frappe

# Clear workflow cache
frappe.cache().hdel("workflow", "Patient Appointment")

# Check for active workflows
workflow_name = frappe.db.get_value("Workflow", {
    "document_type": "Patient Appointment",
    "is_active": 1
}, "name")

if workflow_name:
    # Check if workflow exists
    if not frappe.db.exists("Workflow", workflow_name):
        # Deactivate non-existent workflow
        frappe.db.set_value("Workflow", workflow_name, "is_active", 0, update_modified=False)
        print(f"Deactivated non-existent workflow: {workflow_name}")
    else:
        print(f"Workflow {workflow_name} exists and is active")

# Also check for workflow with Arabic name
arabic_workflow = frappe.db.get_value("Workflow", {
    "workflow_name": "موعد المريض"
}, "name")

if arabic_workflow:
    if frappe.db.exists("Workflow", arabic_workflow):
        doc_type = frappe.db.get_value("Workflow", arabic_workflow, "document_type")
        if doc_type == "Patient Appointment":
            frappe.db.set_value("Workflow", arabic_workflow, "is_active", 0, update_modified=False)
            print(f"Deactivated workflow: {arabic_workflow}")
    else:
        print(f"Workflow {arabic_workflow} doesn't exist")

# Clear all caches
frappe.clear_cache()
print("Cache cleared. Try creating an appointment now.")
```

### Option 4: Clear Cache via Bench Command

```bash
cd /home/frappe-user/frappe-bench
bench --site <your-site-name> clear-cache
bench --site <your-site-name> clear-website-cache
```

## Verification

After running the fix, try creating a Patient Appointment again. The error should be resolved.

## Prevention

To prevent this issue in the future:
1. Always deactivate workflows before deleting them
2. Use the Workflow Builder UI to manage workflows
3. Clear cache after making workflow changes

