#!/usr/bin/env python3
"""
ConstructFlow ERP — Demo Data Seeder
=====================================
Populates the Odoo database with realistic demo data for a Palembang-based
construction subcontractor business (Bapak Junaidi's company).

Uses Odoo's XML-RPC interface.  Run from the Docker host:
    python3 scripts/seed_demo_data.py

Environment variables (auto-read from .env if present):
    ODOO_HOST          default 127.0.0.1
    ODOO_PORT          default 8069
    ODOO_DB            default constructflow_erp
    ODOO_USER          default admin
    ODOO_PASSWORD      default admin   (the Odoo *login* password, NOT master pwd)
"""

import os
import sys
import random
import xmlrpc.client
from datetime import date, timedelta
from pathlib import Path

# ---------------------------------------------------------------------------
# 0.  Load .env (simple key=value parser)
# ---------------------------------------------------------------------------
_env_path = Path(__file__).resolve().parent.parent / ".env"
if _env_path.exists():
    for line in _env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

ODOO_HOST = os.environ.get("ODOO_HOST", "127.0.0.1")
ODOO_PORT = int(os.environ.get("ODOO_PORT", "8069"))
ODOO_DB = os.environ.get("ODOO_DB") or os.environ.get("ODOO_DB_NAME", "constructflow_erp")
ODOO_USER = os.environ.get("ODOO_USER", "admin")
ODOO_PASSWORD = os.environ.get("ODOO_PASSWORD", "admin")

URL = f"http://{ODOO_HOST}:{ODOO_PORT}"


# ---------------------------------------------------------------------------
# 1.  Connect & authenticate
# ---------------------------------------------------------------------------
def connect():
    common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common", allow_none=True)
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
    if not uid:
        print(
            f"ERROR  Authentication failed.\n"
            f"       URL={URL}  DB={ODOO_DB}  user={ODOO_USER}\n"
            f"       Make sure ODOO_PASSWORD is the *login* password for the '{ODOO_USER}' user,\n"
            f"       NOT the Odoo master password."
        )
        sys.exit(1)
    models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object", allow_none=True)
    print(f"OK  Authenticated as uid={uid} on {URL} / {ODOO_DB}")
    return uid, models


def x(models, uid, model, method, *args, **kw):
    """Shortcut for models.execute_kw."""
    return models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, model, method, *args, **kw)


def find_or_create(models, uid, model, domain, vals):
    """Return existing record id or create a new one."""
    ids = x(models, uid, model, "search", [[domain]], {"limit": 1})
    if ids:
        return ids[0]
    return x(models, uid, model, "create", [vals])


# ---------------------------------------------------------------------------
# 2.  Reference / lookup helpers
# ---------------------------------------------------------------------------
def get_idr_currency(models, uid):
    ids = x(models, uid, "res.currency", "search", [[("name", "=", "IDR")]], {"limit": 1})
    if ids:
        # Make sure it's active
        x(models, uid, "res.currency", "write", [ids, {"active": True}])
        return ids[0]
    # Fallback: company currency
    cids = x(models, uid, "res.company", "search", [[]], {"limit": 1})
    company = x(models, uid, "res.company", "read", [cids, ["currency_id"]])[0]
    return company["currency_id"][0]


def get_or_create_uom(models, uid, name, category_name=None):
    """Look up a UoM by name; return its id."""
    ids = x(models, uid, "uom.uom", "search", [[("name", "=", name)]], {"limit": 1})
    if ids:
        return ids[0]
    # Try common aliases
    alt = {"m³": "m", "m²": "m", "batang": "Units", "lembar": "Units",
           "sak": "Units", "kg": "kg", "liter": "Liter(s)", "unit": "Units"}
    ids = x(models, uid, "uom.uom", "search", [[("name", "ilike", alt.get(name, name))]], {"limit": 1})
    if ids:
        return ids[0]
    # Last resort: return generic "Units"
    ids = x(models, uid, "uom.uom", "search", [[("name", "=", "Units")]], {"limit": 1})
    return ids[0] if ids else False


def get_or_create_product_category(models, uid, name):
    """Find or create a product category."""
    ids = x(models, uid, "product.category", "search", [[("name", "=", name)]], {"limit": 1})
    if ids:
        return ids[0]
    return x(models, uid, "product.category", "create", [{"name": name}])


def get_stock_location(models, uid, usage="internal"):
    """Get the main stock location."""
    domain = [("usage", "=", usage)]
    if usage == "internal":
        domain.append(("company_id", "!=", False))
    ids = x(
        models, uid, "stock.location", "search",
        [domain],
        {"limit": 1},
    )
    return ids[0] if ids else False


# ---------------------------------------------------------------------------
# 3.  Seed data definitions  (realistic Indonesian construction context)
# ---------------------------------------------------------------------------

