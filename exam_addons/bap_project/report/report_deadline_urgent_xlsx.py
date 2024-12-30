import io
import xlsxwriter
from odoo import models
from odoo.exceptions import UserError

class ReportDeadlineUrgentXLSX(models.AbstractModel):
    _name = 'report.bap_project.report_deadline_urgent_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = "Report Deadline Urgent XLSX"

    def generate_xlsx_report(self, data):
        # Tạo file trong bộ nhớ cho báo cáo
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        project_ids = data.get('project_ids', [])

        # Thêm worksheet và định dạng
        worksheet = workbook.add_worksheet('Deadline Report')
        title_format = workbook.add_format({'bold': True, 'align': 'center', 'font_size': 14, 'bg_color': '#DDEBF7'})
        header_format = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': '#4F81BD', 'font_color': 'white'})
        date_format = workbook.add_format({'num_format': 'dd/mm/yyyy', 'align': 'center'})
        # Set tiêu đề và độ rộng cột
        worksheet.merge_range('A1:H1', 'Task Deadline Report', title_format)
        worksheet.set_column('A:H', 20)

        # Tiêu đề các cột
        headers = [
            'Task Code', 'Task Name', 'Project', 'Dev Member',
            'QC Member', 'Dev Deadline', 'QC Deadline' ,'Status'
        ]
        for col, header in enumerate(headers):
            worksheet.write(2, col, header, header_format)

        # Xây dựng câu truy vấn SQL
        query = """
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
                (t.dev_deadline >= CURRENT_DATE - INTERVAL '2 days'
                 OR t.qc_deadline >= CURRENT_DATE - INTERVAL '2 days')
        """

        params = []
        if project_ids:
            query += " AND t.project_id IN %s"
            params.append(tuple(project_ids))

        # Thực thi câu truy vấn
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