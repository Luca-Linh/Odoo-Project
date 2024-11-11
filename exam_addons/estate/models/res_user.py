from odoo import models, fields
from odoo.fields import Date


class ResUser(models.Model):
    _inherit = 'res.users'

    property_ids = fields.One2many('estate.property','user_id', string='Properties', domain=[('date_availability','<=',Date.today())])