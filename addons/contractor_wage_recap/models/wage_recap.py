from odoo import api, fields, models


class ContractorWorker(models.Model):
    _name = "contractor.worker"
    _description = "Construction Worker"
    _order = "name"

    name = fields.Char(required=True)
    partner_id = fields.Many2one("res.partner", string="Contact")
    role_type = fields.Selection([
        ("tukang", "Tukang"),
        ("kenek", "Kenek"),
        ("mandor", "Mandor"),
        ("other", "Other"),
    ], default="tukang", required=True)
    default_daily_wage = fields.Monetary(currency_field="currency_id")
    phone = fields.Char()
    active = fields.Boolean(default=True)
    project_id = fields.Many2one("project.project", string="Default Project")
    notes = fields.Text()
    currency_id = fields.Many2one("res.currency", default=lambda self: self.env.company.currency_id)


class ContractorWageRecap(models.Model):
    _name = "contractor.wage.recap"
    _description = "Worker Wage Recap"
    _order = "period_start desc, project_id, worker_id"

    name = fields.Char(compute="_compute_name", store=True)
    project_id = fields.Many2one("project.project", required=True)
    period_start = fields.Date(required=True)
    period_end = fields.Date(required=True)
    worker_id = fields.Many2one("contractor.worker", required=True)
    role_type = fields.Selection(related="worker_id.role_type", store=True)
    daily_wage = fields.Monetary(currency_field="currency_id", required=True)
    work_days = fields.Float(required=True, default=0.0)
    total_wage = fields.Monetary(compute="_compute_total_wage", store=True, currency_field="currency_id")
    payment_method = fields.Selection([
        ("cash", "Cash"),
        ("bank_transfer", "Bank Transfer"),
        ("other", "Other"),
    ], default="cash")
    payment_date = fields.Date()
    payment_status = fields.Selection([
        ("unpaid", "Unpaid"),
        ("paid", "Paid"),
    ], default="unpaid", required=True)
    notes = fields.Text()
    currency_id = fields.Many2one("res.currency", default=lambda self: self.env.company.currency_id)

    @api.depends("worker_id", "project_id", "period_start", "period_end")
    def _compute_name(self):
        for rec in self:
            worker = rec.worker_id.name or "Worker"
            project = rec.project_id.name or "Project"
            rec.name = f"{worker} - {project} ({rec.period_start or ''} to {rec.period_end or ''})"

    @api.depends("daily_wage", "work_days")
    def _compute_total_wage(self):
        for rec in self:
            rec.total_wage = (rec.daily_wage or 0.0) * (rec.work_days or 0.0)

    @api.onchange("worker_id")
    def _onchange_worker_id(self):
        for rec in self:
            if rec.worker_id and not rec.daily_wage:
                rec.daily_wage = rec.worker_id.default_daily_wage


class ContractorMaterialPurchase(models.Model):
    _name = "contractor.material.purchase"
    _description = "Material Purchase Record"
    _order = "purchase_date desc"

    name = fields.Char(required=True, string="Material Name")
    project_id = fields.Many2one("project.project", required=True)
    supplier_id = fields.Many2one("res.partner", string="Supplier")
    purchase_date = fields.Date(required=True, default=fields.Date.context_today)
    quantity = fields.Float(required=True, default=1.0)
    unit = fields.Char(default="pcs")
    unit_price = fields.Monetary(currency_field="currency_id")
    total_price = fields.Monetary(compute="_compute_total_price", store=True, currency_field="currency_id")
    payment_status = fields.Selection([
        ("unpaid", "Unpaid"),
        ("paid", "Paid"),
    ], default="unpaid")
    receipt_reference = fields.Char(string="Receipt/Photo Reference")
    notes = fields.Text()
    currency_id = fields.Many2one("res.currency", default=lambda self: self.env.company.currency_id)

    @api.depends("quantity", "unit_price")
    def _compute_total_price(self):
        for rec in self:
            rec.total_price = (rec.quantity or 0.0) * (rec.unit_price or 0.0)
