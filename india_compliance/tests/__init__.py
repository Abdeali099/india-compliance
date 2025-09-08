from functools import partial

import frappe
from frappe.desk.page.setup_wizard.setup_wizard import setup_complete

# from frappe.tests.utils import make_test_objects
from frappe.utils import getdate
from frappe.utils.nestedset import get_root_of

# from erpnext.accounts.utils import get_fiscal_year


def before_tests():
    frappe.clear_cache()

    if not frappe.db.a_row_exists("Company"):
        today = getdate()
        year = today.year if today.month > 3 else today.year - 1

        setup_complete(
            {
                "currency": "INR",
                "full_name": "Test User",
                "company_name": "Wind Power LLP",
                "timezone": "Asia/Kolkata",
                "company_abbr": "WP",
                "industry": "Manufacturing",
                "country": "India",
                "fy_start_date": f"{year}-04-01",
                "fy_end_date": f"{year + 1}-03-31",
                "language": "English",
                "company_tagline": "Testing",
                "email": "test@example.com",
                "password": "test",
                "chart_of_accounts": "Standard",
                "company_gstin": "29MUMB22923F1D",
                "default_gst_rate": "18.0",
                "enable_audit_trail": 0,
            }
        )

    set_default_settings_for_tests()

    # For Frappe Verse - 25 demo, replace with:
    from india_compliance.tests.demo_data_generator import create_frappe_verse_demo_data

    create_frappe_verse_demo_data()

    frappe.db.commit()

    frappe.flags.country = "India"
    frappe.flags.skip_test_records = True
    frappe.enqueue = partial(frappe.enqueue, now=True)


def set_default_settings_for_tests():
    # e.g. set "All Customer Groups" as the default Customer Group
    for key in ("Customer Group", "Supplier Group", "Item Group", "Territory"):
        frappe.db.set_default(frappe.scrub(key), get_root_of(key))

    # Allow Negative Stock
    frappe.db.set_single_value("Stock Settings", "allow_negative_stock", 1)

    # Enable Sandbox Mode in GST Settings
    frappe.db.set_single_value("GST Settings", "sandbox_mode", 1)
