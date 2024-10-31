from odoo import models, fields, exceptions, _

class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Estate Property Tag"

    name = fields.Char(string="Property Tag", required=True)

    _sql_constraints = [
        ('property_tag_name_unique', 'UNIQUE(name)', 'The property tag name must be unique.')
    ]