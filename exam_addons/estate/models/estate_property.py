from email.policy import default
from tokenize import String

from odoo import models,fields
from datetime import date
from dateutil.relativedelta import relativedelta

class EstateProperty(models.Model):
    _name = 'estate.property'
    _description = 'Estate Property'

    name = fields.Char(string='Name', required = True)
    description = fields.Text(string='Description')
    postcode = fields.Char(string='Postcode')
    date_availability = fields.Date(string='Date Available', copy= False, default=lambda self: date.today() + relativedelta(months=3) )
    expected_price = fields.Float(string='Expected Price',digits=(16,2), required= True)
    selling_price = fields.Float(string='Sell Price',digits=(16,2), readonly= True, copy= False)
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
    active = fields.Boolean(default= True)
    state = fields.Selection([
        ('new','New'),
        ('offer_received','Offer Received'),
        ('offer_accepted','Offer Accepted'),
        ('sold','Sold'),
        ('canceled','Canceled'),
    ],required= True, copy= False, default='new')