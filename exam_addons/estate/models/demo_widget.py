from odoo import models, fields

class DemoWidget(models.Model):
    _name = 'demo.widget'
    _description = 'Demo Widget'

    name = fields.Char(string="Name", required=True)
    color = fields.Integer(string="Color")
    date = fields.Date(string="Date")

class View(models.Model):
    _inherit = 'ir.ui.view'

    type = fields.Selection(selection_add=[('student', 'Student')])

class ActWindowView(models.Model):
    _inherit = 'ir.actions.act_window.view'

    view_mode = fields.Selection(
        selection_add=[('student', 'Student')],
        ondelete={'student': 'cascade'}
    )