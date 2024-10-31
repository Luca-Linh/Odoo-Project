from datetime import timedelta
from email.policy import default

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import UserError


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Estate Property Offer"

    price = fields.Float(digits=(16,2),string="Price")
    status = fields.Selection([
        ('draft','Draft'),
        ('accepted','Accepted'),
        ('refused','Refused'),
    ], copy=False, string="Status", default='draft')
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

    def action_confirm(self):
        for offer in self:
            if offer.status == 'accepted':
                raise UserError(_("This offer is already accepted."))
            offer.status = 'accepted'
            offer.property_id.partner_id = offer.partner_id
            accepted_offers = offer.property_id.offer_ids.filtered(lambda o: o.status == 'accepted')
            offer.property_id.selling_price = sum(accepted_offers.mapped('price'))

    def action_cancel(self):
        for record in self:
            if record.status == 'accepted':
                raise UserError(_('An accepted offer cannot be refused.'))
            record.status = 'refused'

    _sql_constraints = [
        ('check_offer_price_positive','CHECK(price > 0)','The offer price must be strictly positive.')
    ]