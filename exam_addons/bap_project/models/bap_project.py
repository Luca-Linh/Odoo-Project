from lxml import etree

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, _logger


class BapProject(models.Model):
    _name = "bap.project"
    _description = "Bap Project"

    project_code = fields.Char(
        string="Project Code",
        readonly=True,
        copy=False,
        default=lambda self: _('New Project Code')
    )
    project_name = fields.Char(string='Project Name', required=True, unique=True)
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date')
    status = fields.Selection([
        ('open', 'Open'),
        ('close', 'Closed')
    ],
        string='Status',
        required=True
    )
    pm_id = fields.Many2one('res.users', string='Project Manager', required=True)
    dev_ids = fields.Many2many(
        'res.users',
        'bap_project_dev_rel',
        'project_id',
        'user_id',
        string='Dev Team',
        required = True
    )

    qc_ids = fields.Many2many(
        'res.users',
        'bap_project_qc_rel',
        'project_id',
        'user_id',
        string='QC Team',
        required=True
    )
    description = fields.Text(string='Description', required=True)

    sprint_ids = fields.One2many('bap.project.sprint', 'project_id', string='Sprint')
    task_ids = fields.One2many('bap.project.task', 'project_id', string='Tasks')
    task_count = fields.Integer(
        compute="_compute_bap_task_count"
    )
    request_id = fields.Many2one('bap.project.request.open', string='Request', readonly=True)

    def name_get(self):
        result = []
        for project in self:
            name = project.project_name
            result.append((project.id, name))
        return result

    @api.depends('task_ids')
    def _compute_bap_task_count(self):
        for project in self:
            project.task_count = len(project.task_ids)


    @api.model
    def create(self, vals):
        vals['project_code'] = self.env['ir.sequence'].next_by_code('project_sequence_code')
        bap_project = super(BapProject, self).create(vals)

        request_id = vals.get('request_id')  # Giả định bạn truyền request_id vào project_vals
        if request_id:
            request = self.env['bap.project.request.open'].browse(request_id)
            template = self.env.ref('bap_project.email_template_accept_request_open')
            if template:
                template.send_mail(request.id, force_send=True)
        # Gửi email thông báo cho các thành viên tham gia dự án
        email_list = []
        if bap_project.pm_id.email:
            email_list.append(bap_project.pm_id.email)
        email_list += [dev.email for dev in bap_project.dev_ids if dev.email]
        email_list += [qc.email for qc in bap_project.qc_ids if qc.email]

        if email_list:
            self._send_project_notification(bap_project, email_list)

        return bap_project

    def _send_project_notification(self, bap_project, email_list):
        _logger.info(f"Sending email to: {email_list}")  # Log danh sách email để kiểm tra
        template = self.env.ref('bap_project.email_template_project_created')

        if template and email_list:
            template.write({
                'email_to': ','.join(email_list)
            })
            template.send_mail(bap_project.id, force_send=True)

    @api.constrains('start_date', 'end_date')
    def _check_start_end_date(self):
        """Ensure end date is greater than or equal to start date."""
        for project in self:
            if project.end_date and project.end_date < project.start_date:
                raise ValidationError(
                    _('The End Date (%s) cannot be earlier than the Start Date (%s).') %
                    (project.end_date, project.start_date)
                )

    @api.constrains('project_name')
    def _check_unique_project_name(self):
        """Ensure project name is unique (case insensitive)."""
        for project in self:
            duplicate_project = self.search([
                ('id', '!=', project.id),
                ('project_name', 'ilike', project.project_name)
            ])
            if duplicate_project:
                raise ValidationError(
                    _('The Project Name "%s" must be unique (case insensitive).') %
                    project.project_name
                )

    def action_view_task_project(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Task',
            'res_model': 'bap.project.task',
            'view_mode': 'tree,form',
            'domain': [('project_id', '=', self.id)],
            'context': {
                'default_project_id': self.id,
                'stat_button_view': True,
            },
            'target': 'current',
        }

    def action_view_project(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Project Form',
            'res_model': 'bap.project',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'current',
        }


