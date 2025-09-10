"""
Demo Data Generator for Frappe Verse - 25 Event
===============================================

This module generates comprehensive demo data for India Compliance App.
All configuration is at the top of the main function for easy customization.

Usage:
    from india_compliance.tests.demo_data_generator import create_frappe_verse_demo_data
    create_frappe_verse_demo_data()
"""

import random
from datetime import timedelta

import frappe
from frappe.tests.utils import make_test_objects
from frappe.utils import add_months, getdate
from erpnext.accounts.utils import get_fiscal_year

from india_compliance.gst_india.constants import INDIAN_STATES, STATE_PINCODE_MAPPING
from india_compliance.gst_india.overrides.company import make_default_tax_templates
from india_compliance.gst_india.setup.__init__ import create_hsn_codes
from india_compliance.gst_india.utils.tests import (
    create_purchase_invoice,
    create_sales_invoice,
)

DEFAULT_COMPANY = "Resilient Tech"

DEFAULT_COMPANY_CONFIG = {
    "abbr": "RT",
    "company_name": DEFAULT_COMPANY,
    "name": DEFAULT_COMPANY,
    "country": "India",
    "default_currency": "INR",
    "domain": "Manufacturing",
    "chart_of_accounts": "Standard",
    "enable_perpetual_inventory": 0,
    "gstin": "24AUTPV8831F1ZZ",
    "gst_category": "Registered Regular",
}

# Companies with different GST categories
COMPANIES_CONFIG = [
    DEFAULT_COMPANY_CONFIG,
    {
        "abbr": "ITS",
        "name": "InnovateTech Solutions Ltd",
        "company_name": "InnovateTech Solutions Ltd",
        "country": "India",
        "default_currency": "INR",
        "domain": "Manufacturing",
        "chart_of_accounts": "Standard",
        "enable_perpetual_inventory": 0,
        "gstin": "24AAQCA8719H1ZC",
        "gst_category": "Registered Composition",
    },
    {
        "abbr": "DME",
        "name": "Digital Matrix Enterprises",
        "company_name": "Digital Matrix Enterprises",
        "gstin": "",
        "country": "India",
        "default_currency": "INR",
        "domain": "Manufacturing",
        "chart_of_accounts": "Standard",
        "enable_perpetual_inventory": 0,
        "gst_category": "Unregistered",
    },
    {
        "abbr": "STI",
        "company_name": "SoftTech Innovations",
        "name": "SoftTech Innovations",
        "country": "India",
        "default_currency": "INR",
        "doctype": "Company",
        "domain": "Manufacturing",
        "chart_of_accounts": "Standard",
        "enable_perpetual_inventory": 0,
        "gstin": "24AAQCA8719H1ZC",
        "gst_category": "Registered Regular",
    },
    {
        "abbr": "CWS",
        "company_name": "Chhayanwala Solutions",
        "name": "Chhayanwala Solutions",
        "country": "India",
        "default_currency": "INR",
        "doctype": "Company",
        "domain": "Manufacturing",
        "chart_of_accounts": "Standard",
        "enable_perpetual_inventory": 0,
        "gst_category": "Unregistered",
    },
    {
        "abbr": "MJC",
        "company_name": "Mark Johnson Corp",
        "name": "Mark Johnson Corp",
        "country": "United States",
        "default_currency": "USD",
        "doctype": "Company",
        "domain": "Manufacturing",
        "chart_of_accounts": "Standard",
        "enable_perpetual_inventory": 0,
    },
]


# Invoice date ranges (in months from today)
PAST_MONTHS = 6
FUTURE_MONTHS = 3

# Number of invoices to generate
SALES_INVOICES_COUNT = 50
PURCHASE_INVOICES_COUNT = 40