# --- 3a. Clients (developer companies) ---
CLIENTS = [
    {
        "name": "PT Rid Jaya Bersama",
        "phone": "0711-5551234",
        "email": "info@ridjaya.co.id",
        "street": "Jl. Jend. Sudirman No. 102",
        "city": "Palembang",
        "zip": "30128",
        "comment": "<p>Developer perumahan Dream Land 1 di kawasan Borang.</p>",
        "company_type": "company",
        "is_company": True,
        "customer_rank": 1,
    },
    {
        "name": "PT Ramatrimitra Development",
        "phone": "0711-5559876",
        "email": "project@ramatrimitra.co.id",
        "street": "Jl. Kolonel Atmo No. 45",
        "city": "Palembang",
        "zip": "30135",
        "comment": "<p>Developer utama: Kartika Mataram, The Greenvillage, Taman Asri 2, Siknatur.</p>",
        "company_type": "company",
        "is_company": True,
        "customer_rank": 1,
    },
    {
        "name": "PT Agung Sumatera Development",
        "phone": "0711-5557654",
        "email": "hrd@agungsumatera.co.id",
        "street": "Jl. R. Sukamto No. 88, Komp. Ilir Barat Permai",
        "city": "Palembang",
        "zip": "30152",
        "comment": "<p>Developer kawasan premium: Osaka Residence, Griya Bukit Berlian, Orchard.</p>",
        "company_type": "company",
        "is_company": True,
        "customer_rank": 1,
    },
]

# --- 3b. Suppliers (building material stores) ---
SUPPLIERS = [
    {
        "name": "TB Jaya Makmur",
        "phone": "0711-7712345",
        "street": "Jl. Mayor Zen No. 33, Sei Selincah",
        "city": "Palembang",
        "zip": "30164",
        "comment": "<p>Supplier utama semen, besi, dan bata. Bisa antar ke lokasi proyek.</p>",
        "supplier_rank": 1,
        "is_company": True,
    },
    {
        "name": "UD Sumber Material",
        "phone": "0711-7734567",
        "street": "Jl. Soekarno-Hatta No. 120, Karya Baru",
        "city": "Palembang",
        "zip": "30114",
        "comment": "<p>Toko bahan bangunan lengkap. Harga kompetitif untuk pembelian besar.</p>",
        "supplier_rank": 1,
        "is_company": True,
    },
    {
        "name": "CV Baja Kuat Perkasa",
        "phone": "0711-7756789",
        "street": "Jl. RE Martadinata No. 78",
        "city": "Palembang",
        "zip": "30118",
        "comment": "<p>Spesialis besi beton, wiremesh, dan material struktur baja.</p>",
        "supplier_rank": 1,
        "is_company": True,
    },
    {
        "name": "TB Mitra Pasir Beton",
        "phone": "0711-7798765",
        "street": "Jl. Alamsyah Ratu Prawiranegara KM 8",
        "city": "Palembang",
        "zip": "30163",
        "comment": "<p>Supplier pasir, batu split, beton readymix. Armada truk sendiri.</p>",
        "supplier_rank": 1,
        "is_company": True,
    },
    {
        "name": "Toko Cat Warna Indah",
        "phone": "0711-7711223",
        "street": "Jl. Angkatan 45 No. 56",
        "city": "Palembang",
        "zip": "30121",
        "comment": "<p>Distributor cat Dulux, Nippon Paint, dan perlengkapan finishing.</p>",
        "supplier_rank": 1,
        "is_company": True,
    },
    {
        "name": "UD Kayu Sejati Mandiri",
        "phone": "0711-7744556",
        "street": "Jl. Yos Sudarso No. 210, 8 Ilir",
        "city": "Palembang",
        "zip": "30115",
        "comment": "<p>Supplier kayu kamper, meranti, dan plywood. Bisa potong custom.</p>",
        "supplier_rank": 1,
        "is_company": True,
    },
]

# --- 3c. Workers ---
WORKERS = [
    # Mandor / supervisors
    {"name": "Hendra Saputra", "role_type": "mandor", "default_daily_wage": 150000, "phone": "081367110001"},
    {"name": "Agus Firmansyah", "role_type": "mandor", "default_daily_wage": 150000, "phone": "081367110002"},
    # Tukang (skilled labor)
    {"name": "Bambang Suryadi", "role_type": "tukang", "default_daily_wage": 100000, "phone": "081367220001"},
    {"name": "Rudi Hartono", "role_type": "tukang", "default_daily_wage": 100000, "phone": "081367220002"},
    {"name": "Dedi Mulyadi", "role_type": "tukang", "default_daily_wage": 95000, "phone": "081367220003"},
    {"name": "Slamet Riyadi", "role_type": "tukang", "default_daily_wage": 95000, "phone": "081367220004"},
    {"name": "Wahyu Nugroho", "role_type": "tukang", "default_daily_wage": 90000, "phone": "081367220005"},
    {"name": "Eko Prasetyo", "role_type": "tukang", "default_daily_wage": 90000, "phone": "081367220006"},
    {"name": "Suparman", "role_type": "tukang", "default_daily_wage": 100000, "phone": "081367220007"},
    {"name": "Joko Susanto", "role_type": "tukang", "default_daily_wage": 85000, "phone": "081367220008"},
    {"name": "Andi Wijaya", "role_type": "tukang", "default_daily_wage": 90000, "phone": "081367220009"},
    {"name": "Budi Santoso", "role_type": "tukang", "default_daily_wage": 95000, "phone": "081367220010"},
    {"name": "Iwan Setiawan", "role_type": "tukang", "default_daily_wage": 85000, "phone": "081367220011"},
    {"name": "Rizal Fauzi", "role_type": "tukang", "default_daily_wage": 90000, "phone": "081367220012"},
    # Kenek (helpers / unskilled)
    {"name": "Tono", "role_type": "kenek", "default_daily_wage": 65000, "phone": "081367330001"},
    {"name": "Sugi Hartanto", "role_type": "kenek", "default_daily_wage": 65000, "phone": "081367330002"},
    {"name": "Darmawan", "role_type": "kenek", "default_daily_wage": 60000, "phone": "081367330003"},
    {"name": "Yanto", "role_type": "kenek", "default_daily_wage": 60000, "phone": "081367330004"},
    {"name": "Surya Pratama", "role_type": "kenek", "default_daily_wage": 65000, "phone": "081367330005"},
    {"name": "Feri Irawan", "role_type": "kenek", "default_daily_wage": 60000, "phone": "081367330006"},
    {"name": "Arifin", "role_type": "kenek", "default_daily_wage": 60000, "phone": "081367330007"},
    {"name": "Maman Sudrajat", "role_type": "kenek", "default_daily_wage": 65000, "phone": "081367330008"},
    # Other / specialist
    {"name": "Pak Usman (Elektrikal)", "role_type": "other", "default_daily_wage": 120000, "phone": "081367440001"},
    {"name": "Pak Rosid (Plumbing)", "role_type": "other", "default_daily_wage": 110000, "phone": "081367440002"},
]

