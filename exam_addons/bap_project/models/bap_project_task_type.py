from odoo import models, fields, api, _


class BapProjectTaskType(models.Model):
    _name = 'bap.project.task.type'
    _description = 'Bap Project Task Type'

    task_type_code = fields.Char(
        string='Type Code',
        readonly=True,
        default=lambda self: _('New Task Type Code')
    )
    take_type_name = fields.Char(string='Task Type Name', required=True)
    active = fields.Boolean(string='Active', default=True)
    @api.model
    def create(self, vals):
        vals['task_type_code'] = self.env['ir.sequence'].next_by_code('task_type_sequence_code')
        return super(BapProjectTaskType, self).create(vals)

    def name_get(self):
        result = []
        for task_type in self:
            name = task_type.take_type_name
            result.append((task_type.id, name))
        return result

