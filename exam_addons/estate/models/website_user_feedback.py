from odoo import models, fields, api
from datetime import datetime

class WebsiteUserFeedback(models.Model):
    _name = 'website.user.feedback'
    _description = 'User Feedback'

    description = fields.Text(string='Feedback Description', required=True)
    create_datetime = fields.Datetime(string='Created On', default=datetime.now())