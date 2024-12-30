from odoo import http
from odoo.http import request
from datetime import datetime


class ReportController(http.Controller):

    @http.route('/report_deadline_urgent_xlsx',type='http', auth='user', csrf=False)
    def report_deadline_urgent_xlsx(self, project_ids='', **kwargs):
        user = request.env.user
        project_ids = [int(pid) for pid in project_ids.split(',')] if project_ids else []

        if not project_ids:
            if user.has_group('bap_project.group_project_pm'):
                # Nếu là PM, lấy tất cả các dự án mà PM này quản lý
                project_ids = [project.id for project in request.env['bap.project'].search([('pm_id', '=', user.id)])]
            else:
                # Nếu không phải là PM, lấy tất cả các dự án
                project_ids = [project.id for project in request.env['bap.project'].search([])]

        # Sinh dữ liệu báo cáo
        report = request.env['report.bap_project.report_deadline_urgent_xlsx']
        file_content = report.generate_xlsx_report({'project_ids': project_ids})

        filename = 'Deadline_Report_Urgent.xlsx'
        headers = [
            ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
            ('Content-Disposition', f'attachment; filename={filename}')
        ]
        return request.make_response(file_content, headers=headers)


    @http.route('/report_task_sprint_xlsx', type='http', auth='user', csrf=False)
    def report_task_sprint_xlsx(self, **kwargs):
        date_from = kwargs.get('date_from')
        date_to = kwargs.get('date_to')
        project_ids = kwargs.get('project_ids')

        # Validate dates
        if not date_from or not date_to:
            return "Date from and date to are required."

        # Convert start_date and end_date to date objects
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
        except ValueError:
            return "Invalid date format. Please use YYYY-MM-DD."

        # Convert buyer_ids to a list of integers if provided
        user = request.env.user
        project_ids = [int(pid) for pid in project_ids.split(',')] if project_ids else []

        if not project_ids:
            if user.has_group('bap_project.group_project_pm'):
                # Nếu là PM, lấy tất cả các dự án mà PM này quản lý
                project_ids = [project.id for project in request.env['bap.project'].search([('pm_id', '=', user.id)])]
            else:
                # Nếu không phải là PM, lấy tất cả các dự án
                project_ids = [project.id for project in request.env['bap.project'].search([])]

        # Prepare the context for the report
        data = {
            'date_from': date_from_obj,
            'date_to': date_to_obj,
            'project_ids': project_ids,  # Pass list of IDs or None if no buyers selected
        }
        print("Daata Report",data)

        # Generate the XLSX report
        report = request.env['report.bap_project.report_task_sprint_xlsx']
        file_content = report.generate_xlsx_report_task_in_sprint(data)

        # Return the file as an attachment
        filename = 'Report_Task_Sprint.xlsx'
        response = request.make_response(
            file_content,
            headers=[
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                ('Content-Disposition', f'attachment; filename={filename}')
            ]
        )

        return response