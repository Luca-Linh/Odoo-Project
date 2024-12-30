from odoo import models, fields, api


class ReportDeadlineUrgent(models.Model):
    _name = 'report.deadline.urgent'
    _description = 'Report Deadline Urgent'
    _auto = False

    task_code = fields.Char(string='Task Code')
    task_name = fields.Char(string='Task Name')
    project_id = fields.Many2one('bap.project', string='Project')
    dev_member = fields.Char(string='Dev Member')
    qc_member = fields.Char(string='QC Member')
    dev_deadline = fields.Date(string='Dev Deadline')
    qc_deadline = fields.Date(string='QC Deadline')
    status = fields.Selection([
        ('new', 'New'),
        ('dev', 'Development'),
        ('qc', 'Quality Control'),
        ('done', 'Done')
    ], string='Status')

    def init(self):
        self._cr.execute("DROP VIEW IF EXISTS report_deadline_urgent")

        self.env.cr.execute("""
            CREATE OR REPLACE VIEW report_deadline_urgent AS (
                SELECT
                    t.id AS id,
                    t.task_code AS task_code,
                    t.task_name AS task_name,
                    t.project_id AS project_id,
                    rp1.name AS dev_member,  
                    rp2.name AS qc_member,
                    t.dev_deadline AS dev_deadline,
                    t.qc_deadline AS qc_deadline,
                    t.status AS status
                FROM
                    bap_project_task t
                JOIN
                    bap_project p ON t.project_id = p.id
                LEFT JOIN
                    res_users u1 ON t.dev_id = u1.id
                LEFT JOIN
                    res_partner rp1 ON u1.partner_id = rp1.id
                LEFT JOIN
                    res_users u2 ON t.qc_id = u2.id
                LEFT JOIN
                    res_partner rp2 ON u2.partner_id = rp2.id
                WHERE
                    t.dev_deadline >= CURRENT_DATE - 2
                    OR t.qc_deadline >= CURRENT_DATE - 2
            )
        """)

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        user = self.env.user
        if user.has_group('bap_project.group_project_pm'):
            args += [('project_id.pm_id', '=', user.id)]
        return super(ReportDeadlineUrgent, self).search(args, offset, limit, order, count)
