from email.policy import default
from sqlite3.dbapi2 import apilevel
from datetime import timedelta
from functools import partial
from Tools.scripts.dutree import store

from odoo import models, fields, api, exceptions, _
from odoo.addons.test_convert.tests.test_env import record
from odoo.tools.populate import compute


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Estate Property Offer"

    price = fields.Float(digits=(16,2),string="Price")
    status = fields.Selection([
        ('accepted','Accepted'),
        ('refused','Refused'),
    ], copy=False, string="Status")
    partner_id = fields.Many2one('res.partner', required=True, string="Partner")
    property_id = fields.Many2one('estate.property', required=True, string="Property")
    property_type_id = fields.Many2one('estate.property.type',related='property_id.property_type_id', store=True)
    validity = fields.Integer(string="Validity", default=7)
    date_deadline = fields.Date(compute="compute_date_deadline", store=True)

    @api.depends("create_date","validity")
    def compute_date_deadline(self):
        for rec in self:
            if rec.create_date and rec.validity:
                rec.date_deadline = rec.create_date.date() + timedelta(days=rec.validity)
            else:
                rec.date_deadline = fields.Date.context_today(self) + timedelta(days=rec.validity or 0)

    def write(self, vals):
        for rec in self:
            if rec.status == "accepted":
                raise exceptions.UserError(_("Cannot Edit Offer Accepted"))
            return super(EstatePropertyOffer, self).write(vals)

    def unlink(self):
        for rec in self:
            if rec.status == "accepted":
                raise  exceptions.UserError(_("Cannot Delete Offer Accepted"))
            return super(EstatePropertyOffer, self).unlink()