def create_frappe_verse_demo_data():
    """
    Single endpoint to create all demo data for Frappe Verse - 25 event.

    CONFIGURATION - Modify these settings as needed:
    """
    # ==== CONFIGURATION SETTINGS ====

    # Clear existing demo data
    print("🧹 Cleaning existing demo data...")
    _clear_demo_data()

    # Create multiple companies with different GST categories
    print("🏭 Creating companies with different GST categories...")
    companies = []
    for company_config in COMPANIES_CONFIG:
        _create_company(**company_config)
        companies.append(company_config["name"])

    print("🏢 Setting default company...")
    _set_default_company(DEFAULT_COMPANY)

    # creating HSN
    print("📚 Creating HSN codes...")
    create_hsn_codes()

    print("📦 Creating 30+ items with valid HSN codes...")
    items = _create_items()

    print("🏪 Creating 20+ suppliers with different GST categories...")
    suppliers = _create_suppliers()

    print("👥 Creating 20+ customers with different GST categories...")
    customers = _create_customers()

    print("📍 Creating addresses for all parties...")
    _create_addresses(customers, suppliers, DEFAULT_COMPANY)

    # Generate invoices for the default company
    print(f"📄 Creating {SALES_INVOICES_COUNT} sales invoices...")
    _create_sales_invoices(
        company=DEFAULT_COMPANY,
        customers=[customer["name"] for customer in customers],
        items=items,
        count=SALES_INVOICES_COUNT,
        past_months=PAST_MONTHS,
        future_months=FUTURE_MONTHS,
    )

    print(f"📄 Creating {PURCHASE_INVOICES_COUNT} purchase invoices...")
    _create_purchase_invoices(
        company=DEFAULT_COMPANY,
        suppliers=suppliers,
        items=items,
        count=PURCHASE_INVOICES_COUNT,
        past_months=PAST_MONTHS,
        future_months=FUTURE_MONTHS,
    )

    # Create GST Invoice Management System demo data
    print("🏛️ Creating GST Invoice Management System demo data...")
    create_gst_invoice_management_demo_data()

    print("✅ Demo data creation completed successfully!")
    print("📊 Summary:")
    print(f"   - Companies: {len(companies)}")
    for i, company in enumerate(companies):
        gst_cat = COMPANIES_CONFIG[i].get("gst_category")
        print(f"     • {company} ({gst_cat})")
    print(f"  - Default Company: {DEFAULT_COMPANY}")
    print(f"   - Items: {len(items)}")
    print(f"   - Customers: {len(customers)}")
    print(f"   - Suppliers: {len(suppliers)}")
    print(f"   - Sales Invoices: {SALES_INVOICES_COUNT}")
    print(f"   - Purchase Invoices: {PURCHASE_INVOICES_COUNT}")
    print("🎉 Ready for Frappe Verse - 25 demo!")


