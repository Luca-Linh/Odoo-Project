import io
import xlsxwriter
from odoo import models
from odoo.exceptions import UserError

class ReportDeadlineUrgentXLSX(models.AbstractModel):
    _name = 'report.bap_project.report_deadline_urgent_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = "Report Deadline Urgent XLSX"

    def generate_urgent_xlsx_report(self, data):
        # Tạo file trong bộ nhớ cho báo cáo
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        project_ids = data.get('project_ids')
        print(project_ids)
        if not project_ids:
            raise UserError("Project IDs must not be empty.")


        # Thêm worksheet và định dạng
        worksheet = workbook.add_worksheet('Deadline Report')
        title_format = workbook.add_format({'bold': True, 'align': 'center', 'font_size': 14, 'bg_color': '#DDEBF7'})
        header_format = workbook.add_format(
            {'bold': True, 'align': 'center', 'bg_color': '#4F81BD', 'font_color': 'white'})
        date_format = workbook.add_format({'num_format': 'dd/mm/yyyy', 'align': 'center'})

        # Set tiêu đề và độ rộng cột
        worksheet.merge_range('A1:E1', 'Task Deadline Report', title_format)
        worksheet.set_column('A:E', 25)

        # Tiêu đề các cột
        headers = [
            'Task Code', 'Task Name', 'Project', 'Member',
            'Deadline', 'Status'
        ]
        for col, header in enumerate(headers):
            worksheet.write(2, col, header, header_format)

        # Xây dựng câu truy vấn SQL
        query = """
            SELECT DISTINCT
                t.task_code AS task_code,
                t.task_name AS task_name,
                p.project_name AS project_name,
                rp1.name AS member, -- Dev Member
                t.dev_deadline AS deadline,
                t.status AS status
            FROM
                bap_project_task t
            LEFT JOIN
                res_users u1 ON t.dev_id = u1.id
            LEFT JOIN
                res_partner rp1 ON u1.partner_id = rp1.id
            LEFT JOIN
                bap_project p ON t.project_id = p.id
            WHERE
                t.dev_deadline BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '2 days'
        """
        # Thêm điều kiện lọc theo project_ids nếu có
        if project_ids:
            query += " AND t.project_id = ANY(%s)"

        query += """
            UNION ALL
            SELECT DISTINCT
                t.task_code AS task_code,
                t.task_name AS task_name,
                p.project_name AS project_name,
                rp2.name AS member, -- QC Member
                t.qc_deadline AS deadline,
                t.status AS status
            FROM
                bap_project_task t
            LEFT JOIN
                res_users u2 ON t.qc_id = u2.id
            LEFT JOIN
                res_partner rp2 ON u2.partner_id = rp2.id
            LEFT JOIN
                bap_project p ON t.project_id = p.id
            WHERE
                t.qc_deadline BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '2 days'
        """
        # Thêm điều kiện lọc theo project_ids nếu có cho phần UNION
        if project_ids:
            query += " AND t.project_id = ANY(%s)"

        try:
            # Chuyển project_ids_tuple thành array cho PostgreSQL
            self.env.cr.execute(query, (project_ids, project_ids))
            results = self.env.cr.fetchall()
            print("hfhdjdidifdfopfdofodi", results)
        except Exception as e:
            raise UserError(f"An error occurred while fetching data: {str(e)}")

        # Populate các dòng dữ liệu vào báo cáo
        row = 3
        for report in results:
            if len(report) != len(headers):
                raise UserError(f"Unexpected column count: {len(report)} expected {len(headers)}")
            for col, value in enumerate(report):
                # Áp dụng định dạng cho các cột ngày tháng
                if col == 4:  # Cột Sprint Start Date và Sprint End Date
                    worksheet.write_datetime(row, col, value, date_format)
                else:
                    worksheet.write(row, col, value)
            row += 1

        # Đóng workbook và trả về dữ liệu
        workbook.close()
        output.seek(0)
        return output.getvalue()