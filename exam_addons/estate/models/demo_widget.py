from odoo import models, fields, api

class DemoWidget(models.Model):
    _name = 'demo.widget'
    _description = 'Demo Widget'

    name = fields.Char(string="Name", required=True)
    color = fields.Integer(string="Color")
    date = fields.Date(string="Date")
    hide_color = fields.Boolean(string="Hide Color", default=False)
    hide_date = fields.Boolean(string="Hide Date", default=False)

    @api.model
    def update_hide_flags(self, flags):
        # Validate flags
        if not isinstance(flags, list) or len(flags) != 2:
            raise ValueError("Flags must be a list containing exactly two elements.")

        hide_color, hide_date = flags

        self.env['demo.widget'].search([]).write({
            'hide_color': hide_color,
            'hide_date': hide_date,
        })
        self.env['ir.config_parameter'].sudo().set_param('demo_widget.hide_color', hide_color)
        self.env['ir.config_parameter'].sudo().set_param('demo_widget.hide_date', hide_date)
        return True

    @api.model
    def get_hide_flags(self):
        """Retrieve the saved flags for hiding fields."""
        hide_color = self.env['ir.config_parameter'].sudo().get_param('demo_widget.hide_color', 'False') == 'True'
        hide_date = self.env['ir.config_parameter'].sudo().get_param('demo_widget.hide_date', 'False') == 'True'
        return [hide_color, hide_date]
