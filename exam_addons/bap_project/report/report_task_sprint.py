from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ReportTaskSprint(models.Model):
    _name = 'report.task.sprint'
    _description = 'Project Task Sprint Report'
    _auto = False

    member_id = fields.Many2one('res.users', string='Member', readonly=True)
    member_name = fields.Char(string='Member Name', readonly=True)
    project_id = fields.Many2one('bap.project', string='Project', readonly=True)
    project_name = fields.Many2one('bap.project', string='Project Name', readonly=True)
    sprint_id = fields.Many2one('bap.project.sprint', string='Sprint', readonly=True)
    sprint_name = fields.Many2one('bap.project.sprint', string='Sprint Name', readonly=True)
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

    def show_tasks_based_on_field(self, field_name, record_id):
        # Tạo domain cho các task cần hiển thị
        domain = [('project_id', '=', self.project_id.id), ('sprint_id', '=', self.sprint_id.id)]

        if field_name == 'total_task_count':
            return self._get_task_popup_view(domain)
        elif field_name == 'task_new_count':
            return self._get_task_popup_view(domain + [('status', '=', 'new')])
        elif field_name == 'task_dev_count':
            return self._get_task_popup_view(domain + [('status', '=', 'dev')])
        elif field_name == 'task_qc_count':
            return self._get_task_popup_view(domain + [('status', '=', 'qc')])
        elif field_name == 'task_done_count':
            return self._get_task_popup_view(domain + [('status', '=', 'done')])
        else:
            return {}

    def _get_task_popup_view(self, domain):
        """Trả về action để mở view task dưới dạng popup."""
        tasks = self.env['bap.project.task'].search(domain)
        print(tasks)
        action = {
            'type': 'ir.actions.act_window',
            'name': _('Tasks'),
            'res_model': 'bap.project.task',
            'view_mode': 'tree,form',
            'target': 'new',  # Mở popup
            'domain': [('id', 'in', tasks.ids)],
        }
        return {'action': action}

    # def show_all_tasks(self):
    #     return self._get_task_popup_view([])
    #
    # def show_new_tasks(self):
    #     return self._get_task_popup_view([('status', '=', 'new')])
    #
    # def show_dev_tasks(self):
    #     return self._get_task_popup_view([('status', '=', 'dev')])
    #
    # def show_qc_tasks(self):
    #     return self._get_task_popup_view([('status', '=', 'qc')])
    #
    # def show_done_tasks(self):
    #     return self._get_task_popup_view([('status', '=', 'done')])
    #
    # def _get_task_popup_view(self, additional_domain):
    #     """Trả về danh sách nhiệm vụ dưới dạng popup."""
    #     domain = [
    #         ('project_id', '=', self.project_id.id),
    #         ('sprint_id', '=', self.sprint_id.id),
    #         ('member_id', '=', self.member_id.id),
    #     ] + additional_domain
    #
    #     return {
    #         'name': _('Tasks'),
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'bap.project.task',
    #         'view_mode': 'tree',
    #         'target': 'new',  # Hiển thị dưới dạng popup
    #         'domain': domain,
    #     }