def create_gst_invoice_management_demo_data():
    """
    Create demo data for GST Invoice Management System using Resilient Tech
    """
    import frappe

    from india_compliance.gst_india.doctype.purchase_reconciliation_tool.test_purchase_reconciliation_tool import (
        create_gst_inward_supply,
    )
    from india_compliance.gst_india.utils.tests import create_purchase_invoice

    # Current date is September 10, 2025
    current_period = "092025"
    bill_date = "2025-09-05"
    gen_date = "2025-09-08"

    print(f"📋 Creating GST IMS document for {DEFAULT_COMPANY}...")

    # Create or get existing GST Invoice Management System document
    try:
        if not frappe.db.exists(
            "GST Invoice Management System", {"company": DEFAULT_COMPANY}
        ):
            gst_ims = frappe.get_doc(
                {
                    "doctype": "GST Invoice Management System",
                    "company": DEFAULT_COMPANY,
                    "company_gstin": DEFAULT_COMPANY_CONFIG["gstin"],
                    "return_period": current_period,
                }
            )
            gst_ims.insert(ignore_permissions=True)
            print(f"✅ Created GST IMS document for {DEFAULT_COMPANY}")
        else:
            print(f"✅ GST IMS document already exists for {DEFAULT_COMPANY}")
    except Exception as e:
        print(
            f"⚠️  GST Invoice Management System doctype may not be available: {str(e)}"
        )
        print(
            "   Continuing with GST Inward Supply creation only..."
        )  # Create GST Inward Supply demo records
    print("📄 Creating GST Inward Supply records...")

    inward_supply_data = [
        {
            "bill_no": "RT-GST-25-001",
            "supplier_name": "TechGlobal Components Ltd",
            "supplier_gstin": "09AAACC1206D5ZA",
            "taxable_value": 50000.0,
            "integrated_tax": 9000.0,
            "central_tax": 0.0,
            "state_tax": 0.0,
            "previous_ims_action": "No Action",
            "action": "Pending",
            "items": [{"taxable_value": 50000.0, "rate": 18, "igst": 9000.0}],
            "document_value": 59000.0,
        },
        {
            "bill_no": "RT-GST-25-002",
            "supplier_name": "Smart Electronics Pvt Ltd",
            "supplier_gstin": "27AAACC1206D1ZG",
            "taxable_value": 75000.0,
            "integrated_tax": 0.0,
            "central_tax": 6750.0,
            "state_tax": 6750.0,
            "previous_ims_action": "Rejected",
            "action": "No Action",
            "previous_action": "Pending",
            "items": [
                {"taxable_value": 75000.0, "rate": 18, "cgst": 6750.0, "sgst": 6750.0}
            ],
            "document_value": 88500.0,
        },
        {
            "bill_no": "RT-GST-25-003",
            "supplier_name": "Digital Supplies Co",
            "supplier_gstin": "30AAACC1206D2ZS",
            "taxable_value": 25000.0,
            "integrated_tax": 4500.0,
            "central_tax": 0.0,
            "state_tax": 0.0,
            "previous_ims_action": "Accepted",
            "action": "No Action",
            "previous_action": "Pending",
            "items": [{"taxable_value": 25000.0, "rate": 18, "igst": 4500.0}],
            "document_value": 29500.0,
        },
        {
            "bill_no": "RT-GST-25-004",
            "supplier_name": "Metro Office Products",
            "supplier_gstin": "06AAACC1206D2ZJ",
            "taxable_value": 30000.0,
            "integrated_tax": 5400.0,
            "central_tax": 0.0,
            "state_tax": 0.0,
            "previous_ims_action": "No Action",
            "action": "Pending",
            "items": [{"taxable_value": 30000.0, "rate": 18, "igst": 5400.0}],
            "document_value": 35400.0,
        },
        {
            "bill_no": "RT-GST-25-005",
            "supplier_name": "Universal Stationery Hub",
            "supplier_gstin": "02AAACC1206D1ZS",
            "taxable_value": 15000.0,
            "integrated_tax": 0.0,
            "central_tax": 1350.0,
            "state_tax": 1350.0,
            "previous_ims_action": "No Action",
            "action": "Pending",
            "items": [
                {"taxable_value": 15000.0, "rate": 18, "cgst": 1350.0, "sgst": 1350.0}
            ],
            "document_value": 17700.0,
        },
    ]

    default_args = {
        "company": DEFAULT_COMPANY,
        "company_gstin": DEFAULT_COMPANY_CONFIG["gstin"],
        "bill_date": bill_date,
        "return_period_2b": current_period,
        "gen_date_2b": gen_date,
        "classification": "B2B",
        "doc_type": "Invoice",
        "supply_type": "Regular",
        "place_of_supply": "24-Gujarat",
        "itc_availability": "Yes",
    }

    created_supplies = []
    for supply_data in inward_supply_data:
        try:
            # Check if already exists
            if not frappe.db.exists(
                "GST Inward Supply", {"bill_no": supply_data["bill_no"]}
            ):
                create_gst_inward_supply(**default_args, **supply_data)
                created_supplies.append(supply_data["bill_no"])
                print(f"  ✅ Created inward supply: {supply_data['bill_no']}")
            else:
                print(f"  ℹ️  Inward supply already exists: {supply_data['bill_no']}")
        except Exception as e:
            print(
                f"  ❌ Error creating inward supply {supply_data['bill_no']}: {str(e)}"
            )

    # Create matching Purchase Invoices for some of the inward supplies
    print("📑 Creating matching Purchase Invoices...")

    purchase_invoice_data = [
        {
            "bill_no": "RT-GST-25-001",
            "supplier": "TechGlobal Components Ltd",
            "supplier_gstin": "09AAACC1206D5ZA",
            "items": [
                {
                    "item_code": "LAPTOP_DELL_INSPIRON",
                    "qty": 1,
                    "rate": 50000,
                }
            ],
        },
        {
            "bill_no": "RT-GST-25-003",
            "supplier": "Digital Supplies Co",
            "supplier_gstin": "30AAACC1206D2ZS",
            "items": [
                {
                    "item_code": "A4_COPY_PAPER_500_SHEETS",
                    "qty": 100,
                    "rate": 250,
                }
            ],
        },
        {
            "bill_no": "RT-GST-25-005",
            "supplier": "Universal Stationery Hub",
            "supplier_gstin": "02AAACC1206D1ZS",
            "items": [
                {
                    "item_code": "BALLPOINT_PEN_BLUE",
                    "qty": 1500,
                    "rate": 10,
                }
            ],
        },
    ]

    created_invoices = []
    for invoice_data in purchase_invoice_data:
        try:
            # Check if supplier exists, if not use a test supplier
            if not frappe.db.exists("Supplier", invoice_data["supplier"]):
                invoice_data["supplier"] = "_Test Registered Supplier"
                invoice_data["supplier_gstin"] = "24AABCR6898M1ZN"

            # Check if items exist, if not use test item
            for item in invoice_data["items"]:
                if not frappe.db.exists("Item", item["item_code"]):
                    item["item_code"] = "_Test Trading Goods 1"

            pinv = create_purchase_invoice(
                company=DEFAULT_COMPANY, bill_date=bill_date, **invoice_data
            )
            created_invoices.append(pinv.name)
            print(f"  ✅ Created purchase invoice: {invoice_data['bill_no']}")
        except Exception as e:
            print(
                f"  ❌ Error creating purchase invoice {invoice_data['bill_no']}: {str(e)}"
            )

    print("✅ GST Invoice Management System demo data creation completed!")
    print("📊 GST IMS Demo Summary:")
    print(f"   - GST Inward Supplies: {len(created_supplies)}")
    print(f"   - Matching Purchase Invoices: {len(created_invoices)}")
    print(f"   - Return Period: {current_period}")
    print(f"   - Company: {DEFAULT_COMPANY}")
    print(f"   - Company GSTIN: {DEFAULT_COMPANY_CONFIG['gstin']}")
    print("🎯 Ready for GST Invoice Management System demo!")