# --- 3d. Projects (matches README context) ---
PROJECTS = [
    # PT Rid Jaya Bersama
    {"name": "Dream Land 1 (Borang)", "client": "PT Rid Jaya Bersama",
     "type": "Pembangunan perumahan", "location": "Borang, Palembang",
     "start_delta": -180, "duration": 270, "contract_value": 2_800_000_000,
     "status": "in_progress"},
    # PT Ramatrimitra Development
    {"name": "Kartika Mataram (Talang Jambi)", "client": "PT Ramatrimitra Development",
     "type": "Pembangunan perumahan", "location": "Talang Jambi, Palembang",
     "start_delta": -365, "duration": 300, "contract_value": 3_500_000_000,
     "status": "done"},
    {"name": "The Greenvillage (Mata Merah)", "client": "PT Ramatrimitra Development",
     "type": "Pembangunan perumahan cluster", "location": "Mata Merah, Palembang",
     "start_delta": -90, "duration": 240, "contract_value": 4_200_000_000,
     "status": "in_progress"},
    {"name": "Taman Asri 2 (Gandus)", "client": "PT Ramatrimitra Development",
     "type": "Pembangunan perumahan subsidi", "location": "Gandus, Palembang",
     "start_delta": -420, "duration": 360, "contract_value": 2_100_000_000,
     "status": "done"},
    {"name": "Siknatur (Gandus)", "client": "PT Ramatrimitra Development",
     "type": "Pembangunan townhouse", "location": "Gandus, Palembang",
     "start_delta": -30, "duration": 180, "contract_value": 1_800_000_000,
     "status": "in_progress"},
    # PT Agung Sumatera Development
    {"name": "Osaka Residence", "client": "PT Agung Sumatera Development",
     "type": "Pembangunan perumahan premium", "location": "Sukarami, Palembang",
     "start_delta": -500, "duration": 360, "contract_value": 5_000_000_000,
     "status": "done"},
    {"name": "Osaka Residence 2", "client": "PT Agung Sumatera Development",
     "type": "Pembangunan perumahan premium", "location": "Sukarami, Palembang",
     "start_delta": -120, "duration": 300, "contract_value": 5_500_000_000,
     "status": "in_progress"},
    {"name": "Griya Bukit Berlian", "client": "PT Agung Sumatera Development",
     "type": "Pembangunan perumahan cluster", "location": "Sako, Palembang",
     "start_delta": -600, "duration": 400, "contract_value": 3_800_000_000,
     "status": "done"},
    {"name": "Orchard Sukomoro", "client": "PT Agung Sumatera Development",
     "type": "Pembangunan ruko dan perumahan", "location": "Sukomoro, Palembang",
     "start_delta": -60, "duration": 240, "contract_value": 4_100_000_000,
     "status": "in_progress"},
    {"name": "Orchard Tanjung Sari", "client": "PT Agung Sumatera Development",
     "type": "Pembangunan perumahan cluster", "location": "Tanjung Sari, OKI",
     "start_delta": -15, "duration": 300, "contract_value": 3_200_000_000,
     "status": "in_progress"},
]

