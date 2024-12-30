import io
import xlsxwriter
from odoo import models
from odoo.exceptions import UserError

class ReportTaskSprintXLSX(models.AbstractModel):
    _name = 'report.bap_project.report_task_sprint_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = "Report Task Sprint XLSX"

    def generate_xlsx_report_task_in_sprint(self, data):
        # Tạo file trong bộ nhớ cho báo cáo
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        project_ids = data.get('project_ids', [])
        date_from = data.get('date_from')
        date_to = data.get('date_to')

        # Thêm worksheet và định dạng
        worksheet = workbook.add_worksheet('Report Task Sprint')
        title_format = workbook.add_format({'bold': True, 'align': 'center', 'font_size': 14, 'bg_color': '#DDEBF7'})
        header_format = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': '#4F81BD', 'font_color': 'white'})
        date_format = workbook.add_format({'num_format': 'dd/mm/yyyy', 'align': 'center'})  # Định dạng ngày

        # Set tiêu đề và độ rộng cột
        worksheet.merge_range('A1:H1', 'Task Deadline Report', title_format)
        worksheet.set_column('A:N', 30)

        # Tiêu đề các cột
        headers = [
            'Member', 'Member Name', 'Project ID', 'Project Name', 'Sprint ID', 'Sprint Name',
            'Role', 'Total Tasks', 'New Tasks', 'Development Tasks',
            'Quality Control Tasks', 'Done Tasks', 'Sprint Start Date',
            'Sprint End Date'
        ]
        for col, header in enumerate(headers):
            worksheet.write(2, col, header, header_format)

        # Xây dựng câu truy vấn SQL
        query = """
                SELECT
                    pt.project_id,
                    p.project_name AS project_name,
                    pt.sprint_id,
                    ps.sprint_name AS sprint_name,
                    COALESCE(pt.dev_id, pt.qc_id) AS member_id,
                    COALESCE(rp_dev.name, rp_qc.name) AS member_name,
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
                LEFT JOIN bap_project p ON p.id = pt.project_id
                LEFT JOIN res_users ru_dev ON ru_dev.id = pt.dev_id
                LEFT JOIN res_partner rp_dev ON rp_dev.id = ru_dev.partner_id
                LEFT JOIN res_users ru_qc ON ru_qc.id = pt.qc_id
                LEFT JOIN res_partner rp_qc ON rp_qc.id = ru_qc.partner_id
                LEFT JOIN bap_project_sprint ps ON ps.id = pt.sprint_id
                WHERE COALESCE(pt.dev_id, pt.qc_id) IS NOT NULL
                  AND ps.start_date >= %s
                  AND ps.end_date <= %s
        """
        params = [date_from, date_to]

        if project_ids:
            query += " AND pt.project_id IN %s"
            params.append(tuple(project_ids))

        query += """
                GROUP BY
                    pt.project_id, p.project_name, pt.sprint_id, ps.sprint_name, COALESCE(pt.dev_id, pt.qc_id),
                    COALESCE(rp_dev.name, rp_qc.name), ps.start_date, ps.end_date,
                    pt.dev_id, pt.qc_id
        """

        # Thực thi truy vấn SQL
        try:
            self.env.cr.execute(query, params)
            results = self.env.cr.fetchall()
        except Exception as e:
            raise UserError(f"An error occurred while fetching data: {str(e)}")

        # Populate các dòng dữ liệu vào báo cáo
        row = 3
        for report in results:
            for col, value in enumerate(report):
                # Áp dụng định dạng cho các cột ngày tháng
                if col in [12, 13]:  # Cột Sprint Start Date và Sprint End Date
                    worksheet.write_datetime(row, col, value, date_format)
                else:
                    worksheet.write(row, col, value)
            row += 1

        # Đóng workbook và trả về dữ liệu
        workbook.close()
        output.seek(0)
        return output.getvalue()
