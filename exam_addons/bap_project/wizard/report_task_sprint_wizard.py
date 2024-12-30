from odoo import models, fields, _
from odoo.exceptions import UserError


class ReportTaskSprintWizard(models.TransientModel):
    _name = 'report.task.sprint.wizard'
    _description = 'Report Task Sprint Wizard'

    date_from = fields.Date(string='Date From', required=True)
    date_to = fields.Date(string='Date To', required=True)
    project_ids = fields.Many2many('bap.project',string='Project', domain=lambda self: self._get_project_domain())

    def _get_project_domain(self):
        user = self.env.user
        if user.has_group('bap_project.group_project_pm'):
            return [('pm_id', '=', user.id)]
        return []

    def action_generate_report(self):
        self.ensure_one()

        # Ensure required fields are valid
        if not self.date_from or not self.date_to:
            raise UserError(_("You must enter both 'Date From' and 'Date To'."))

        if self.date_from > self.date_to:
            raise UserError(_("The 'Date From' must be before or equal to 'Date To'."))

        # Get projects based on user input or permissions
        project_ids = self.project_ids or self._get_default_projects()
        if not project_ids:
            raise UserError(_("No projects available for the selected criteria."))

        # Build the domain to filter the report by projects
        report_data = self.generate_report_data(project_ids)

        return {
            'name': _('Task Sprint Report'),
            'type': 'ir.actions.act_window',
            'res_model': 'report.task.sprint',
            'view_mode': 'tree',
            'target': 'current',
            'context': {
                'default_report_data': report_data,
            },
        }

    def generate_report_data(self, project_ids):
        # Xóa view nếu tồn tại
        self._cr.execute("DROP VIEW IF EXISTS report_task_sprint")

        # Truy vấn SQL để tạo view
        query = """
            CREATE OR REPLACE VIEW report_task_sprint AS (
                SELECT
                    ROW_NUMBER() OVER() AS id,
                    pt.project_id,
                    pt.sprint_id,
                    COALESCE(pt.dev_id, pt.qc_id) AS member_id,
                    CASE
                        WHEN pt.dev_id IS NOT NULL THEN 'dev'
                        WHEN pt.qc_id IS NOT NULL THEN 'qc'
                    END AS role,
                    COUNT(pt.id) AS total_task_count,
                    SUM(CASE WHEN pt.status = 'new' THEN 1 ELSE 0 END) AS task_new_count,
                    SUM(CASE WHEN pt.status = 'dev' THEN 1 ELSE 0 END) AS task_dev_count,
                    SUM(CASE WHEN pt.status = 'qc' THEN 1 ELSE 0 END) AS task_qc_count,
                    SUM(CASE WHEN pt.status = 'done' THEN 1 ELSE 0 END) AS task_done_count,
                    ps.start_date AS sprint_start_date,
                    ps.end_date AS sprint_end_date
                FROM
                    bap_project_task pt
                LEFT JOIN res_users ru_dev ON ru_dev.id = pt.dev_id
                LEFT JOIN res_partner rp_dev ON rp_dev.id = ru_dev.partner_id
                LEFT JOIN res_users ru_qc ON ru_qc.id = pt.qc_id
                LEFT JOIN res_partner rp_qc ON rp_qc.id = ru_qc.partner_id
                LEFT JOIN bap_project_sprint ps ON ps.id = pt.sprint_id
                WHERE COALESCE(pt.dev_id, pt.qc_id) IS NOT NULL
                  AND ps.start_date >= %s
                  AND ps.end_date <= %s
        """
        params = [self.date_from, self.date_to]

        # Sử dụng project_ids.ids để lấy danh sách ID của các project
        if project_ids:
            query += " AND pt.project_id IN %s"
            params.append(tuple(project_ids.ids))  # Dùng tuple để truyền danh sách ID vào query

        query += """
                GROUP BY
                    pt.project_id, pt.sprint_id, COALESCE(pt.dev_id, pt.qc_id),
                    COALESCE(rp_dev.name, rp_qc.name), ps.start_date, ps.end_date,
                    pt.dev_id, pt.qc_id
            )
        """

        # Thực thi truy vấn SQL
        try:
            self.env.cr.execute(query, params)
        except Exception as e:
            raise UserError(f"An error occurred while creating the report: {str(e)}")

        # Truy vấn dữ liệu từ view
        self._cr.execute("SELECT * FROM report_task_sprint")
        result = self._cr.fetchall()

        # Bạn có thể trả về dữ liệu ở đây, hoặc xử lý thêm nếu cần
        return result

    def _get_default_projects(self):
        domain = self._get_project_domain()
        return self.env['bap.project'].search(domain)
