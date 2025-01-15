from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ReportTaskSprint(models.Model):
    _name = 'report.task.sprint'
    _description = 'Project Task Sprint Report'
    _auto = False

    member_id = fields.Many2one('res.users', string='Member', readonly=True)
    member_name = fields.Char(string='Member Name', readonly=True)
    project_id = fields.Many2one('bap.project', string='Project', readonly=True)
    project_name = fields.Char(string='Project Name', readonly=True)
    sprint_id = fields.Many2one('bap.project.sprint', string='Sprint', readonly=True)
    sprint_name = fields.Char(string='Project Name', readonly=True)
    role = fields.Selection([('dev', 'Developer'), ('qc', 'Quality Controller')], string='Role', readonly=True)
    total_task_count = fields.Integer(string='Total Tasks', readonly=True)
    task_new_count = fields.Integer(string='New Tasks', readonly=True)
    task_dev_count = fields.Integer(string='Development Tasks', readonly=True)
    task_qc_count = fields.Integer(string='Quality Control Tasks', readonly=True)
    task_done_count = fields.Integer(string='Done Tasks', readonly=True)
    sprint_start_date = fields.Date(string='Sprint Start Date', readonly=True)
    sprint_end_date = fields.Date(string='Sprint End Date', readonly=True)

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        user = self.env.user
        if user.has_group('bap_project.group_project_pm'):
            args += [('project_id.pm_id', '=', user.id)]
        return super(ReportTaskSprint, self).search(args, offset, limit, order, count)

    def action_view_total_tasks(self):
        """Hiển thị tất cả các task liên quan đến báo cáo này."""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Total Tasks',
            'view_mode': 'tree',
            'res_model': 'bap.project.task',
            'domain': [
                ('project_id', '=', self.project_id.id),
                ('sprint_id', '=', self.sprint_id.id),
                ('member_id', '=', self.member_id.id),
            ],
            'context': dict(self.env.context),
            'target': 'new',
        }

    def action_view_new_tasks(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'New Tasks',
            'view_mode': 'tree',
            'res_model': 'bap.project.task',
            'domain': [('project_id', '=', self.project_id.id),
                       ('sprint_id', '=', self.sprint_id.id),
                       ('member_id', '=', self.member_id.id),
                       ('status', '=', 'new')],
            'context': dict(self.env.context),
            'target': 'new',
        }

    def action_view_dev_tasks(self):
        """Show development tasks related to the current project."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Dev Tasks',
            'view_mode': 'tree',
            'res_model': 'bap.project.task',
            'domain': [('project_id', '=', self.project_id.id),
                       ('sprint_id', '=', self.sprint_id.id),
                       ('member_id', '=', self.dev_ids.id),
                       ('status', '=', 'dev')],
            'context': dict(self.env.context),
            'target':'new',
        }

    def action_view_qc_tasks(self):
        """Show quality control tasks related to the current project."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'QC Tasks',
            'view_mode': 'tree',
            'res_model': 'bap.project.task',
            'domain': [('project_id', '=', self.project_id.id),
                       ('sprint_id', '=', self.sprint_id.id),
                       ('member_id', '=', self.member_id.id),
                       ('status', '=', 'qc')],
            'context': dict(self.env.context),
            'target': 'new',
        }

    def action_view_done_tasks(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Done Tasks',
            'view_mode': 'tree',
            'res_model': 'bap.project.task',
            'domain': [('project_id', '=', self.project_id.id),
                       ('sprint_id', '=', self.sprint_id.id),
                       ('member_id', '=', self.member_id.id),
                       ('status', '=', 'done')],
            'context': dict(self.env.context),
            'target': 'new',
        }
