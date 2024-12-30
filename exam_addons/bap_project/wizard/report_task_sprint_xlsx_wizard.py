from odoo import models, fields, _
from odoo.exceptions import UserError

class ReportTaskSprintXLSXWizard(models.TransientModel):
    _name = 'report.task.sprint.xlsx.wizard'
    _description = 'Report Task Sprint XLSX Wizard'

    date_from = fields.Date(string='Date From', required=True)
    date_to = fields.Date(string='Date To', required=True)
    project_ids = fields.Many2many('bap.project',string='Project', domain=lambda self: self._get_project_domain())

    def _get_project_domain(self):
        user = self.env.user
        if user.has_group('bap_project.group_project_pm'):
            return [('pm_id', '=', user.id)]
        return []

    def action_export_task_sprint_excel(self):
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise UserError('Date From cannot be later than Date To.')

        date_from = self.date_from
        date_to = self.date_to
        project_ids = ','.join(map(str, self.project_ids.ids)) if self.project_ids else ''
        url = f'/report_task_sprint_xlsx?date_from={date_from}&date_to={date_to}&project_ids={project_ids}'
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'self',
        }