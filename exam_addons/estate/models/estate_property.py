from tokenize import String

from odoo import models,fields


class EstateProperty(models.Model):
    _name = 'estate.property'
    _description = 'Estate Property'

    name = fields.Char(string='Name', required = True)
    description = fields.Text(string='Description')
    postcode = fields.Char(string='Postcode')
    date_availability = fields.Date(string='Date Available')
    expected_price = fields.Float(string='Expected Price',digits=(16,2), required= True)
    selling_price = fields.Float(string='Sell Price',digits=(16,2))
    bedrooms = fields.Integer(string='bedrooms')
    living_area = fields.Integer(string='living area')
    facades = fields.Integer(string='facades')
    garage = fields.Boolean(string='garage')
    garden = fields.Boolean(string='garden')
    garden_area = fields.Integer(string='garden area')
    garden_orientation = fields.Selection([
        ('north','North'),
        ('south','South'),
        ('east','East'),
        ('west','West')
    ])