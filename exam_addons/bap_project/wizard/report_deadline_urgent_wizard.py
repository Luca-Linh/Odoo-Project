from odoo import models, fields

class ReportDeadlineUrgentWizard(models.TransientModel):
    _name = 'report.deadline.urgent.wizard'
    _description = 'Report Deadline Urgent Wizard'

    project_ids = fields.Many2many('bap.project',string='Project', domain=lambda self: self._get_project_domain())

    def _get_project_domain(self):
        user = self.env.user
        if user.has_group('bap_project.group_project_pm'):
            return [('pm_id', '=', user.id)]
        return []

    def action_export_excel(self):
        project_ids = ','.join(map(str, self.project_ids.ids)) if self.project_ids else ''
        url = f'/report_deadline_urgent_xlsx?project_ids={project_ids}'
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'self',
        }