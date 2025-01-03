from email.policy import default

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class BapProjectTask(models.Model):
    _name = 'bap.project.task'
    _description = 'Bap Project Task'

    task_code = fields.Char(
        string='Task Code',
        readonly=True,
        default=lambda self: _('New Task Code')
    )
    task_name = fields.Char(string='Task Name', required=True)
    project_id = fields.Many2one('bap.project', string='Project', required=True)
    sprint_id = fields.Many2one(
        'bap.project.sprint',
        string='Sprint',
        required = True
    )
    dev_id = fields.Many2one('res.users', string='Developer')
    qc_id = fields.Many2one('res.users', string='Quality Controller')
    task_type_id = fields.Many2one('bap.project.task.type', string='Task Type')
    dev_deadline = fields.Date(string='Developer Deadline')
    qc_deadline = fields.Date(string='QC Deadline')
    status = fields.Selection([
        ('new', 'New'),
        ('dev', 'Development'),
        ('qc', 'Quality Control'),
        ('done', 'Done')
    ],
        string='Status',
        default='new',

    )
    description = fields.Text(string='Description', required=True)

    project_code = fields.Char(
        string='Project Code',
        related='project_id.project_code',  # Sử dụng trường liên kết nếu cần lấy từ project
        readonly=True
    )
    is_qc = fields.Boolean(
        compute='_compute_user_permissions',
    )
    is_dev = fields.Boolean(
        compute='_compute_user_permissions',
    )

    @api.model
    def create(self, vals):
        vals['task_code'] = self.env['ir.sequence'].next_by_code('task_sequence_code')
        return super(BapProjectTask, self).create(vals)

    def name_get(self):
        result = []
        for task in self:
            name = task.task_name
            result.append((task.id, name))
        return result

    @api.depends('project_id.dev_ids', 'project_id.qc_ids')
    def _compute_user_permissions(self):
        for task in self:
            current_user = self.env.user
            task.is_dev = (
                    current_user in task.project_id.dev_ids and task.status == 'dev'
            )
            task.is_qc = (
                    current_user in task.project_id.qc_ids and task.status == 'qc'
            )

    @api.model
    def action_update_newest_sprint(self, project_id):
        """Update tasks from closed sprints to the newest open sprint."""
        closed_sprints = self.env['bap.project.sprint'].search([
            ('project_id', '=', project_id),
            ('status', '=', 'close')
        ])

        newest_open_sprint = self.env['bap.project.sprint'].search([
            ('project_id', '=', project_id),
            ('status', '=', 'open')
        ], order='start_date desc', limit=1)

        if not newest_open_sprint:
            return {'error': 'No open sprint found for this project.'}

        tasks_to_update = self.search([
            ('sprint_id', 'in', closed_sprints.ids),
            ('status', '!=', 'done')
        ])

        if not tasks_to_update:
            return {'error': 'No tasks found to update for this project.'}

        tasks_to_update.write({'sprint_id': newest_open_sprint.id})

        # Trả về kết quả thành công
        return {'success': f'{len(tasks_to_update)} tasks updated to the newest open sprint.'}



    @api.constrains('dev_id', 'dev_deadline', 'qc_id', 'qc_deadline')
    def _check_deadlines(self):
        for task in self:
            if task.dev_id and not task.dev_deadline:
                raise ValidationError('Developer Deadline is required if a Developer is assigned.')
            if task.qc_id and not task.qc_deadline:
                raise ValidationError('QC Deadline is required if a Quality Controller is assigned.')

    def action_submit_to_qc(self):
        """Dev submits task to QC."""
        if self.status != 'dev':
            raise UserError(_("You can only submit tasks in Development status."))

        self.write({'status': 'qc'})

        # Send email to QC
        template = self.env.ref('bap_project.email_template_done_task_to_qc')
        if template:
            template.sudo().send_mail(self.id, force_send=True)

    def action_qc_test_done(self):
        """QC confirms task is done."""
        if self.status != 'qc':
            raise UserError(_("Only tasks in Quality Control status can be marked as Done."))

        self.write({'status': 'done'})

        # Send email to PM
        template = self.env.ref('bap_project.email_template_done_task_to_pm')
        if template:
            template.sudo().send_mail(self.id, force_send=True)

    def action_qc_return_to_dev(self):
        """QC returns task to Developer."""
        if self.status != 'qc':
            raise UserError(_("Only tasks in Quality Control can be returned to Development."))

        self.write({'status': 'dev'})

        # Send email to Developer
        template = self.env.ref('bap_project.email_template_return_task_to_dev')
        if template:
            template.sudo().send_mail(self.id, force_send=True)

