import re
from odoo.exceptions import ValidationError

from odoo import fields, models, api
from odoo.tools.populate import compute


class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Property Type"

    name = fields.Char(string="Type Property", required=True)
    offer_ids = fields.One2many('estate.property.offer', 'property_type_id',string="Offers")
    offer_count = fields.Integer(string="Offers Count", compute="_compute_offer_count")

    @api.depends('offer_ids')
    def _compute_offer_count(self):
        for rec in self:
            rec.offer_count = len(rec.offer_ids)

    @api.constrains("name")
    def _check_unique_name(self):
        for rec in self:
            # if not re.match('^[a-zA-Z]+$', rec.name):
            #     raise ValidationError("Name only contain letters")
            existing_rec_name = self.search([
                ('id', '!=', rec.id),
                ('name', 'ilike', rec.name)
            ])
            if existing_rec_name:
                raise ValidationError("Name already exists")

    def action_view_offer(self):
        self.ensure_one()
        return {
            'type':'ir.actions.act_window',
            'name':'Offer',
            'res_model':'estate.property.offer',
            'view_mode':'tree,form',
            'domain': [('property_type_id', '=', self.id)],
            'target': 'current',
            'context': {'default_property_type_id': self.id},
        }
    _sql_constraints = [
        ('property_type_name_unique', 'UNIQUE(name)', 'The property type name must be unique.')
    ]