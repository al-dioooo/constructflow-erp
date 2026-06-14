{
    "name": "Contractor Wage Recap",
    "version": "19.0.1.0.0",
    "summary": "Mandor-managed worker wage recap and material expense records for contractor ERP MVP.",
    "category": "Project",
    "author": "Contractor ERP MVP",
    "license": "LGPL-3",
    "depends": ["base", "contacts", "project", "purchase"],
    "data": [
        "security/ir.model.access.csv",
        "views/wage_recap_views.xml",
    ],
    "application": True,
    "installable": True,
}