def create_standalone_gst_ims_demo():
    """
    Standalone function to create only GST Invoice Management System demo data
    Can be called independently without creating the full demo dataset.

    Usage:
        from india_compliance.tests.demo_data_generator import create_standalone_gst_ims_demo
        create_standalone_gst_ims_demo()
    """
    import frappe

    print("🏛️ Creating standalone GST Invoice Management System demo data...")

    # Ensure Resilient Tech company exists
    if not frappe.db.exists("Company", DEFAULT_COMPANY):
        print(f"⚠️  Company '{DEFAULT_COMPANY}' does not exist. Creating it first...")
        _create_company(**DEFAULT_COMPANY_CONFIG)
        _set_default_company(DEFAULT_COMPANY)

    # Create GST IMS demo data
    create_gst_invoice_management_demo_data()

    print("✅ Standalone GST Invoice Management System demo data created successfully!")


def _clear_demo_data():
    """Remove existing demo data to start fresh"""
    doctypes_to_clear = [
        "Sales Invoice",
        "Purchase Invoice",
        "Item",
        "Customer",
        "Supplier",
        "Address",
        "Company",
        "GST Inward Supply",
        "GST Invoice Management System",
    ]

    for doctype in doctypes_to_clear:
        # Only delete records that look like demo data
        demo_filters = []
        if doctype == "Company":
            demo_filters = [
                ["company_name", "like", "%Electronics%"],
                ["company_name", "like", "%TechnoSpark%"],
            ]
        elif doctype in ["Item"]:
            demo_filters = [
                ["item_name", "like", "%Laptop%"],
                ["item_name", "like", "%Pen%"],
                ["item_name", "like", "%Phone%"],
            ]
        elif doctype == "GST Inward Supply":
            demo_filters = [
                ["bill_no", "like", "RT-GST-%"],
            ]
        elif doctype == "GST Invoice Management System":
            demo_filters = [
                ["company", "=", DEFAULT_COMPANY],
            ]

        if demo_filters:
            for filter_condition in demo_filters:
                try:
                    records = frappe.get_all(
                        doctype, filters=[filter_condition], pluck="name"
                    )
                    for record in records:
                        frappe.delete_doc(
                            doctype, record, force=True, ignore_permissions=True
                        )
                except Exception:
                    pass  # Ignore errors during cleanup


def _create_company(**kwargs):
    """Create demo company with specified GST category"""
    company_name = kwargs.get("company_name")
    if not frappe.db.exists("Company", kwargs.get("company_name")):
        company = frappe.get_doc({"doctype": "Company", **kwargs})
        company.insert(ignore_permissions=True)
        company_name = company.get("name")

    # Create GST accounts and tax templates for the company
    try:
        make_default_tax_templates(company_name)
        print(f"✅ Created GST accounts for {company_name}")
    except Exception as e:
        print(f"⚠️  Error creating GST accounts for {company_name}: {str(e)}")

    # Add to fiscal year
    try:
        fy = get_fiscal_year(getdate(), as_dict=True)
        doc = frappe.get_doc("Fiscal Year", fy.name)
        fy_companies = [row.company for row in doc.companies]

        company_name = kwargs.get("company_name")
        if company_name and company_name not in fy_companies:
            doc.append("companies", {"company": company_name})
            doc.save(ignore_permissions=True)
    except Exception:
        pass


