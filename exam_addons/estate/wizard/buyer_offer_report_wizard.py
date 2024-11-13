from odoo import models, fields
from odoo.exceptions import UserError

class BuyerOfferReportWizard(models.TransientModel):
    _name = 'buyer.offer.report.wizard'
    _description = 'Buyer Offer Report Wizard'

    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    buyer_ids = fields.Many2many('res.partner', string='Buyers')

    def action_export_excel(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise UserError('Start Date cannot be later than End Date.')

        start_date = self.start_date
        end_date = self.end_date
        # Join selected buyer IDs into a comma-separated string
        buyer_ids = ','.join(map(str, self.buyer_ids.ids)) if self.buyer_ids else ''
        url = f'/buyer_offer_report_xlsx?start_date={start_date}&end_date={end_date}&buyer_ids={buyer_ids}'
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'self',
        }