# --- 3e. Inventory products (building materials for stock module) ---
PRODUCTS = [
    # Semen
    {"name": "Semen Tiga Roda 50 kg", "categ": "Semen", "uom": "sak",
     "price": 72000, "cost": 65000},
    {"name": "Semen Padang 40 kg", "categ": "Semen", "uom": "sak",
     "price": 58000, "cost": 52000},
    # Besi
    {"name": "Besi Beton Polos 10mm (12m)", "categ": "Besi & Baja", "uom": "batang",
     "price": 85000, "cost": 75000},
    {"name": "Besi Beton Polos 12mm (12m)", "categ": "Besi & Baja", "uom": "batang",
     "price": 120000, "cost": 108000},
    {"name": "Besi Beton Ulir 13mm (12m)", "categ": "Besi & Baja", "uom": "batang",
     "price": 155000, "cost": 140000},
    {"name": "Wiremesh M8 (2.1m x 5.4m)", "categ": "Besi & Baja", "uom": "lembar",
     "price": 580000, "cost": 520000},
    # Pasir & Batu
    {"name": "Pasir Cor (per m³)", "categ": "Agregat", "uom": "m³",
     "price": 350000, "cost": 300000},
    {"name": "Batu Split 1-2 (per m³)", "categ": "Agregat", "uom": "m³",
     "price": 420000, "cost": 370000},
    {"name": "Batu Bata Merah Press", "categ": "Agregat", "uom": "unit",
     "price": 800, "cost": 600},
    # Kayu
    {"name": "Kayu Kamper 6/12 (4m)", "categ": "Kayu", "uom": "batang",
     "price": 135000, "cost": 115000},
    {"name": "Plywood 9mm (122x244cm)", "categ": "Kayu", "uom": "lembar",
     "price": 125000, "cost": 105000},
    {"name": "Kayu Meranti 5/7 (4m)", "categ": "Kayu", "uom": "batang",
     "price": 55000, "cost": 45000},
    # Cat & Finishing
    {"name": "Cat Dulux Catylac Interior 5 kg", "categ": "Cat & Finishing", "uom": "unit",
     "price": 95000, "cost": 82000},
    {"name": "Cat Nippon Vinilex 25 kg", "categ": "Cat & Finishing", "uom": "unit",
     "price": 380000, "cost": 330000},
    {"name": "Plamir Tembok 25 kg", "categ": "Cat & Finishing", "uom": "unit",
     "price": 110000, "cost": 90000},
    # Atap
    {"name": "Genteng Beton Flat", "categ": "Atap", "uom": "unit",
     "price": 11000, "cost": 8500},
    {"name": "Baja Ringan C75.075 (6m)", "categ": "Atap", "uom": "batang",
     "price": 72000, "cost": 62000},
    # Pipa & Sanitasi
    {"name": "Pipa PVC Rucika 4\" AW (4m)", "categ": "Pipa & Sanitasi", "uom": "batang",
     "price": 120000, "cost": 100000},
    {"name": "Pipa PVC Rucika 3/4\" D (4m)", "categ": "Pipa & Sanitasi", "uom": "batang",
     "price": 28000, "cost": 22000},
    # Kelistrikan
    {"name": "Kabel NYM 3x2.5mm² (50m)", "categ": "Kelistrikan", "uom": "unit",
     "price": 650000, "cost": 560000},
    {"name": "MCB 16A Schneider", "categ": "Kelistrikan", "uom": "unit",
     "price": 65000, "cost": 48000},
]

# --- 3f. Material purchase templates for wage_recap module ---
MATERIAL_PURCHASE_TEMPLATES = [
    {"name": "Semen Tiga Roda 50 kg", "unit": "sak", "unit_price": 72000, "qty_range": (20, 100)},
    {"name": "Semen Padang 40 kg", "unit": "sak", "unit_price": 58000, "qty_range": (30, 80)},
    {"name": "Besi Beton Polos 10mm", "unit": "batang", "unit_price": 85000, "qty_range": (50, 200)},
    {"name": "Besi Beton Ulir 13mm", "unit": "batang", "unit_price": 155000, "qty_range": (30, 100)},
    {"name": "Pasir Cor", "unit": "m³", "unit_price": 350000, "qty_range": (5, 25)},
    {"name": "Batu Split 1-2", "unit": "m³", "unit_price": 420000, "qty_range": (5, 20)},
    {"name": "Batu Bata Merah Press", "unit": "buah", "unit_price": 800, "qty_range": (2000, 10000)},
    {"name": "Kayu Kamper 6/12", "unit": "batang", "unit_price": 135000, "qty_range": (20, 80)},
    {"name": "Plywood 9mm", "unit": "lembar", "unit_price": 125000, "qty_range": (10, 50)},
    {"name": "Cat Dulux Catylac 5 kg", "unit": "kaleng", "unit_price": 95000, "qty_range": (5, 30)},
    {"name": "Genteng Beton Flat", "unit": "buah", "unit_price": 11000, "qty_range": (200, 1000)},
    {"name": "Baja Ringan C75.075", "unit": "batang", "unit_price": 72000, "qty_range": (30, 120)},
    {"name": "Pipa PVC 4\" AW", "unit": "batang", "unit_price": 120000, "qty_range": (10, 40)},
    {"name": "Kabel NYM 3x2.5mm²", "unit": "roll", "unit_price": 650000, "qty_range": (2, 10)},
    {"name": "Wiremesh M8", "unit": "lembar", "unit_price": 580000, "qty_range": (5, 30)},
    {"name": "Plamir Tembok 25 kg", "unit": "sak", "unit_price": 110000, "qty_range": (5, 20)},
]

# --- Map material-purchase template names to product.product names ---
# Some templates use shortened names; map them to the full product name in PRODUCTS.
_MATERIAL_TO_PRODUCT = {
    "Besi Beton Polos 10mm": "Besi Beton Polos 10mm (12m)",
    "Besi Beton Ulir 13mm": "Besi Beton Ulir 13mm (12m)",
    "Pasir Cor": "Pasir Cor (per m³)",
    "Batu Split 1-2": "Batu Split 1-2 (per m³)",
    "Kayu Kamper 6/12": "Kayu Kamper 6/12 (4m)",
    "Plywood 9mm": "Plywood 9mm (122x244cm)",
    "Cat Dulux Catylac 5 kg": "Cat Dulux Catylac Interior 5 kg",
    "Baja Ringan C75.075": "Baja Ringan C75.075 (6m)",
    "Pipa PVC 4\" AW": "Pipa PVC Rucika 4\" AW (4m)",
    "Kabel NYM 3x2.5mm²": "Kabel NYM 3x2.5mm² (50m)",
    "Plamir Tembok 25 kg": "Plamir Tembok 25 kg",
}


def _resolve_product_name(mat_name):
    """Return the canonical product name from PRODUCTS for a material template name."""
    return _MATERIAL_TO_PRODUCT.get(mat_name, mat_name)