def _create_items():
    """Create 30+ items with valid HSN codes (hardcoded)"""

    # Electronics items with valid 8-digit HSN codes
    electronics_items = [
        ("Smartphone Samsung Galaxy", "85271300", "Nos", 25000),
        ("Laptop Dell Inspiron", "85271900", "Nos", 45000),
        ("Desktop Computer HP", "85272100", "Nos", 35000),
        ("Tablet iPad", "85272900", "Nos", 30000),
        ("Bluetooth Headphones", "85273100", "Nos", 2500),
        ("Wireless Mouse Logitech", "85273200", "Nos", 800),
        ("Keyboard Mechanical", "85273900", "Nos", 1200),
        ("Monitor LED 24 inch", "85279011", "Nos", 12000),
        ("External Hard Drive 1TB", "85279012", "Nos", 3500),
        ("USB Flash Drive 32GB", "85279019", "Nos", 500),
        ("Power Bank 10000mAh", "85279090", "Nos", 1500),
        ("Smartphone Charger", "85279100", "Nos", 300),
        ("Laptop Bag", "85279200", "Nos", 800),
        ("Webcam HD", "85279911", "Nos", 2000),
        ("Printer Inkjet Canon", "85279912", "Nos", 8000),
        ("Scanner Flatbed", "85279919", "Nos", 6000),
        ("Router WiFi", "85279990", "Nos", 2500),
        ("Ethernet Cable 5m", "85281211", "Meter", 200),
        ("Speakers Bluetooth", "85281212", "Nos", 3000),
        ("Smart Watch", "85281213", "Nos", 8000),
    ]

    # Stationery items with valid 8-digit HSN codes
    stationery_items = [
        ("A4 Copy Paper 500 Sheets", "481730", "Set", 250),
        ("Ballpoint Pen Blue", "481840", "Nos", 10),
        ("Ballpoint Pen Black", "481910", "Nos", 10),
        ("Gel Pen Set", "481920", "Set", 50),
        ("Pencil HB", "481950", "Nos", 5),
        ("Eraser White", "482010", "Nos", 8),
        ("Ruler Plastic 30cm", "482090", "Nos", 15),
        ("Stapler Desktop", "482110", "Nos", 120),
        ("Staple Pins Box", "482190", "Box", 25),
        ("Paper Clips Box", "482290", "Box", 30),
        ("Highlighter Yellow", "482370", "Nos", 25),
        ("Marker Permanent Black", "482390", "Nos", 35),
        ("Notebook A4 200 Pages", "490110", "Nos", 80),
        ("Spiral Notebook A5", "490210", "Nos", 45),
        ("File Folder Plastic", "490290", "Nos", 35),
        ("Binder Clips Set", "490300", "Set", 40),
        ("Correction Fluid", "490590", "Nos", 20),
        ("Glue Stick", "490599", "Nos", 18),
        ("Scissors Office", "490700", "Nos", 65),
        ("Calculator Desktop", "490900", "Nos", 450),
    ]

    items = []

    # Create electronics items
    for name, hsn, uom, rate in electronics_items:
        item_code = name.replace(" ", "_").upper()
        item = {
            "doctype": "Item",
            "item_code": item_code,
            "item_name": name,
            "description": name,
            "item_group": "Products",
            "is_stock_item": 1,
            "stock_uom": uom,
            "gst_hsn_code": hsn,
            "valuation_rate": rate,
            "standard_rate": rate,
        }
        items.append(item)

    # Create stationery items
    for name, hsn, uom, rate in stationery_items:
        item_code = name.replace(" ", "_").upper()
        item = {
            "doctype": "Item",
            "item_code": item_code,
            "item_name": name,
            "description": name,
            "item_group": "Products",
            "is_stock_item": 1,
            "stock_uom": uom,
            "gst_hsn_code": hsn,
            "valuation_rate": rate,
            "standard_rate": rate,
        }
        items.append(item)

    # Create items in database
    make_test_objects("Item", items)

    return [item["item_code"] for item in items]


