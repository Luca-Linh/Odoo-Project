from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class BapProjectSprint(models.Model):
    _name = 'bap.project.sprint'
    _description = 'Bap Project Sprint'

    sprint_code = fields.Char(
        string='Sprint Code',
        readonly=True,
        default=lambda self: _('New Sprint Code')
    )
    sprint_name = fields.Char(string='Sprint Name', required=True)
    project_id = fields.Many2one('bap.project', string='Project', required=True, domain=lambda self: self._get_project_domain())
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    status = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('close', 'Closed')
    ],
        string='Status',
        default='draft',
        required=True
    )
    task_ids = fields.One2many('bap.project.task', 'sprint_id', string='Tasks')
    def name_get(self):
        result = []
        for sprint in self:
            name = sprint.sprint_name
            result.append((sprint.id, name))
        return result

    def _get_project_domain(self):
        user = self.env.user
        if user.has_group('bap_project.group_project_pm'):
            return [('pm_id', '=', user.id)]
        return []

    @api.model
    def create(self, vals):
        vals['sprint_code'] = self.env['ir.sequence'].next_by_code('sprint_sequence_code')
        return super(BapProjectSprint, self).create(vals)

    @api.constrains('start_date', 'end_date', 'project_id')
    def _check_date_overlap(self):
        """Ensure no overlapping sprints for the same project."""
        for sprint in self:
            if sprint.start_date and sprint.end_date:
                overlapping_sprints = self.search([
                    ('id', '!=', sprint.id),
                    ('project_id', '=', sprint.project_id.id),
                    ('start_date', '<=', sprint.end_date),
                    ('end_date', '>=', sprint.start_date),
                ])
                if overlapping_sprints:
                    raise ValidationError(
                        "The sprint dates overlap with another sprint in the same project."
                    )

    @api.constrains('status', 'project_id')
    def _check_single_open_sprint(self):
        """Ensure only one sprint is open at a time for the same project."""
        for sprint in self:
            if sprint.status == 'open':
                open_sprints = self.search([
                    ('id', '!=', sprint.id),
                    ('project_id', '=', sprint.project_id.id),
                    ('status', '=', 'open'),
                ])
                if open_sprints:
                    raise ValidationError(
                        "Only one sprint can be open at a time for the same project."
                    )