# ---------------------------------------------------------------------------
# 4.  Seeding functions
# ---------------------------------------------------------------------------
def seed_clients(models, uid, currency_id):
    print("\n── Seeding Clients ──")
    ids = {}
    for c in CLIENTS:
        cid = find_or_create(models, uid, "res.partner", ("name", "=", c["name"]), c)
        ids[c["name"]] = cid
        print(f"   ✓ {c['name']}  (id={cid})")
    return ids


def seed_suppliers(models, uid, currency_id):
    print("\n── Seeding Suppliers ──")
    ids = {}
    for s in SUPPLIERS:
        sid = find_or_create(models, uid, "res.partner", ("name", "=", s["name"]), s)
        ids[s["name"]] = sid
        print(f"   ✓ {s['name']}  (id={sid})")
    return ids


def seed_projects(models, uid, client_ids, currency_id):
    print("\n── Seeding Projects ──")
    today = date.today()
    project_ids = {}

    # Determine if project.project has our expected custom fields
    # Standard Odoo project fields we can use
    for p in PROJECTS:
        start = today + timedelta(days=p["start_delta"])
        end = start + timedelta(days=p["duration"])

        vals = {
            "name": p["name"],
            "description": (
                f"<p><b>Tipe:</b> {p['type']}<br/>"
                f"<b>Lokasi:</b> {p['location']}<br/>"
                f"<b>Nilai Kontrak:</b> Rp {p['contract_value']:,.0f}</p>"
            ),
        }
        if p["client"] and p["client"] in client_ids:
            vals["partner_id"] = client_ids[p["client"]]

        # Check available fields for date
        try:
            vals["date_start"] = start.isoformat()
            vals["date"] = end.isoformat()
        except Exception:
            pass

        pid = find_or_create(models, uid, "project.project", ("name", "=", p["name"]), vals)
        project_ids[p["name"]] = pid
        print(f"   ✓ {p['name']}  (id={pid})")

    return project_ids


def seed_project_locations(models, uid, project_ids):
    """Create project stock locations under WH/Stock → Projects → <project>."""
    print("\n── Seeding Project Stock Locations ──")
    location_ids = {}

    # Find the main 'Stock' internal location (WH/Stock)
    stock_loc_ids = x(
        models, uid, "stock.location", "search",
        [[
            ("usage", "=", "internal"),
            ("name", "=", "Stock"),
            ("company_id", "!=", False),
        ]],
        {"limit": 1},
    )
    if not stock_loc_ids:
        print("   ⚠ Could not find WH/Stock location. Skipping project locations.")
        return location_ids

    stock_loc_id = stock_loc_ids[0]

    # Create or find the 'Projects' parent location under Stock
    projects_loc_id = find_or_create(
        models, uid, "stock.location",
        ("name", "=", "Projects"),
        {
            "name": "Projects",
            "usage": "internal",
            "location_id": stock_loc_id,
        },
    )
    print(f"   ✓ Projects location  (id={projects_loc_id})")

    # Create a child location for each active project
    active_projects = [
        p for p in PROJECTS if p["status"] == "in_progress"
    ]
    for proj in active_projects:
        proj_name = proj["name"]
        pid = project_ids.get(proj_name)
        if not pid:
            continue

        loc_name = proj_name
        loc_id = find_or_create(
            models, uid, "stock.location",
            ("name", "=", loc_name),
            {
                "name": loc_name,
                "usage": "internal",
                "location_id": projects_loc_id,
            },
        )
        location_ids[proj_name] = loc_id
        print(f"   ✓ {loc_name}  (id={loc_id})")

    print(f"   ✓ Created/found {len(location_ids)} project locations")
    return location_ids


def seed_workers(models, uid, project_ids, currency_id):
    print("\n── Seeding Workers ──")
    worker_ids = {}
    project_names = list(project_ids.keys())

    for i, w in enumerate(WORKERS):
        vals = {
            "name": w["name"],
            "role_type": w["role_type"],
            "default_daily_wage": w["default_daily_wage"],
            "phone": w["phone"],
            "currency_id": currency_id,
            "active": True,
        }
        # Assign workers to active projects (round-robin among in-progress ones)
        active_projects = [
            pn for pn in project_names
            if any(pr["name"] == pn and pr["status"] == "in_progress" for pr in PROJECTS)
        ]
        if active_projects:
            assigned = active_projects[i % len(active_projects)]
            vals["project_id"] = project_ids[assigned]

        wid = find_or_create(
            models, uid, "contractor.worker", ("name", "=", w["name"]), vals
        )
        worker_ids[w["name"]] = wid
        print(f"   ✓ {w['name']} ({w['role_type']}, Rp{w['default_daily_wage']:,}/hari)  (id={wid})")

    return worker_ids


