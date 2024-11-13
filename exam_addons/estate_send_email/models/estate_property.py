from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import re

class EstateProperty(models.Model):
    _inherit = 'estate.property'

    # buyer = partner
    buyer_mail = fields.Char(string='Buyer Mail', required=False)
    user_sold = fields.Many2one('res.users',string='Sold buy', readonly=1)

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        for rec in self:
            if rec.partner_id:
                rec.buyer_mail = rec.partner_id.email

    @api.constrains('buyer_mail')
    def _check_buyer_mail(self):
        for record in self:
            if record.buyer_mail:
                if not re.match(r"[^@]+@[^@]+\.[^@]+", record.buyer_mail):
                    raise ValidationError(_('Please enter a valid email address.'))

    def action_sold(self):
        super(EstateProperty, self).action_sold()
        self.user_sold = self.env.user

    def action_send_mail(self):
        template_id = self.env.ref('estate_send_email.email_template_property_sold')
        if template_id:
            template_id.send_mail(self.id, force_send=True)