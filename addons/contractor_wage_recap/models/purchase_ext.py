from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    """Extend PO lines with project and stock-location tracking.

    This lets the contractor link each purchased material line to a
    specific construction project and its on-site warehouse, so that
    project material expenses and stock are automatically connected.
    """

    _inherit = "purchase.order.line"

    project_id = fields.Many2one(
        "project.project",
        string="Project",
        help="Construction project this material is purchased for.",
    )
    stock_location_id = fields.Many2one(
        "stock.location",
        string="Project Stock Location",
        domain=[("usage", "=", "internal")],
        help="The project-site warehouse to receive this material.",
    )

    @api.onchange("project_id")
    def _onchange_project_id(self):
        for rec in self:
            if rec.project_id:
                # Find project location under Stock/Projects
                location = self.env["stock.location"].search([
                    ("usage", "=", "internal"),
                    ("name", "=", rec.project_id.name),
                ], limit=1)
                if location:
                    rec.stock_location_id = location.id

    def _prepare_stock_move_vals(self, picking, price_unit, product_uom_qty, product_uom):
        res = super(PurchaseOrderLine, self)._prepare_stock_move_vals(
            picking, price_unit, product_uom_qty, product_uom
        )
        if self.project_id:
            res["project_id"] = self.project_id.id
        if self.stock_location_id:
            res["location_dest_id"] = self.stock_location_id.id
        return res


class StockMove(models.Model):
    """Extend stock.move to carry project_id and create material purchases when validated."""

    _inherit = "stock.move"

    project_id = fields.Many2one(
        "project.project",
        string="Project",
        help="Construction project this stock move is for.",
    )

    def _action_done(self, cancel_backorder=False):
        res = super(StockMove, self)._action_done(cancel_backorder=cancel_backorder)
        for move in res:
            if move.project_id and move.purchase_line_id:
                # Deduplication check
                existing = self.env["contractor.material.purchase"].search([
                    ("picking_id", "=", move.picking_id.id),
                    ("product_id", "=", move.product_id.id),
                    ("project_id", "=", move.project_id.id),
                    ("quantity", "=", move.quantity),
                ], limit=1)
                if not existing:
                    self.env["contractor.material.purchase"].create({
                        "name": move.product_id.display_name or move.name,
                        "project_id": move.project_id.id,
                        "supplier_id": move.picking_id.partner_id.id or move.purchase_line_id.order_id.partner_id.id,
                        "purchase_date": fields.Date.context_today(self),
                        "product_id": move.product_id.id,
                        "product_uom_id": move.product_uom.id,
                        "quantity": move.quantity,
                        "unit_price": move.purchase_line_id.price_unit,
                        "stock_location_id": move.location_dest_id.id,
                        "purchase_order_id": move.purchase_line_id.order_id.id,
                        "picking_id": move.picking_id.id,
                        "payment_status": "unpaid",
                    })
        return res
