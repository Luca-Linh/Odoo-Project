from odoo import models, fields

class DemoWidget(models.Model):
    _name = 'demo.widget'
    _description = 'Demo Widget'

    name = fields.Char(string="Name", required=True)
    color = fields.Integer(string="Color")
    date = fields.Date(string="Date")
