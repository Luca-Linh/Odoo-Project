from odoo import models, fields, api
from odoo.exceptions import UserError

class ProjectRequestCancelOpenWizard(models.TransientModel):
    _name = "project.request.cancel.open.wizard"
    _description = "Wizard to Cancel Project Request"

    cancel_reason = fields.Text(string="Cancel Reason", required=True)

    def action_confirm_cancel_open(self):
        # Get the active record (the project request)
        request = self.env['bap.project.request.open'].browse(self.env.context.get('active_id'))
        if not request:
            raise UserError("Request not found.")

        # Ensure the request is in 'submitted' status before cancelling
        if request.status != 'submitted':
            raise UserError("Only submitted requests can be cancelled.")

        # Update the request with the cancel reason
        request.sudo().write({'status': 'cancelled'})
        request.sudo().write({'cancel_reason': self.cancel_reason})
        request.sudo().write({'approved_by': self.env.user})

        # Send the email notification
        self._send_cancel_email(request)

        # Return action to close the wizard
        return {'type': 'ir.actions.act_window_close'}

    def _send_cancel_email(self, request):
        template = self.env.ref('bap_project.email_template_cancel_request_open', raise_if_not_found=True)
        # Pass the necessary values to the template context
        template.send_mail(request.id, force_send=True)