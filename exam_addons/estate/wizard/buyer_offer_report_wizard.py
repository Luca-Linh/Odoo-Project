from odoo import models, fields
from odoo.exceptions import UserError

class BuyerOfferReportWizard(models.TransientModel):
    _name = 'buyer.offer.report.wizard'
    _description = 'Buyer Offer Report Wizard'

    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    buyer_id = fields.Many2one('res.partner', string='Buyer')

    def action_export_excel(self):
        # Validate that the start date is not after the end date
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise UserError('Start Date cannot be later than End Date.')

        # Prepare parameters for the report
        start_date = self.start_date
        end_date = self.end_date
        buyer_id = self.buyer_id.id if self.buyer_id else None  # Either the selected buyer or None

        if buyer_id:
            # Only one buyer is selected, pass the buyer ID
            url = f'/buyer_offer_report_xlsx?start_date={start_date}&end_date={end_date}&buyer_id={buyer_id}'
        else:
            # If no buyer is selected, do not filter by buyer_id
            url = f'/buyer_offer_report_xlsx?start_date={start_date}&end_date={end_date}'

        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'self',  # Open the URL in the same window
        }