def _create_customers():
    """Create 20+ customers with different GST categories"""
    from erpnext.crm.doctype.prospect.test_prospect import make_prospect

    prospect_name = make_prospect().name

    customer_data = [
        (
            "Rajesh Electronics Store",
            "Registered Regular",
            "24AAACC1206D1ZM",
            "Company",
        ),
        ("Mumbai Tech Solutions", "Registered Regular", "29AAACC1206D2ZB", "Company"),
        (
            "Priya Stationery Mart",
            "Registered Composition",
            "23AAACC1206D2ZN",
            "Individual",
        ),
        ("Delhi Office Supplies", "Registered Regular", "21AAACC1206D2ZR", "Company"),
        ("Bangalore IT Hub", "SEZ", "04AAACC1206D3ZM", "Company"),
        ("Chennai Electronics", "Registered Regular", "33AAACC1206D1ZN", "Company"),
        ("Kolkata Traders", "Registered Composition", "03AAACC1206D1ZQ", "Individual"),
        ("Pune Software Systems", "UIN Holders", "34AAACC1206D1ZL", "Company"),
        (
            "Ahmedabad Business Center",
            "Registered Regular",
            "35AAACC1206D1ZJ",
            "Company",
        ),
        ("Hyderabad Tech Park", "Tax Deductor", "07AAACC1206D1ZI", "Company"),
        (
            "Jaipur Office Depot",
            "Registered Composition",
            "18AAACC1206D1ZF",
            "Individual",
        ),
        ("Lucknow Enterprises", "Unregistered", "", "Individual"),
        ("Kanpur Retail Store", "Unregistered", "", "Individual"),
        ("Indore Business Hub", "Registered Regular", "13AAACC1206D1ZP", "Company"),
        (
            "Bhopal Tech Center",
            "Registered Composition",
            "16AAACC1206D1ZJ",
            "Individual",
        ),
        ("Coimbatore Industries", "Tax Collector", "37AAACC1206D2ZE", "Company"),
        ("Kochi Trading Co", "Registered Regular", "36AAACC1206D2ZG", "Company"),
        ("Nagpur Electronics", "Unregistered", "", "Individual"),
        ("Vadodara Suppliers", "Deemed Export", "08AAACC1206D1ZG", "Company"),
        (
            "Surat Textile Tech",
            "Registered Composition",
            "32AAACC1206D2ZO",
            "Individual",
        ),
        (
            "Visakhapatnam Traders",
            "Input Service Distributor",
            "09AAACC1206D2ZD",
            "Company",
        ),
        ("Guwahati Business", "Unregistered", "", "Individual"),
        ("Chandigarh Office", "Overseas", "", "Company"),
        ("Thiruvananthapuram Tech", "Registered Regular", "05AAACC1206D1ZM", "Company"),
    ]

    customers = []
    for name, gst_category, gstin, customer_type in customer_data:
        customer = {
            "name": name,
            "customer_name": name,
            "customer_type": customer_type,
            "gst_category": gst_category,
            "gender": "Male",  # BUG
            "prospect_name": prospect_name,  # BUG
            "gstin": gstin,
        }
        customers.append(customer)

    make_test_objects("Customer", customers)

    return customers


def _create_suppliers():
    """Create 20+ suppliers with different GST categories"""

    supplier_data = [
        (
            "TechGlobal Components Ltd",
            "Registered Regular",
            "09AAACC1206D5ZA",
            "Company",
            0,
        ),
        (
            "Smart Electronics Pvt Ltd",
            "Registered Regular",
            "27AAACC1206D1ZG",
            "Company",
            0,
        ),
        (
            "Digital Supplies Co",
            "Registered Composition",
            "30AAACC1206D2ZS",
            "Individual",
            0,
        ),
        ("Metro Office Products", "SEZ", "06AAACC1206D2ZJ", "Company", 0),
        (
            "Universal Stationery Hub",
            "Registered Regular",
            "02AAACC1206D1ZS",
            "Company",
            0,
        ),
        ("Prime Electronics India", "UIN Holders", "10AAACC1206D3ZT", "Company", 0),
        (
            "Omega Trading House",
            "Registered Composition",
            "20AAACC1206D1ZU",
            "Individual",
            0,
        ),
        ("Alpha Tech Distributors", "Tax Deductor", "19AAACC1206D2ZC", "Company", 0),
        (
            "Beta Business Solutions",
            "Registered Regular",
            "22AAACC1206D1ZQ",
            "Company",
            0,
        ),
        ("Gamma Office Mart", "Unregistered", "", "Individual", 0),
        ("Delta Electronics Supply", "Tax Collector", "07AAACC1206D2ZH", "Company", 0),
        (
            "Epsilon Stationery",
            "Registered Composition",
            "37AAACI1681G2ZN",
            "Individual",
            0,
        ),
        (
            "Zeta Tech Components",
            "Input Service Distributor",
            "35AAACI1681G1ZS",
            "Company",
            0,
        ),
        ("Eta Business Products", "Unregistered", "", "Individual", 0),
        (
            "Theta Office Supplies",
            "Registered Regular",
            "12AAACI1681G1Z0",
            "Company",
            0,
        ),
        ("Iota Electronics Hub", "Deemed Export", "18AAACI1681G1ZO", "Company", 0),
        (
            "Kappa Trading Solutions",
            "Registered Composition",
            "10AAACI1681G1Z4",
            "Individual",
            0,
        ),
        ("Lambda Tech Supplies", "Registered Regular", "04AAACI1681G1ZX", "Company", 0),
        ("Mu Office Equipment", "Unregistered", "", "Individual", 0),
        ("Nu Electronics Depot", "Overseas", "", "Company", 0),
        ("Xi Business Center", "Registered Regular", "22AAACI1681G1ZZ", "Company", 0),
        (
            "Omicron Stationery Co",
            "Registered Composition",
            "26AAACI1681G1ZR",
            "Individual",
            0,
        ),
        ("Pi Tech Solutions", "Registered Regular", "07AAACI1681G1ZR", "Company", 0),
        ("Rho Office Products", "Unregistered", "", "Individual", 0),
        (
            "The Transporters Pvt Ltd",
            "Registered Regular",
            "29AABCF6516A1ZZ",
            "Company",
            1,
        ),
    ]

    suppliers = []
    for name, gst_category, gstin, supplier_type, is_transporter in supplier_data:
        supplier = {
            "name": name,
            "supplier_name": name,
            "supplier_type": supplier_type,
            "gst_category": gst_category,
            "gstin": gstin,
            "is_transporter": is_transporter,
        }
        suppliers.append(supplier)

    make_test_objects("Supplier", suppliers)

    return suppliers


