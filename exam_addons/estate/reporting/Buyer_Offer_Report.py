from odoo import models, fields


class BuyerOfferReport(models.Model):
    _name = 'buyer.offer.report'
    _description = 'Buyer Offer Report'
    _auto = False

    buyer_id = fields.Many2one('res.partner', string='Buyer')
    property_count = fields.Integer(string='Total Properties')
    properties_accepted = fields.Integer(string='Accepted Properties')
    properties_sold = fields.Integer(string='Sold Properties')
    properties_canceled = fields.Integer(string='Canceled Properties')
    offers_accepted = fields.Integer(string='Accepted Offers')
    offers_rejected = fields.Integer(string='Rejected Offers')
    min_offer_price = fields.Float(string='Min Offer Price')
    max_offer_price = fields.Float(string='Max Offer Price')

    def init(self):
        self._cr.execute("DROP VIEW IF EXISTS buyer_offer_report")

        self._cr.execute(""" 
            CREATE OR REPLACE VIEW buyer_offer_report AS (
                SELECT row_number() OVER () AS id,
                    ep.partner_id AS buyer_id,
                    COUNT(ep.id) AS property_count,
                    COUNT(CASE WHEN ep.state = 'offer_accepted' THEN 1 END) AS properties_accepted,
                    COUNT(CASE WHEN ep.state = 'sold' THEN 1 END) AS properties_sold,
                    COUNT(CASE WHEN ep.state = 'canceled' THEN 1 END) AS properties_canceled,
                    COUNT(CASE WHEN epo.status = 'accepted' THEN 1 END) AS offers_accepted,
                    COUNT(CASE WHEN epo.status = 'refused' THEN 1 END) AS offers_rejected,
                    MIN(epo.price) AS min_offer_price,
                    MAX(epo.price) AS max_offer_price
                FROM estate_property ep
                LEFT JOIN estate_property_offer epo ON ep.id = epo.property_id
                GROUP BY ep.partner_id 
            )
        """)