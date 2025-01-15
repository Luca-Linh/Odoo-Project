from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class BapProjectRequestClose(models.Model):
    _name = 'bap.project.request.close'
    _description = 'Bap Project Request Close'

    rq_close_code = fields.Char(
        string='Request Code',
        required=True,
        readonly=True,
        default=lambda self: _('New Request Close Project Code')
    )
    project_id = fields.Many2one('bap.project', string='Project', required=True, domain=lambda self: self._get_project_domain())
    pm_id = fields.Many2one('res.users', string='Project Manager', required=True)
    end_date = fields.Date(string='End Date',required=True)
    close_reason = fields.Text(string='Close Reason', required=True)
    status = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('cancelled', 'Cancelled')
    ],
        string='Status',
        default='draft'
    )
    cancel_reason = fields.Text(string='Cancel Reason', readonly=True)
    project_code = fields.Char(
        string='Project Code',
        related='project_id.project_code',  # Sử dụng trường liên kết nếu cần lấy từ project
        readonly=True
    )
    created_by = fields.Many2one('res.users', string='Created By', default=lambda self: self.env.user)
    approved_by = fields.Many2one('res.users', string='Approved By', readonly=True)

    def name_get(self):
        result = []
        for re_close in self:
            name = re_close.project_id.project_name
            result.append((re_close.id, name))
        return result

    def _get_project_domain(self):
        user = self.env.user
        if user.has_group('bap_project.group_project_pm'):
            return [('pm_id', '=', user.id)]
        return []

    @api.onchange('project_id')
    def _onchange_project_id(self):
        """When the project is selected, update the Project Manager (pm_id)."""
        if self.project_id:
            self.pm_id = self.project_id.pm_id

    @api.constrains('project_id')
    def _check_all_sprints_closed(self):
        """Constraint: Kiểm tra tất cả các sprint của dự án đã đóng."""
        for record in self:
            if record.project_id:
                open_sprints = record.project_id.sprint_ids.filtered(lambda sprint: sprint.status != 'close')
                if open_sprints:
                    raise ValidationError(
                        _('Cannot create a close request for project "%s" because the following sprints are not closed: %s') %
                        (record.project_id.project_name, ', '.join(open_sprints.mapped('sprint_name')))
                    )

    @api.constrains('project_id')
    def _check_all_tasks_done(self):
        """Constraint: Kiểm tra tất cả các task của dự án đã hoàn thành."""
        for record in self:
            if record.project_id:
                incomplete_tasks = record.project_id.task_ids.filtered(lambda task: task.status != 'done')
                if incomplete_tasks:
                    raise ValidationError(
                        _('Cannot create a close request for project "%s" because the following tasks are not done: %s') %
                        (record.project_id.project_name, ', '.join(incomplete_tasks.mapped('task_name')))
                    )


    @api.model
    def create(self, vals):
        if not self.env.user.has_group('bap_project.group_project_admin'):
            # If pm_id is provided and does not match the logged-in user, raise an error
            if vals.get('pm_id') and vals['pm_id'] != self.env.user.id:
                raise UserError("The Project Manager must be yourself.")
        vals['rq_close_code'] = self.env['ir.sequence'].next_by_code('close_sequence_code')
        return super(BapProjectRequestClose, self).create(vals)

    def action_approve_all(self):
        for record in self:
            if record.status != 'submitted':
                raise UserError(_("Only records with status 'Submitted' can be approved."))
            record.project_id.write({
                'end_date': record.end_date,
                'status': 'close',  # Giả sử dự án có trạng thái closed
            })
        self.write({
            'status': 'approved',
            'approved_by': self.env.user
        })

    def action_refuse_all(self):
        for record in self:
            if record.status != 'submitted':
                raise UserError(_("Only records with status 'Submitted' can be refused."))
        self.write({
            'status': 'cancelled',
            'cancel_reason': 'cancelled all',
            'approved_by': self.env.user
        })

    def action_submit(self):
        """Send request for approval."""
        if self.status == 'draft':
            self.write({'status': 'submitted'})

    def action_approve(self):
        """Approve the request and create the project."""
        for record in self:
            if record.status != 'submitted':
                raise UserError(_("Only submitted requests can be approved."))

            # Update Project Status and End Date
            if not record.project_id:
                raise UserError(_("The related project does not exist."))

            record.project_id.sudo().write({
                'end_date': record.end_date,
                'status': 'close',  # Giả sử dự án có trạng thái closed
            })

        self.write({'status':'approved'})
        self.write({'approved_by': self.env.user})

        # Gửi email
        template = self.env.ref('bap_project.email_template_accept_request_close')
        if template:
            template.send_mail(self.id, force_send=True)

    def action_close_cancel_wizard(self):
        return {
            'name': 'Cancel Close Project Request',
            'type': 'ir.actions.act_window',
            'res_model': 'project.request.cancel.close.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_request_id': self.id}
        }