def _create_addresses(customers, suppliers, company):
    """Create addresses for all customers, suppliers, and company"""

    addresses = []

    # Company address
    addresses.append(
        {
            "doctype": "Address",
            "address_type": "Billing",
            "address_line1": "Tech Park, Bandra Kurla Complex",
            "city": "Vadodara",
            "state": "Gujarat",
            "pincode": "390023",
            "country": "India",
            "gstin": "24AUTPV8831F1ZZ",
            "gst_category": "Registered Regular",
            "is_primary_address": 1,
            "is_shipping_address": 1,
            "is_your_company_address": 1,
            "links": [{"link_doctype": "Company", "link_name": company}],
        }
    )
    india_state_map = {v: k for k, v in INDIAN_STATES.items()}

    def get_state_from_gstin(gstin):
        """Get state from GSTIN, with fallback to Gujarat if invalid"""
        if not gstin or len(gstin) < 2:
            return "Gujarat"

        state_code = gstin[:2]
        if state_code in india_state_map:
            return india_state_map[state_code]
        else:
            # If invalid state code, default to Gujarat
            return "Gujarat"

    # Customer addresses
    for i, customer in enumerate(customers):
        state = get_state_from_gstin(customer.get("gstin", ""))

        pincode = pincode_generator(state)
        addresses.append(
            {
                "doctype": "Address",
                "address_type": "Billing",
                "address_line1": f"Plot {i + 1}, Sector {i % 10 + 1}",
                "city": f"City {i + 1}",
                "state": state,
                "pincode": pincode,
                "gstin": customer.get("gstin", ""),
                "country": "India",
                "is_primary_address": 1,
                "is_shipping_address": 1,
                "links": [
                    {"link_doctype": "Customer", "link_name": customer.get("name")}
                ],
            }
        )

    # Supplier addresses
    for i, supplier in enumerate(suppliers):
        state = get_state_from_gstin(supplier.get("gstin", ""))
        pincode = pincode_generator(state)
        addresses.append(
            {
                "doctype": "Address",
                "address_type": "Billing",
                "address_line1": f"Industrial Area {i + 1}, Zone {i % 5 + 1}",
                "city": f"Industrial City {i + 1}",
                "state": state,
                "pincode": pincode,
                "gstin": supplier.get("gstin", ""),
                "country": "India",
                "is_primary_address": 1,
                "is_shipping_address": 1,
                "links": [
                    {"link_doctype": "Supplier", "link_name": supplier.get("name")}
                ],
            }
        )

    make_test_objects("Address", addresses)

    return addresses


def pincode_generator(state):
    """Generate a random pincode for a given state"""
    import random

    if state in STATE_PINCODE_MAPPING:
        pincode_range = STATE_PINCODE_MAPPING[state]
        if isinstance(pincode_range[0], tuple):
            pincode_range = pincode_range[0]

        return str(pincode_range[0]) + str(random.randint(0, 999)).zfill(3)

    return "110001"  # Default to Delhi if state not found