def seed_wage_recaps(models, uid, project_ids, worker_ids, currency_id):
    """Generate weekly wage recaps for the last ~8 weeks across active projects."""
    print("\n── Seeding Wage Recaps ──")
    today = date.today()
    count = 0

    active_projects = [
        p for p in PROJECTS if p["status"] == "in_progress"
    ]
    worker_list = list(worker_ids.items())

    for proj in active_projects:
        pid = project_ids[proj["name"]]
        proj_start = today + timedelta(days=proj["start_delta"])

        # Generate recaps for weeks going back, up to 8 weeks or project start
        for week_offset in range(8):
            # Saturday = payday
            days_to_last_saturday = (today.weekday() + 2) % 7
            period_end = today - timedelta(days=days_to_last_saturday + 7 * week_offset)
            period_start = period_end - timedelta(days=5)  # Monday

            if period_start < proj_start:
                break

            # Pick a subset of workers for this project/week
            num_workers = random.randint(4, min(12, len(worker_list)))
            selected = random.sample(worker_list, num_workers)

            for worker_name, wid in selected:
                w_data = next((w for w in WORKERS if w["name"] == worker_name), None)
                if not w_data:
                    continue

                work_days = random.choice([4, 4.5, 5, 5, 5.5, 6, 6, 6])
                daily_wage = w_data["default_daily_wage"]
                is_paid = week_offset >= 1  # Current week unpaid, older weeks paid

                vals = {
                    "project_id": pid,
                    "period_start": period_start.isoformat(),
                    "period_end": period_end.isoformat(),
                    "worker_id": wid,
                    "daily_wage": daily_wage,
                    "work_days": work_days,
                    "payment_method": "cash",
                    "payment_status": "paid" if is_paid else "unpaid",
                    "currency_id": currency_id,
                }
                if is_paid:
                    vals["payment_date"] = period_end.isoformat()

                # Check if this recap already exists
                existing = x(
                    models, uid, "contractor.wage.recap", "search",
                    [[
                        ("project_id", "=", pid),
                        ("worker_id", "=", wid),
                        ("period_start", "=", period_start.isoformat()),
                    ]],
                    {"limit": 1},
                )
                if not existing:
                    x(models, uid, "contractor.wage.recap", "create", [vals])
                    count += 1

    print(f"   ✓ Created {count} wage recap entries")
    return count


def seed_material_purchases(models, uid, project_ids, supplier_ids, currency_id,
                            project_location_ids=None):
    """Generate material purchase records across active projects.

    Phase-2: links each purchase to a ``product.product``, ``uom.uom``,
    and project stock location.  The legacy ``unit`` field is no longer set.
    """
    print("\n── Seeding Material Purchases ──")
    today = date.today()
    count = 0
    supplier_names = list(supplier_ids.keys())
    project_location_ids = project_location_ids or {}

    # Pre-resolve product.product ids and UoMs so we don't query per-loop
    _product_cache = {}   # canonical_name → product.product id
    _uom_cache = {}       # canonical_name → uom.uom id

    def _get_product_and_uom(mat_name):
        canonical = _resolve_product_name(mat_name)
        if canonical not in _product_cache:
            pp_ids = x(
                models, uid, "product.product", "search",
                [[("name", "=", canonical)]],
                {"limit": 1},
            )
            if not pp_ids:
                # Try ilike as fallback
                pp_ids = x(
                    models, uid, "product.product", "search",
                    [[("name", "ilike", canonical)]],
                    {"limit": 1},
                )
            _product_cache[canonical] = pp_ids[0] if pp_ids else False
            if pp_ids:
                prod_data = x(
                    models, uid, "product.product", "read",
                    [pp_ids[:1], ["uom_id"]],
                )[0]
                _uom_cache[canonical] = prod_data["uom_id"][0] if prod_data.get("uom_id") else False
            else:
                _uom_cache[canonical] = False
        return _product_cache.get(canonical, False), _uom_cache.get(canonical, False)

    active_projects = [p for p in PROJECTS if p["status"] == "in_progress"]

    for proj in active_projects:
        pid = project_ids[proj["name"]]
        proj_start = today + timedelta(days=proj["start_delta"])

        # Generate 8-15 material purchases per active project
        num_purchases = random.randint(8, 15)
        selected_materials = random.sample(
            MATERIAL_PURCHASE_TEMPLATES,
            min(num_purchases, len(MATERIAL_PURCHASE_TEMPLATES)),
        )

        for mat in selected_materials:
            purchase_date = proj_start + timedelta(
                days=random.randint(0, max(1, (today - proj_start).days))
            )
            qty = random.randint(*mat["qty_range"])
            # Add some realistic price variation (±5%)
            unit_price = int(mat["unit_price"] * random.uniform(0.95, 1.05))
            supplier = random.choice(supplier_names)
            is_paid = purchase_date < today - timedelta(days=14)

            product_id, uom_id = _get_product_and_uom(mat["name"])

            vals = {
                "name": mat["name"],
                "project_id": pid,
                "supplier_id": supplier_ids[supplier],
                "purchase_date": purchase_date.isoformat(),
                "quantity": qty,
                "unit_price": unit_price,
                "payment_status": "paid" if is_paid else "unpaid",
                "currency_id": currency_id,
                "notes": f"Pengiriman ke lokasi {proj['location']}" if random.random() < 0.3 else False,
            }
            if product_id:
                vals["product_id"] = product_id
            if uom_id:
                vals["product_uom_id"] = uom_id
            loc_id = project_location_ids.get(proj["name"])
            if loc_id:
                vals["stock_location_id"] = loc_id

            existing = x(
                models, uid, "contractor.material.purchase", "search",
                [[
                    ("project_id", "=", pid),
                    ("name", "=", mat["name"]),
                    ("purchase_date", "=", purchase_date.isoformat()),
                ]],
                {"limit": 1},
            )
            if not existing:
                x(models, uid, "contractor.material.purchase", "create", [vals])
                count += 1

    print(f"   ✓ Created {count} material purchase records")
    return count


