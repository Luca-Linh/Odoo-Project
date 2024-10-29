import re
from odoo.exceptions import ValidationError

from odoo import fields, models, api



class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Property Type"

    name = fields.Char(string="Type Property", required=True)

    @api.constrains("name")
    def _check_unique_name(self):
        for rec in self:
            if not re.match('^[a-zA-Z]+$', rec.name):
                raise ValidationError("Name only contain letters")
            existing_rec_count = self.search_count([
                ('name', '=', rec.name.lower())
            ])
            if existing_rec_count > 0:
                raise ValidationError("Name already exists")