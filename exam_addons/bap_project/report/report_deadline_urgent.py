from odoo import models, fields, api


class ReportDeadlineUrgent(models.Model):
    _name = 'report.deadline.urgent'
    _description = 'Report Deadline Urgent'
    _auto = False

    task_code = fields.Char(string='Task Code')
    task_name = fields.Char(string='Task Name')
    project_id = fields.Many2one('bap.project', string='Project')
    project_name = fields.Many2one('bap.project', string='Project Name', readonly=True)
    pm_id = fields.Many2one('res.users', string="Project Manager")
    member = fields.Char(string='Member')
    deadline = fields.Date(string='Deadline')
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
                SELECT DISTINCT
                    row_number() OVER () AS id,
                    t.task_code AS task_code,
                    t.task_name AS task_name,
                    p.pm_id AS pm_id,
                    t.project_id AS project_id,
                    rp1.name AS member, -- Dev Member
                    t.dev_deadline AS deadline,
                    t.status AS status
                FROM
                    bap_project_task t
                JOIN
                    bap_project p ON t.project_id = p.id
                LEFT JOIN
                    res_users u1 ON t.dev_id = u1.id
                LEFT JOIN
                    res_partner rp1 ON u1.partner_id = rp1.id
                WHERE
                    t.dev_deadline BETWEEN CURRENT_DATE AND CURRENT_DATE + 2
                UNION ALL
                SELECT DISTINCT
                    row_number() OVER () + 100000 AS id,
                    t.task_code AS task_code,
                    t.task_name AS task_name,
                    p.pm_id AS pm_id,
                    t.project_id AS project_id,
                    rp2.name AS member, -- QC Member
                    t.qc_deadline AS deadline,
                    t.status AS status
                FROM
                    bap_project_task t
                JOIN
                    bap_project p ON t.project_id = p.id
                LEFT JOIN
                    res_users u2 ON t.qc_id = u2.id
                LEFT JOIN
                    res_partner rp2 ON u2.partner_id = rp2.id
                WHERE
                    t.qc_deadline BETWEEN CURRENT_DATE AND CURRENT_DATE + 2
            )
        """)

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        print('sfdjfnsj',args)
        user = self.env.user
        if user.has_group('bap_project.group_project_pm'):
            args += [('pm_id', '=', user.id)]
        return super(ReportDeadlineUrgent, self).search(args, offset, limit, order, count)
