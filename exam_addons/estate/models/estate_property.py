from datetime import date

from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError




class EstateProperty(models.Model):
    _name = 'estate.property'
    _description = 'Estate Property'
    _inherit = ['mail.thread','mail.activity.mixin']

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')
    postcode = fields.Char(string='Postcode')
    date_availability = fields.Date(string='Date Available', copy=False, default=lambda self: date.today() + relativedelta(months=3) )
    expected_price = fields.Float(string='Expected Price',digits=(16,2), required=True)
    selling_price = fields.Float(string='Sell Price',digits=(16,2), copy=False, default=0.0)
    bedrooms = fields.Integer(string='Bedrooms')
    living_area = fields.Integer(string='Living area')
    facades = fields.Integer(string='Facades')
    garage = fields.Boolean(string='Garage')
    garden = fields.Boolean(string='Garden')
    garden_area = fields.Integer(string='Garden Area')
    garden_orientation = fields.Selection([
        ('north','North'),
        ('south','South'),
        ('east','East'),
        ('west','West')
    ])
    active = fields.Boolean(default=True)
    state = fields.Selection([
        ('new','New'),
        ('offer_received','Offer Received'),
        ('offer_accepted','Offer Accepted'),
        ('sold','Sold'),
        ('canceled','Canceled'),
    ],required=True, copy=False, default='new')
    property_type_id = fields.Many2one("estate.property.type", string="Property Type", required=True)
    partner_id = fields.Many2one('res.partner', string='Buyer', copy=False)
    user_id = fields.Many2one('res.users', string='Salesperson', default=lambda self: self.env.user)
    offer_ids = fields.One2many('estate.property.offer','property_id', string="Property Offer")
    tag_ids = fields.Many2many('estate.property.tag', string="Property Tag")
    total_area = fields.Integer(compute="compute_total_area", string="Total Area")

    @api.depends('living_area','garden_area')
    def compute_total_area(self):
        for rec in self:
            rec.total_area = (rec.living_area or 0) + (rec.garden_area or 0)

    best_price = fields.Float(string="Highest Price", compute="compute_best_price",digits=(16,2))

    @api.depends("offer_ids.price")
    def compute_best_price(self):
        for rec in self:
            rec.best_price = max(rec.offer_ids.mapped("price"), default=0)

    @api.onchange("garden")
    def onchange_garden(self):
        if not self.garden:
            self.garden_area = 0
            self.garden_orientation = ''

    @api.onchange("date_availability")
    def onchange_date_availability(self):
        if self.date_availability and self.date_availability < date.today():
            return {
                "warning":{
                    "title":_("Warning"),
                    "message":_("Availability Date is set in the part")
                }
            }

    @api.constrains("date_availability")
    def _check_date_availability(self):
        for rec in self:
            if rec.date_availability and rec.date_availability < date.today():
                raise ValidationError("Availability Date is set in the part")

    code = fields.Char(
        string="Code",
        required=True,
        readonly=True,
        copy=False, default=lambda self: _('New Code'))

    @api.model
    def create(self, vals):
        vals['code'] = self.env['ir.sequence'].next_by_code('estate_sequence_code')
        return super(EstateProperty, self).create(vals)

    def unlink(self):
        for rec in self:
            if rec.state not in ['new','canceled']:
                raise UserError(_("Can not Delete Property not in new or canceled"))
        return super(EstateProperty,self).unlink()

    @api.constrains('expected_price','selling_price','state')
    def _check_selling_price(self):
        for rec in self:
            if rec.state != 'new' and rec.selling_price >= 0 and rec.expected_price > 0:
                if rec.selling_price < 0.9 * rec.expected_price:
                    raise ValidationError("Selling Price Cannot Lower 90% Expected Price")

    def action_sold(self):
        for record in self:
            if record.state == 'canceled':
                raise UserError(_("A canceled property cannot be sold."))
            record.state = 'sold'

    def action_cancelled(self):
        for record in self:
            if record.state == 'sold':
                raise UserError(_('A sold property cannot be canceled.'))
            record.state = 'canceled'

    _sql_constraints = [
        ('check_expected_price_positive', 'CHECK(expected_price > 0)', 'The expected price must be strictly positive.'),
        ('check_selling_price_positive', 'CHECK(selling_price >= 0)', 'The selling price must be positive.')
    ]