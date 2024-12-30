from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class BapProjectRequestOpen(models.Model):
    _name = 'bap.project.request.open'
    _description = 'Bap Project Request Open'

    rq_open_code = fields.Char(
        string='Request Code',
        readonly=True,
        default=lambda self: _('New Request Open Project Code')
    )
    project_name = fields.Char(string='Project Name', required=True)
    pm_id = fields.Many2one('res.users', string='Project Manager', required=True)
    dev_ids = fields.Many2many(
        'res.users',
        'bap_project_request_dev_rel',
        'project_id',
        'user_id',
        string='Dev Team',
        required=True
    )

    qc_ids = fields.Many2many(
        'res.users',
        'bap_project_request_qc_rel',
        'project_id',
        'user_id',
        string='QC Team',
        required=True
    )
    start_date = fields.Date(string='Start Date', required=True)
    description = fields.Text(string='Description', required=True)
    status = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('cancelled', 'Cancelled')
    ],
        string='Status',
        default='draft',
    )
    cancel_reason = fields.Text(string='Cancel Reason', readonly=True)
    project_code = fields.Char(string="Project Code")

    created_by = fields.Many2one('res.users', string='Created By', default=lambda self: self.env.user)
    approved_by = fields.Many2one('res.users', string='Approved By', readonly=True)

    @api.model
    def create(self, vals):
        vals['rq_open_code'] = self.env['ir.sequence'].next_by_code('open_sequence_code')
        return super(BapProjectRequestOpen, self).create(vals)

    def name_get(self):
        result = []
        for re_open in self:
            name = re_open.project_name
            result.append((re_open.id, name))
        return result

    def action_approve_all(self):
        for record in self:
            if record.status != 'submitted':
                raise UserError(_("Only records with status 'Submitted' can be approved."))
        self.sudo().write({'status': 'approved'})

    def action_refuse_all(self):
        for record in self:
            if record.status != 'submitted':
                raise UserError(_("Only records with status 'Submitted' can be refused."))
        self.sudo().write({'status': 'cancelled'})

    def action_submit(self):
        """Send request for approval."""
        if self.status == 'draft':
            self.sudo().write({'status': 'submitted'})

    def action_approve(self):
        """Approve the request and create the project."""
        if self.status != 'submitted':
            raise ValidationError(_("Only requests in 'Submitted' status can be approved."))

        # Tạo dự án
        project_vals = {
            'project_name': self.project_name,
            'pm_id': self.pm_id.id,
            'dev_ids': [(6, 0, self.dev_ids.ids)],
            'qc_ids': [(6, 0, self.qc_ids.ids)],
            'start_date': self.start_date,
            'description': self.description,
            'status': 'open',
            'request_id': self.id,
        }
        self.env['bap.project'].sudo().create(project_vals)

        self.sudo().write({'status':'approved','approved_by': self.env.user})


    def action_open_cancel_wizard(self):
        return {
            'name': 'Cancel Project Request',
            'type': 'ir.actions.act_window',
            'res_model': 'project.request.cancel.open.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_request_id': self.id}
        }