import frappe
from frappe.permissions import add_permission, update_permission_property


ROLE_NAME = "موظف الاستعلامات"


def ensure_role():
    """Create receptionist role if missing."""
    if frappe.db.exists("Role", ROLE_NAME):
        return frappe.get_doc("Role", ROLE_NAME)

    role = frappe.get_doc(
        {
            "doctype": "Role",
            "role_name": ROLE_NAME,
            "desk_access": 1,
            "two_factor_auth": 0,
            "restrict_forms_to_domain": 0,
        }
    )
    role.insert(ignore_permissions=True)
    frappe.db.commit()
    return role


def ensure_permission(doctype: str, perms: dict, permlevel: int = 0):
    """Guarantee that the role has the expected permission flags for a DocType."""
    if not frappe.db.get_value(
        "DocPerm",
        {"parent": doctype, "role": ROLE_NAME, "permlevel": permlevel},
        "name",
    ):
        add_permission(doctype, ROLE_NAME, permlevel=permlevel)

    for key, value in perms.items():
        update_permission_property(
            doctype,
            ROLE_NAME,
            permlevel=permlevel,
            property=key,
            value=value,
        )


def setup_receptionist_role():
    """
    Create/update receptionist role with the curated permission matrix.
    Run via: bench --site <site> execute healthcare.healthcare.api.receptionist_permissions.setup_receptionist_role
    """
    ensure_role()

    writable_doctypes = {
        "Patient": {"read": 1, "write": 1, "create": 1},
        "Patient Appointment": {"read": 1, "write": 1, "create": 1},
        "Contact": {"read": 1, "write": 0, "create": 1},
        "Address": {"read": 1, "write": 0, "create": 1},
    }

    readonly_doctypes = {
        "Practitioner Schedule",
        "Healthcare Practitioner",
        "Medical Department",
        "Healthcare Settings",
    }

    for doctype, flags in writable_doctypes.items():
        ensure_permission(doctype, flags)

    for doctype in readonly_doctypes:
        ensure_permission(doctype, {"read": 1})

    frappe.clear_cache(doctype="Role")
    return {"status": "success", "message": "Receptionist role configured"}


def create_reception_user(full_name: str, email: str):
    """
    Helper to create a user and assign the receptionist role.
    Example:
        bench --site <site> execute healthcare.healthcare.api.receptionist_permissions.create_reception_user --kwargs "{'full_name': 'Ahmed Reception', 'email': 'reception@example.com'}"
    """
    if frappe.db.exists("User", email):
        user = frappe.get_doc("User", email)
    else:
        user = frappe.get_doc(
            {
                "doctype": "User",
                "email": email,
                "first_name": full_name,
                "send_welcome_email": 0,
                "roles": [],
            }
        )
        user.insert(ignore_permissions=True)

    if ROLE_NAME not in [role.role for role in user.roles]:
        user.append("roles", {"role": ROLE_NAME})
        user.save(ignore_permissions=True)

    frappe.db.commit()
    return {"status": "success", "message": f"User {email} ensured with role {ROLE_NAME}"}