def seed_material_usage(models, uid, project_ids, worker_ids,
                        project_location_ids=None):
    """Create demo material-usage records for active projects.

    Each active project gets 5-10 usage entries, spread over the last 4 weeks,
    referencing products from the PRODUCTS list.
    """
    print("\n── Seeding Material Usage ──")
    today = date.today()
    count = 0
    project_location_ids = project_location_ids or {}

    # Pre-fetch all product.product records matching PRODUCTS names
    product_name_list = [p["name"] for p in PRODUCTS]
    all_pp_ids = x(
        models, uid, "product.product", "search_read",
        [[("name", "in", product_name_list)]],
        {"fields": ["id", "name", "uom_id"]},
    )
    product_pool = []  # list of (id, name, uom_id)
    for pp in all_pp_ids:
        uom = pp["uom_id"][0] if pp.get("uom_id") else False
        product_pool.append((pp["id"], pp["name"], uom))

    if not product_pool:
        print("   ⚠ No products found in database. Skipping material usage.")
        return count

    # Workers — prefer mandor for assignment
    mandor_ids = [
        wid for wname, wid in worker_ids.items()
        if any(w["name"] == wname and w["role_type"] == "mandor" for w in WORKERS)
    ]
    all_worker_ids = list(worker_ids.values())

    active_projects = [p for p in PROJECTS if p["status"] == "in_progress"]

    for proj in active_projects:
        pid = project_ids.get(proj["name"])
        if not pid:
            continue

        num_usages = random.randint(5, 10)
        selected = random.choices(product_pool, k=num_usages)

        for prod_id, prod_name, uom_id in selected:
            # Usage date within the last 4 weeks
            usage_date = today - timedelta(days=random.randint(0, 27))

            # Reasonable quantity — keep lower than typical purchase qty
            prod_data = next((p for p in PRODUCTS if p["name"] == prod_name), None)
            if prod_data:
                low = prod_data.get("qty_range", (1, 10))[0] if "qty_range" in prod_data else 1
                # For PRODUCTS list there is no qty_range, so pick something sensible
                qty = round(random.uniform(1, 30), 1)
            else:
                qty = round(random.uniform(1, 20), 1)

            # Prefer mandor 60% of the time
            if mandor_ids and random.random() < 0.6:
                worker_id = random.choice(mandor_ids)
            elif all_worker_ids:
                worker_id = random.choice(all_worker_ids)
            else:
                worker_id = False

            vals = {
                "project_id": pid,
                "product_id": prod_id,
                "usage_date": usage_date.isoformat(),
                "quantity": qty,
            }
            if uom_id:
                vals["product_uom_id"] = uom_id
            loc_id = project_location_ids.get(proj["name"])
            if loc_id:
                vals["source_location_id"] = loc_id
            if worker_id:
                vals["worker_id"] = worker_id
            if random.random() < 0.3:
                vals["notes"] = f"Pemakaian untuk area {random.choice(['pondasi', 'dinding', 'atap', 'finishing', 'lantai', 'kolom'])}."

            # Check existing
            existing = x(
                models, uid, "contractor.material.usage", "search",
                [[
                    ("project_id", "=", pid),
                    ("product_id", "=", prod_id),
                    ("usage_date", "=", usage_date.isoformat()),
                ]],
                {"limit": 1},
            )
            if not existing:
                x(models, uid, "contractor.material.usage", "create", [vals])
                count += 1

    print(f"   ✓ Created {count} material usage records")
    return count


def seed_inventory_products(models, uid, currency_id):
    """Create products in the Inventory module (product.product / product.template)."""
    print("\n── Seeding Inventory Products ──")
    product_ids = {}

    for p in PRODUCTS:
        categ_id = get_or_create_product_category(models, uid, p["categ"])
        uom_id = get_or_create_uom(models, uid, p["uom"])

        vals = {
            "name": p["name"],
            "categ_id": categ_id,
            "list_price": p["price"],
            "standard_price": p["cost"],
            "type": "consu",  # Odoo 19: 'consu' = Goods
            "is_storable": True,  # Enable inventory tracking
            "sale_ok": False,
            "purchase_ok": True,
        }
        if uom_id:
            vals["uom_id"] = uom_id

        pid = find_or_create(
            models, uid, "product.template", ("name", "=", p["name"]), vals
        )
        product_ids[p["name"]] = pid
        print(f"   ✓ {p['name']}  (categ={p['categ']}, cost=Rp{p['cost']:,})  (id={pid})")

    return product_ids


