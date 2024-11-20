from odoo import models, fields


class EstatePropertyOffer(models.Model):
    _inherit = "estate.property.offer"

    user_accept = fields.Many2one('res.users', string="User Accept", readonly=1)
    user_reject = fields.Many2one('res.users', string="User Reject", readonly=1)

    def action_send_mail_accept(self):
        template_id = self.env.ref('estate_send_email.email_template_accept_offer')
        if template_id:
            template_id.send_mail(self.id, force_send=True)

    def action_confirm(self):
        super(EstatePropertyOffer,self).action_confirm()
        self.user_accept = self.env.user
        self.property_id.onchange_partner_id()
        self.action_send_mail_accept()

    def action_cancel(self):
        super(EstatePropertyOffer,self).action_cancel()
        self.user_reject = self.env.user