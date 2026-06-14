from odoo import api, fields, models


class ContractorMaterialPurchase(models.Model):
    """Project-level material purchase record.

    Phase-2 upgrade: links to ``product.product`` and ``uom.uom`` instead of
    free-text fields so that material data is consistent with Odoo Inventory.
    Optional links to ``purchase.order`` and ``stock.picking`` let users trace
    the full procurement chain from PO → receipt → project warehouse.

    Legacy free-text fields (``unit``) are kept for backward compatibility
    but hidden from the default views.
    """

    _name = "contractor.material.purchase"
    _description = "Material Purchase Record"
    _order = "purchase_date desc"

    # --- Core fields ---
    name = fields.Char(
        required=True,
        string="Material Name",
        help="Auto-filled from product when a product is selected.",
    )
    project_id = fields.Many2one("project.project", required=True)
    supplier_id = fields.Many2one(
        "res.partner",
        string="Supplier",
        domain=[("supplier_rank", ">", 0)],
    )
    purchase_date = fields.Date(required=True, default=fields.Date.context_today)

    # --- Product-linked fields (Level 1 — Inventory integration) ---
    product_id = fields.Many2one(
        "product.product",
        string="Material Product",
        help="Select a product from the Inventory catalog.",
    )
    product_uom_id = fields.Many2one(
        "uom.uom",
        string="Unit of Measure",
        help="Unit of measure from the Inventory module.",
    )
    quantity = fields.Float(required=True, default=1.0)
    unit_price = fields.Monetary(currency_field="currency_id")
    total_price = fields.Monetary(
        compute="_compute_total_price",
        store=True,
        currency_field="currency_id",
    )

    # --- Purchase & Stock integration (Level 2 foundation) ---
    stock_location_id = fields.Many2one(
        "stock.location",
        string="Project Stock Location",
        domain=[("usage", "=", "internal")],
        help="The project-site warehouse where this material is stored.",
    )
    purchase_order_id = fields.Many2one(
        "purchase.order",
        string="Purchase Order",
        help="The Odoo Purchase Order that originated this purchase.",
    )
    picking_id = fields.Many2one(
        "stock.picking",
        string="Receipt / Transfer",
        help="The Inventory receipt or transfer linked to this purchase.",
    )

    payment_status = fields.Selection(
        [("unpaid", "Unpaid"), ("paid", "Paid")],
        default="unpaid",
    )
    receipt_reference = fields.Char(string="Receipt/Photo Reference")
    notes = fields.Text()
    currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.company.currency_id,
    )

    # Legacy field — kept for backward compatibility with old records.
    unit = fields.Char(string="Unit (legacy)")

    # --- Computed / onchange ---
    @api.depends("quantity", "unit_price")
    def _compute_total_price(self):
        for rec in self:
            rec.total_price = (rec.quantity or 0.0) * (rec.unit_price or 0.0)

    @api.onchange("product_id")
    def _onchange_product_id(self):
        for rec in self:
            if rec.product_id:
                rec.name = rec.product_id.display_name
                rec.product_uom_id = rec.product_id.uom_id
                if not rec.unit_price:
                    rec.unit_price = rec.product_id.standard_price


class ContractorMaterialUsage(models.Model):
    """Records material consumption per project.

    Tracks *how much* of a product was actually used on a project site,
    bridging the gap between "we bought material" and "material was used."
    """

    _name = "contractor.material.usage"
    _description = "Material Usage / Pemakaian Material"
    _order = "usage_date desc"

    name = fields.Char(compute="_compute_name", store=True)
    project_id = fields.Many2one("project.project", required=True)
    product_id = fields.Many2one(
        "product.product",
        string="Material",
        required=True,
    )
    product_uom_id = fields.Many2one("uom.uom", string="Unit of Measure")
    source_location_id = fields.Many2one(
        "stock.location",
        string="Source Location",
        domain=[("usage", "=", "internal")],
        help="Project warehouse the material was taken from.",
    )
    usage_date = fields.Date(required=True, default=fields.Date.context_today)
    quantity = fields.Float(required=True, default=1.0, string="Quantity Used")
    worker_id = fields.Many2one(
        "contractor.worker",
        string="Mandor / Used By",
    )
    notes = fields.Text()

    @api.depends("product_id", "project_id", "usage_date")
    def _compute_name(self):
        for rec in self:
            product = rec.product_id.display_name or "Material"
            project = rec.project_id.name or "Project"
            rec.name = f"{product} — {project} ({rec.usage_date or ''})"

    @api.onchange("product_id")
    def _onchange_product_id(self):
        for rec in self:
            if rec.product_id:
                rec.product_uom_id = rec.product_id.uom_id