def _create_sales_invoices(
    company, customers, items, count, past_months, future_months
):
    """Create sales invoices with random data"""

    today = getdate()
    start_date = add_months(today, -past_months)
    end_date = add_months(today, future_months)

    for i in range(count):
        # Random date between start and end
        days_diff = (end_date - start_date).days
        random_days = random.randint(0, days_diff)
        invoice_date = start_date + timedelta(days=random_days)

        # Random customer and items
        customer = random.choice(customers)
        invoice_items = random.sample(items, random.randint(1, 4))

        # Create invoice
        try:
            invoice_data = {
                "company": company,
                "customer": customer,
                "posting_date": invoice_date,
                "items": [],
            }

            for item_code in invoice_items:
                # Get item details
                item_doc = frappe.get_doc("Item", item_code)
                base_rate = item_doc.standard_rate or item_doc.valuation_rate or 100

                # Add some variation to rate
                rate = base_rate * random.uniform(0.9, 1.1)
                qty = random.randint(1, 5)

                invoice_data["items"].append(
                    {"item_code": item_code, "qty": qty, "rate": rate}
                )

            # Determine tax type based on customer and company states
            customer_state = _get_party_state(customer, "Customer")
            company_state = _get_party_state(company, "Company")

            if customer_state == company_state:
                invoice_data["is_in_state"] = True
            else:
                invoice_data["is_out_state"] = True

            create_sales_invoice(**invoice_data)

        except Exception as e:
            print(f"Error creating sales invoice {i + 1}: {str(e)}")
            continue


def _create_purchase_invoices(
    company, suppliers, items, count, past_months, future_months
):
    """Create purchase invoices with random data"""

    today = getdate()
    start_date = add_months(today, -past_months)
    end_date = add_months(today, future_months)

    for i in range(count):
        # Random date between start and end
        days_diff = (end_date - start_date).days
        random_days = random.randint(0, days_diff)
        invoice_date = start_date + timedelta(days=random_days)

        # Random supplier and items
        supplier = random.choice(suppliers)
        invoice_items = random.sample(items, random.randint(1, 3))

        # Create invoice
        try:
            invoice_data = {
                "company": company,
                "supplier": supplier.get("name"),
                "posting_date": invoice_date,
                "items": [],
            }

            for item_code in invoice_items:
                # Get item details
                item_doc = frappe.get_doc("Item", item_code)
                base_rate = item_doc.valuation_rate or 100

                # Add some variation to rate (purchase usually lower than sales)
                rate = base_rate * random.uniform(0.7, 0.9)
                qty = random.randint(1, 10)

                invoice_data["items"].append(
                    {"item_code": item_code, "qty": qty, "rate": rate}
                )

            # Determine tax type based on supplier and company states
            supplier_state = _get_party_state(supplier.get("name"), "Supplier")
            company_state = _get_party_state(company, "Company")

            if supplier.get("gst_category") not in ("Unregistered", "Overseas", ""):
                if supplier_state == company_state:
                    invoice_data["is_in_state"] = True
                else:
                    invoice_data["is_out_state"] = True

            create_purchase_invoice(**invoice_data)

        except Exception as e:
            print(f"Error creating purchase invoice {i + 1}: {str(e)}")
            continue


def _get_party_state(party_name, party_type):
    """Get state of a customer, supplier, or company"""
    try:
        address = frappe.get_all(
            "Address",
            filters=[
                ["Dynamic Link", "link_doctype", "=", party_type],
                ["Dynamic Link", "link_name", "=", party_name],
            ],
            fields=["state"],
            limit=1,
        )
        return address[0].state if address else "Maharashtra"
    except Exception:
        return "Maharashtra"


def _set_default_company(company):
    """Set the created company as default"""
    from erpnext.setup.doctype.company.company import get_name_with_abbr

    try:
        # stock settings
        frappe.db.set_value(
            "Company",
            company,
            {
                "enable_perpetual_inventory": 1,
                "default_inventory_account": get_name_with_abbr(
                    "Stock In Hand", company
                ),
                "stock_adjustment_account": get_name_with_abbr(
                    "Stock Adjustment", company
                ),
                "stock_received_but_not_billed": get_name_with_abbr(
                    "Stock Received But Not Billed", company
                ),
                "expenses_included_in_valuation": get_name_with_abbr(
                    "Expenses Included In Valuation", company
                ),
            },
        )
        # Set default company
        global_defaults = frappe.get_single("Global Defaults")
        global_defaults.default_company = company
        global_defaults.save(ignore_permissions=True)

    except Exception as e:
        print(f"Warning: Could not set defaults Company: {str(e)}")


if __name__ == "__main__":
    # For testing the module directly
    create_frappe_verse_demo_data()
