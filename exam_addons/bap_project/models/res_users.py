from odoo import models, fields


class ResUsers(models.Model):
    _inherit = 'res.users'

    project_manager_ids = fields.One2many('bap.project', 'pm_id', string='Managed Projects')
    developer_ids = fields.One2many('bap.project', 'dev_id', string='Developer Projects')
    qc_ids = fields.One2many('bap.project', 'qc_id', string='Quality Controlled Projects')

