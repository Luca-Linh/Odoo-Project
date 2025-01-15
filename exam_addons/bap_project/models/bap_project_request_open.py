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
        if not self.env.user.has_group('bap_project.group_project_admin'):

            if vals.get('pm_id') and vals['pm_id'] != self.env.user.id:
                raise UserError("The Project Manager must be yourself.")

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
            record.env['bap.project'].create({
                'project_name': record.project_name,
                'pm_id': record.pm_id.id,
                'dev_ids': [(6, 0, record.dev_ids.ids)],
                'qc_ids': [(6, 0, record.qc_ids.ids)],
                'start_date': record.start_date,
                'description': record.description,
                'status': 'open',
                'request_id': record.id,
            })
            # Update the status of the records to 'approved'
        self.sudo().write({'status': 'approved'})

    def action_refuse_all(self):
        for record in self:
            if record.status != 'submitted':
                raise UserError(_("Only records with status 'Submitted' can be refused."))
        self.write({
            'status': 'cancelled',
            'cancel_reason': 'cancelled all',
            'approved_by':  self.env.user
        })

    def action_submit(self):
        if self.status == 'draft':
            self.write({'status': 'submitted'})

    def action_approve(self):
        if self.status != 'submitted':
            raise ValidationError(_("Only requests in 'Submitted' status can be approved."))
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
        self.env['bap.project'].create(project_vals)

        self.write({'status':'approved','approved_by': self.env.user})


    def action_open_cancel_wizard(self):
        return {
            'name': 'Cancel Project Request',
            'type': 'ir.actions.act_window',
            'res_model': 'project.request.cancel.open.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_request_id': self.id}
        }