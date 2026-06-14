{
    "name": "Contractor Wage Recap",
    "version": "19.0.2.0.0",
    "summary": "Mandor-managed worker wage recap, material tracking, and project stock integration for contractor ERP.",
    "category": "Project",
    "author": "Contractor ERP MVP",
    "license": "LGPL-3",
    "depends": ["base", "contacts", "project", "purchase", "stock", "purchase_stock"],
    "data": [
        "security/ir.model.access.csv",
        "views/wage_recap_views.xml",
        "views/material_views.xml",
        "views/purchase_ext_views.xml",
    ],
    "application": True,
    "installable": True,
}
