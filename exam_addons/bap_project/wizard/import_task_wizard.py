from odoo import models, fields
from odoo.exceptions import UserError
import base64
import csv
import xlrd
from io import StringIO
from datetime import datetime, timedelta

class ImportTaskWizard(models.TransientModel):
    _name = 'import.task.wizard'
    _description = 'Import Task Wizard'

    data_file = fields.Binary('File', required=True)
    file_name = fields.Char('File Name', required=True)
    file_type = fields.Selection([('csv', 'CSV'), ('excel', 'Excel')], string='File Type', required=True)

    def action_import_task(self):
        if not self.data_file:
            raise UserError('Please upload a file to import.')

        file_data = base64.b64decode(self.data_file)

        if self.file_type == 'csv':
            self._import_csv(file_data)
        elif self.file_type == 'excel':
            self._import_excel(file_data)

        return {'type': 'ir.actions.act_window_close'}

    def _import_csv(self, file_data):
        file_content = StringIO(file_data.decode('utf-8'))
        reader = csv.DictReader(file_content)

        for row in reader:
            self._create_task_from_row(row)

    def _import_excel(self, file_data):
        workbook = xlrd.open_workbook(file_contents=file_data)
        sheet = workbook.sheet_by_index(0)

        # Get headers
        headers = sheet.row_values(0)

        for row_idx in range(1, sheet.nrows):
            row = {headers[i]: sheet.cell_value(row_idx, i) for i in range(len(headers))}
            self._create_task_from_row(row)

    def _create_task_from_row(self, row):
        task_name = row.get('Tên')
        project_name = row.get('Dự án')
        sprint_code = row.get('Sprint')
        dev_email = row.get('DEV')
        qc_email = row.get('QC')
        task_type_code = row.get('Loại Task')
        dev_deadline = row.get('DEV Deadline')
        qc_deadline = row.get('QC Deadline')
        description = row.get('Mô tả')

        # Chuyển đổi số ngày thành ngày tháng năm
        dev_deadline = self._convert_days_to_date(dev_deadline)
        qc_deadline = self._convert_days_to_date(qc_deadline)

        # Kiểm tra dự án
        project = self.env['bap.project'].search([('project_name', '=', project_name)], limit=1)
        if not project:
            raise UserError(f'Project "{project_name}" not found.')

        # Kiểm tra sprint
        sprint = self.env['bap.project.sprint'].search([('sprint_code', '=', sprint_code)], limit=1)
        if not sprint:
            raise UserError(f'Sprint "{sprint_code}" not found.')

        # Kiểm tra loại task
        task_type = self.env['bap.project.task.type'].search([('task_type_code', '=', task_type_code)], limit=1)
        if not task_type:
            raise UserError(f'Task Type "{task_type_code}" not found.')

        # Kiểm tra người dùng DEV
        dev_user = self.env['res.users'].search([('email', '=', dev_email)], limit=1)
        if not dev_user:
            raise UserError(f'DEV user with email "{dev_email}" not found.')

        # Kiểm tra người dùng QC
        qc_user = self.env['res.users'].search([('email', '=', qc_email)], limit=1)
        if not qc_user:
            raise UserError(f'QC user with email "{qc_email}" not found.')

        # Tạo task mới
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
        """
        Chuyển đổi số ngày thành ngày tháng năm theo mốc thời gian 01/01/1900.
        :param days: Số ngày từ mốc thời gian.
        :return: Ngày tháng năm.
        """
        start_date = datetime(1900, 1, 1)
        return (start_date + timedelta(days=int(days))).strftime('%Y-%m-%d')