def seed_inventory_stock(models, uid, product_tmpl_ids, supplier_ids):
    """Create stock.picking (receipts) to give realistic on-hand quantities."""
    print("\n── Seeding Inventory Stock (Receipts) ──")

    # Get the Receipts picking type
    pick_type_ids = x(
        models, uid, "stock.picking.type", "search",
        [[("code", "=", "incoming")]],
        {"limit": 1},
    )
    if not pick_type_ids:
        print("   ⚠ No incoming picking type found. Skipping stock receipts.")
        return

    pick_type_id = pick_type_ids[0]
    pick_type_data = x(
        models, uid, "stock.picking.type", "read",
        [pick_type_ids, ["default_location_src_id", "default_location_dest_id"]],
    )[0]

    supplier_location = get_stock_location(models, uid, "supplier")
    stock_location = get_stock_location(models, uid, "internal")

    if not supplier_location or not stock_location:
        print("   ⚠ Could not find stock locations. Skipping.")
        return

    today = date.today()
    supplier_names = list(supplier_ids.keys())
    count = 0

    # Group products into batches (simulate receiving shipments)
    product_list = list(product_tmpl_ids.items())
    random.shuffle(product_list)

    # Create 4 receipt shipments over the past month
    for batch_idx in range(4):
        receipt_date = today - timedelta(days=random.randint(3, 30))
        supplier_name = supplier_names[batch_idx % len(supplier_names)]

        # Each batch has 4-6 products
        batch_start = batch_idx * 5
        batch_products = product_list[batch_start:batch_start + 5]
        if not batch_products:
            break

        # Get product.product IDs from product.template IDs
        move_lines = []
        for prod_name, tmpl_id in batch_products:
            prod_prod_ids = x(
                models, uid, "product.product", "search",
                [[("product_tmpl_id", "=", tmpl_id)]],
                {"limit": 1},
            )
            if not prod_prod_ids:
                continue

            prod_data = next((p for p in PRODUCTS if p["name"] == prod_name), None)
            if not prod_data:
                continue

            uom_id = get_or_create_uom(models, uid, prod_data["uom"])
            qty = random.randint(20, 150)

            move_lines.append((0, 0, {
                "product_id": prod_prod_ids[0],
                "product_uom_qty": qty,
                "product_uom": uom_id or 1,
                "location_id": supplier_location,
                "location_dest_id": stock_location,
            }))

        if not move_lines:
            continue

        picking_vals = {
            "picking_type_id": pick_type_id,
            "partner_id": supplier_ids[supplier_name],
            "scheduled_date": receipt_date.isoformat(),
            "origin": f"DEMO-RCV-{batch_idx + 1:03d}",
            "move_ids": move_lines,
            "location_id": supplier_location,
            "location_dest_id": stock_location,
        }

        # Check if this receipt already exists
        existing = x(
            models, uid, "stock.picking", "search",
            [[("origin", "=", f"DEMO-RCV-{batch_idx + 1:03d}")]],
            {"limit": 1},
        )
        if existing:
            print(f"   ⤳ Receipt DEMO-RCV-{batch_idx + 1:03d} already exists, skipping")
            continue

        try:
            picking_id = x(models, uid, "stock.picking", "create", [picking_vals])
            # Confirm and validate to complete the receipt
            try:
                x(models, uid, "stock.picking", "action_confirm", [[picking_id]])
                # Set quantities done on the moves
                moves = x(
                    models, uid, "stock.move", "search",
                    [[("picking_id", "=", picking_id)]],
                )
                for move_id in moves:
                    move_data = x(
                        models, uid, "stock.move", "read",
                        [[move_id], ["product_uom_qty"]],
                    )[0]
                    x(
                        models, uid, "stock.move", "write",
                        [[move_id], {"quantity": move_data["product_uom_qty"]}],
                    )
                # Validate the receipt
                try:
                    x(models, uid, "stock.picking", "button_validate", [[picking_id]])
                except Exception as e:
                    # Some Odoo versions may require a wizard for validation
                    print(f"   ⚠ Could not auto-validate receipt {batch_idx + 1}: {e}")
            except Exception as e:
                print(f"   ⚠ Could not confirm receipt {batch_idx + 1}: {e}")

            count += 1
            print(f"   ✓ Receipt DEMO-RCV-{batch_idx + 1:03d} from {supplier_name}  (id={picking_id})")
        except Exception as e:
            print(f"   ✗ Failed to create receipt {batch_idx + 1}: {e}")

    print(f"   ✓ Created {count} stock receipts")


# ---------------------------------------------------------------------------
# 5.  Main
# ---------------------------------------------------------------------------
def main():
    print("=" * 64)
    print("  ConstructFlow ERP — Demo Data Seeder")
    print("=" * 64)

    uid, models = connect()

    # Get IDR currency
    currency_id = get_idr_currency(models, uid)
    print(f"OK  Using currency id={currency_id}")

    # Seed in dependency order
    client_ids = seed_clients(models, uid, currency_id)
    supplier_ids = seed_suppliers(models, uid, currency_id)
    project_ids = seed_projects(models, uid, client_ids, currency_id)
    project_location_ids = seed_project_locations(models, uid, project_ids)
    worker_ids = seed_workers(models, uid, project_ids, currency_id)
    seed_wage_recaps(models, uid, project_ids, worker_ids, currency_id)

    # Inventory module — products must be seeded BEFORE material purchases
    # so that product_id lookups succeed.
    product_tmpl_ids = seed_inventory_products(models, uid, currency_id)
    seed_inventory_stock(models, uid, product_tmpl_ids, supplier_ids)

    # Material purchases & usage (depend on products + project locations)
    seed_material_purchases(
        models, uid, project_ids, supplier_ids, currency_id,
        project_location_ids=project_location_ids,
    )
    usage_count = seed_material_usage(
        models, uid, project_ids, worker_ids,
        project_location_ids=project_location_ids,
    )

    print("\n" + "=" * 64)
    print("  ✅  Demo data seeding complete!")
    print("=" * 64)
    print(f"\n  Summary:")
    print(f"    Clients:          {len(client_ids)}")
    print(f"    Suppliers:        {len(supplier_ids)}")
    print(f"    Projects:         {len(project_ids)}")
    print(f"    Project Locations:{len(project_location_ids)}")
    print(f"    Workers:          {len(worker_ids)}")
    print(f"    Products:         {len(product_tmpl_ids)}")
    print(f"    Material Usage:   {usage_count}")
    print(f"\n  Login at {URL}/web with user='{ODOO_USER}' to verify.\n")


if __name__ == "__main__":
    main()
