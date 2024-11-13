from datetime import timedelta


from odoo import models, fields, api, exceptions, _
from odoo.exceptions import UserError


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Estate Property Offer"

    price = fields.Float(digits=(16,2),string="Price")
    status = fields.Selection([
        ('new','New'),
        ('accepted','Accepted'),
        ('refused','Refused'),
    ], copy=False, string="Status", default='new')
    buyer_id = fields.Many2one('res.partner', required=True, string="Buyer")
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

    @api.model
    def create(self, vals):
        properties = self.env['estate.property'].browse(vals.get('property_id'))
        if properties.offer_ids.filtered(lambda o:o.price >= vals.get('price')):
            raise UserError(_("You cannot create offer with price lower than or equal to an existing offer."))
        if properties.state == 'new':
            properties.state = 'offer_received'
        return super(EstatePropertyOffer,self).create(vals)


    def update(self, vals):
        for rec in self:
            if rec.status == "accepted":
                raise exceptions.UserError(_("Cannot Edit Offer Accepted"))
        return super().update(vals)

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
            offer.property_id.partner_id = offer.buyer_id
            accepted_offers = offer.property_id.offer_ids.filtered(lambda o: o.status == 'accepted')
            offer.property_id.selling_price = sum(accepted_offers.mapped('price'))

    def action_cancel(self):
        for record in self:
            record.status = 'refused'

    # def total_price(self):
    #     accepted_offers = self.property_id.offer_ids.filtered(lambda o: o.status == 'accepted')
    #     total_price = sum(accepted_offers.mapped('price'))
    #     self.property_id.write({
    #         'partner_id':self.env.user.partner_id.id,
    #         'selling_price': total_price,
    #     })

    _sql_constraints = [
        ('check_offer_price_positive','CHECK(price > 0)','The offer price must be strictly positive.')
    ]