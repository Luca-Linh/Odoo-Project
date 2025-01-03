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
        worksheet.merge_range('A1:K1', 'Task Deadline Report', title_format)
        worksheet.write('C3', 'Date From', title_format)
        worksheet.write('D3', date_from.strftime('%d/%m/%Y'), date_format)
        worksheet.write('F3', 'Date To', title_format)
        worksheet.write('G3', date_to.strftime('%d/%m/%Y'), date_format)
        worksheet.set_column('A:K', 30)

        # Tiêu đề các cột
        headers = [
            'Member','Project', 'Sprint','Role',
            'Total Tasks', 'New Tasks', 'Development Tasks',
            'Quality Control Tasks', 'Done Tasks', 'Sprint Start Date',
            'Sprint End Date'
        ]
        for col, header in enumerate(headers):
            worksheet.write(5, col, header, header_format)


        # Xây dựng câu truy vấn SQL
        query = """
            SELECT
                rp_dev.name AS member_name,
                p.project_name AS project_name,
                ps.sprint_name AS sprint_name,
                CASE WHEN 'dev' = 'dev' THEN 'Developer' END AS role,
                COUNT(pt.id) AS total_task_count,
                SUM(CASE WHEN pt.status = 'new' THEN 1 ELSE 0 END) AS task_new_count,
                SUM(CASE WHEN pt.status = 'dev' THEN 1 ELSE 0 END) AS task_dev_count,
                0 AS task_qc_count,
                SUM(CASE WHEN pt.status = 'done' THEN 1 ELSE 0 END) AS task_done_count,
                ps.start_date AS sprint_start_date,
                ps.end_date AS sprint_end_date
                FROM
                    bap_project_task pt
                LEFT JOIN bap_project p ON p.id = pt.project_id
                LEFT JOIN res_users ru_dev ON ru_dev.id = pt.dev_id
                LEFT JOIN res_partner rp_dev ON rp_dev.id = ru_dev.partner_id
                LEFT JOIN bap_project_sprint ps ON ps.id = pt.sprint_id
                WHERE pt.dev_id IS NOT NULL
                AND ps.start_date >= %s
                AND ps.end_date <= %s
                {project_filter_dev}
                GROUP BY
                    p.project_name, ps.sprint_name, pt.dev_id, rp_dev.name, ps.start_date, ps.end_date
                UNION ALL
                SELECT
                    rp_qc.name AS member_name,
                    p.project_name AS project_name,
                    ps.sprint_name AS sprint_name,
                    CASE WHEN 'qc' = 'qc' THEN 'Quality Controller' END AS role,
                    COUNT(pt.id) AS total_task_count,
                    SUM(CASE WHEN pt.status = 'new' THEN 1 ELSE 0 END) AS task_new_count,
                    0 AS task_dev_count,
                    SUM(CASE WHEN pt.status = 'qc' THEN 1 ELSE 0 END) AS task_qc_count,
                    SUM(CASE WHEN pt.status = 'done' THEN 1 ELSE 0 END) AS task_done_count,
                    ps.start_date AS sprint_start_date,
                    ps.end_date AS sprint_end_date
                    FROM
                        bap_project_task pt
                    LEFT JOIN bap_project p ON p.id = pt.project_id
                    LEFT JOIN res_users ru_qc ON ru_qc.id = pt.qc_id
                    LEFT JOIN res_partner rp_qc ON rp_qc.id = ru_qc.partner_id
                    LEFT JOIN bap_project_sprint ps ON ps.id = pt.sprint_id
                    WHERE pt.qc_id IS NOT NULL
                    AND ps.start_date >= %s
                    AND ps.end_date <= %s
                    {project_filter_qc}
                    GROUP BY
                        p.project_name, ps.sprint_name, pt.qc_id, rp_qc.name, ps.start_date, ps.end_date
                """

        if project_ids:
            project_filter_dev = " AND pt.project_id = ANY(%s)"
            project_filter_qc = " AND pt.project_id = ANY(%s)"
            params = [date_from, date_to, project_ids, date_from, date_to, project_ids]
        else:
            project_filter_dev = ""
            project_filter_qc = ""
            params = [date_from, date_to, date_from, date_to]

        query = query.format(
            project_filter_dev=project_filter_dev,
            project_filter_qc=project_filter_qc
        )

        # Thực thi truy vấn SQL
        try:
            self.env.cr.execute(query, params)
            results = self.env.cr.fetchall()
        except Exception as e:
            raise UserError(f"An error occurred while fetching data: {str(e)}")

        # Populate các dòng dữ liệu vào báo cáo
        row = 6
        for report in results:
            for col, value in enumerate(report):
                # Áp dụng định dạng cho các cột ngày tháng
                if col in [9, 10]:  # Cột Sprint Start Date và Sprint End Date
                    worksheet.write_datetime(row, col, value, date_format)
                else:
                    worksheet.write(row, col, value)
            row += 1

        # Đóng workbook và trả về dữ liệu
        workbook.close()
        output.seek(0)
        return output.getvalue()
