from odoo import models, fields, api
from odoo.exceptions import UserError
import base64
import xlrd
from datetime import datetime, timedelta


class ImportTaskWizard(models.TransientModel):
    _name = 'import.task.wizard'
    _description = 'Import Task Wizard'

    data_file = fields.Binary('File', required=True)
    file_name = fields.Char('File Name', required=True)
    file_preview = fields.Html('File Preview', readonly=True)

    @api.onchange('data_file', 'file_name')
    def _onchange_data_file(self):
        """Preview Excel file content or show an error if the file is not Excel."""
        if not self.data_file:
            self.file_preview = ''
            return

        if not self.file_name or not self.file_name.lower().endswith(('.xls', '.xlsx')):
            raise UserError('Only Excel files (.xls or .xlsx) are allowed.')

        file_data = base64.b64decode(self.data_file)
        try:
            self.file_preview = self._preview_excel(file_data)
        except Exception as e:
            self.file_preview = f"<p style='color: red;'>Error processing file: {str(e)}</p>"

    def _preview_excel(self, file_data):
        """Preview the content of an Excel file."""
        workbook = xlrd.open_workbook(file_contents=file_data)
        sheet = workbook.sheet_by_index(0)

        html = '<table border="1" style="width:100%; text-align:left;">'
        # Add headers
        headers = sheet.row_values(0)
        html += '<tr>' + ''.join(f'<th>{header}</th>' for header in headers) + '</tr>'
        # Add rows
        for row_idx in range(1, sheet.nrows):
            row = sheet.row_values(row_idx)
            html += '<tr>' + ''.join(f'<td>{value}</td>' for value in row) + '</tr>'
        html += '</table>'
        return html

    def action_import_task(self):
        """Import task data from Excel."""
        if not self.data_file:
            raise UserError('Please upload a file to import.')

        if not self.file_name.lower().endswith(('.xls', '.xlsx')):
            raise UserError('Only Excel files (.xls or .xlsx) are allowed.')

        file_data = base64.b64decode(self.data_file)
        workbook = xlrd.open_workbook(file_contents=file_data)
        sheet = workbook.sheet_by_index(0)

        headers = sheet.row_values(0)
        imported_count = 0

        for row_idx in range(1, sheet.nrows):
            row = {headers[i]: sheet.cell_value(row_idx, i) for i in range(len(headers))}
            self._create_task_from_row(row)
            imported_count += 1
        # Hiển thị thông báo thành công
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Import Successful',
                'message': f'{imported_count} tasks have been imported successfully!',
                'type': 'success',
                'sticky': False,
            },
            'next_action': {
                'type': 'ir.actions.act_window_close',
            }
        }

    def _create_task_from_row(self, row):
        """Create a task from a single row of data."""
        task_name = row.get('Tên')
        project_name = row.get('Dự án')
        sprint_code = row.get('Sprint')
        dev_email = row.get('DEV')
        qc_email = row.get('QC')
        task_type_code = row.get('Loại Task')
        dev_deadline = self._convert_days_to_date(row.get('DEV Deadline'))
        qc_deadline = self._convert_days_to_date(row.get('QC Deadline'))
        description = row.get('Mô tả')

        # Reference checks
        project = self.env['bap.project'].search([('project_name', '=', project_name)], limit=1)
        sprint = self.env['bap.project.sprint'].search([('sprint_code', '=', sprint_code)], limit=1)
        task_type = self.env['bap.project.task.type'].search([('task_type_code', '=', task_type_code)], limit=1)
        dev_user = self.env['res.users'].search([('email', '=', dev_email)], limit=1)
        qc_user = self.env['res.users'].search([('email', '=', qc_email)], limit=1)

        if not project:
            raise UserError(f'Project "{project_name}" not found.')
        if not sprint:
            raise UserError(f'Sprint "{sprint_code}" not found.')
        if not task_type:
            raise UserError(f'Task Type "{task_type_code}" not found.')
        if not dev_user:
            raise UserError(f'DEV user with email "{dev_email}" not found.')
        if not qc_user:
            raise UserError(f'QC user with email "{qc_email}" not found.')

        # Create task
        self.env['bap.project.task'].create({
            'task_code': task_type_code,
            'task_name': task_name,
            'project_id': project.id,
            'sprint_id': sprint.id,
            'dev_id': dev_user.id,
            'qc_id': qc_user.id,
            'task_type_id': task_type.id,
            'dev_deadline': dev_deadline,
            'qc_deadline': qc_deadline,
            'description': description,
            'status': 'new'
        })

    @staticmethod
    def _convert_days_to_date(days):
        """Convert number of days since 01/01/1900 to date."""
        start_date = datetime(1900, 1, 1)
        return (start_date + timedelta(days=int(days))).strftime('%Y-%m-%d')
