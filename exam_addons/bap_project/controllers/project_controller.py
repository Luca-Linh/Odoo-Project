import logging

from odoo import http
from odoo.http import request, Response
import json
import logging
_logger = logging.getLogger(__name__)


class ProjectController(http.Controller):
    # ed12bc48e64082082bef88bb86d14abd9434c604
    @http.route('/api/projects', auth='user', type='http', methods=['GET'], csrf=False)
    def get_projects(self):
        username = request.params.get('username')
        project_id = request.params.get('project_id')  # Optional project_id param

        # Check if username is provided
        if not username:
            return Response(
                json.dumps({
                    'status': 'error',
                    'message': 'Username is required'
                }),
                status=400,
                content_type='application/json'
            )

        print("Received Params:", request.params)

        # Search for the user by username
        user = request.env['res.users'].sudo().search([('login', '=', username)], limit=1)

        if not user:
            return Response(
                json.dumps({
                    'status': 'not found',
                    'message': f'User with username {username} does not exist'
                }),
                status=404,
                content_type='application/json'
            )

        # Define the domain based on the user's groups (PM, Developer, QC)
        domain = [
            '|', '|',
            ('pm_id', '=', user.id),
            ('dev_ids', 'in', user.id),
            ('qc_ids', 'in', user.id)
        ]

        # Check if the user belongs to the admin group to give access to all projects
        if user.has_group('bap_project.group_project_admin'):
            domain = []  # Admins can see all projects

        if project_id:
            # If project_id is provided, check if it's part of the domain
            project = request.env['bap.project'].sudo().search([('id', '=', project_id)] + domain, limit=1)
            if project:
                project_data = {
                    'id': project.id,
                    'project_name': project.project_name,
                    'pm_id': project.pm_id.id if project.pm_id else None,
                    'dev_ids': [dev.id for dev in project.dev_ids],
                    'qc_ids': [qc.id for qc in project.qc_ids],
                }
                return Response(
                    json.dumps({
                        'status': 'success',
                        'message': f'Project found for user {username}',
                        'data': project_data
                    }),
                    status=200,
                    content_type='application/json'
                )
            else:
                return Response(
                    json.dumps({
                        'status': 'not found',
                        'message': f'Project with ID {project_id} is not found or does not belong to user {username}'
                    }),
                    status=404,
                    content_type='application/json'
                )
        else:
            # If no project_id is provided, return all the projects for the user
            projects = request.env['bap.project'].sudo().search(domain)

            if projects:
                project_data = []
                for project in projects:
                    project_data.append({
                        'id': project.id,
                        'project_name': project.project_name,
                        'pm_id': project.pm_id.id if project.pm_id else None,
                        'dev_ids': [dev.id for dev in project.dev_ids],
                        'qc_ids': [qc.id for qc in project.qc_ids],
                    })
                return Response(
                    json.dumps({
                        'status': 'success',
                        'message': f'Projects found for user {username}',
                        'data': project_data
                    }),
                    status=200,
                    content_type='application/json'
                )
            else:
                return Response(
                    json.dumps({
                        'status': 'not found',
                        'message': f'No projects found for user {username}'
                    }),
                    status=404,
                    content_type='application/json'
                )


    @http.route('/api/tasks', type='http', auth='user', methods=['GET'], csrf=False)
    def get_tasks(self):
        username = request.params.get('username')
        task_id = request.params.get('task_id')
        if not username:
            return Response(
                json.dumps({
                    "error": "Bad Request",
                    "message": "Username is required"
                }),
                status=400,
                content_type='application/json'
            )
        print("Received Params:", request.params)
        user = request.env['res.users'].sudo().search([('login', '=', username)], limit=1)

        if not user:
            return Response(
                json.dumps({
                    "error": "Not Found",
                    "message": f"User with username '{username}' not found"
                }),
                status=404,
                content_type='application/json'
            )

        # Tạo domain dựa trên quyền của người dùng
        domain = [
            '|', '|',
            ('project_id.dev_ids', 'in', user.id),
            ('project_id.qc_ids', 'in', user.id),
            ('project_id.pm_id', '=', user.id)
        ]
        if user.has_group('bap_project.group_project_admin'):
            domain = []

        if task_id:
            # If project_id is provided, check if it's part of the domain
            task = request.env['bap.project.task'].sudo().search([('id', '=', task_id)] + domain, limit=1)
            if task:
                data = {
                    'id': task.id,
                    'name': task.task_name,
                    'project_id': task.project_id.id,
                    'dev_id': task.dev_id.id if task.dev_id else None,
                    'dev_name': task.dev_id.name if task.dev_id else None,
                    'qc_id': task.qc_id.id if task.qc_id else None,
                    'qc_name': task.qc_id.name if task.qc_id else None,
                    'dev_deadline': task.dev_deadline.strftime('%Y-%m-%d') if task.dev_deadline else None,
                    'qc_deadline': task.qc_deadline.strftime('%Y-%m-%d') if task.qc_deadline else None,
                    'description': task.description,
                    'state': task.status,
                }
                return Response(
                    json.dumps({
                        'status': 'success',
                        'message': f'Task found for user {username}',
                        'data': data
                    }),
                    status=200,
                    content_type='application/json'
                )
            else:
                return Response(
                    json.dumps({
                        'status': 'not found',
                        'message': f'Task with ID {task_id} is not found or does not belong to user {username}'
                    }),
                    status=404,
                    content_type='application/json'
                )
        else:
            # Lọc task theo domain
            tasks = request.env['bap.project.task'].sudo().search(domain)

            if not tasks:
                return Response(
                    json.dumps({
                        "error": "Not Found",
                        "message": "No tasks found for the specified user"
                    }),
                    status=404,
                    content_type='application/json'
                )
            data = [
                {
                    'id': task.id,
                    'name': task.task_name,
                    'project_id': task.project_id.id,
                    'dev_id': task.dev_id.id if task.dev_id else None,
                    'dev_name': task.dev_id.name if task.dev_id else None,
                    'qc_id': task.qc_id.id if task.qc_id else None,
                    'qc_name': task.qc_id.name if task.qc_id else None,
                    'dev_deadline': task.dev_deadline.strftime('%Y-%m-%d') if task.dev_deadline else None,
                    'qc_deadline': task.qc_deadline.strftime('%Y-%m-%d') if task.qc_deadline else None,
                    'description': task.description,
                    'state': task.status,
                }
                for task in tasks
            ]
            return Response(
                json.dumps({
                    "status": "success",
                    "message": "Tasks retrieved successfully",
                    "data": data
                }),
                status=200,
                content_type='application/json'
            )

    @http.route('/api/task/<int:task_id>', type='json', auth='user', methods=['PUT'], csrf=False)
    def update_task(self, task_id):
        _logger.info(f"Request args: {request.httprequest.args}")
        try:
            # Get the username from query parameters
            username = request.httprequest.args.get('username')
            task_data = request.jsonrequest
            _logger.info(f"Received username: {username}")
            if not username:
                return Response(
                    json.dumps({
                        "status": "error",
                        "message": "Username is required"
                    }),
                    headers={'Content-Type': 'application/json'},
                    status=400
                )

            # Tìm user theo username
            user = request.env['res.users'].sudo().search([('login', '=', username)], limit=1)
            if not user:
                return Response(
                    json.dumps({
                        "status": "error",
                        "message": "User not found"
                    }),
                    headers={'Content-Type': 'application/json'},
                    status=404
                )

            # Tìm task theo task_id
            task = request.env['bap.project.task'].sudo().browse(task_id)
            _logger.info(f"Received Task: {task}")

            if not task.exists():
                _logger.error(f"Task {task_id} not found")
                return Response(
                    json.dumps({
                        "status": "error",
                        "message": "Task not found"
                    }),
                    headers={'Content-Type': 'application/json'},
                    status=404
                )

            # Các trường được phép cập nhật
            allowed_fields = [
                'task_name', 'sprint_id',
                'dev_id', 'qc_id', 'task_type_id',
                'dev_deadline', 'qc_deadline', 'status', 'description'
            ]

            project = task.project_id
            if user.has_group('bap_project.group_project_admin'):
                # Lọc các trường hợp lệ từ kwargs
                update_data = {key: value for key, value in task_data.items() if key in allowed_fields}
            elif user.has_group('bap_project.group_project_pm') or user.has_group('bap_project.group_project_member'):
                if user.id in project.qc_ids.ids or user.id in project.dev_ids.ids or user.id == project.pm_id.id :
                    _logger.error(f"User {username} does not have permission to edit task {task_id}")
                    return {
                        'status': 'forbidden',
                        'message': 'You do not have permission to edit this task'
                    }
                # Lọc các trường hợp lệ từ kwargs
                update_data = {key: value for key, value in task_data.items() if key in allowed_fields}
            else:
                _logger.error(f"User {username} is not authorized to edit task {task_id}")
                return {
                    'status': 'forbidden',
                    'message': 'You do not have permission to edit this task'
                }

            if not update_data:
                return Response(
                    json.dumps({
                        "status": "error",
                        "message": "No valid fields to update"
                    }),
                    headers={'Content-Type': 'application/json'},
                    status=400
                )

            # Cập nhật thông tin task
            task.sudo().write(update_data)

            # Trả về thông tin task sau khi cập nhật
            task_data_update = {
                'id': task.id,
                'task_code': task.task_code,
                'task_name': task.task_name,
                'project_id': task.project_id.id,
                'sprint_id': task.sprint_id.id,
                'dev_id': task.dev_id.id if task.dev_id else None,
                'qc_id': task.qc_id.id if task.qc_id else None,
                'task_type_id': task.task_type_id.id if task.task_type_id else None,
                'dev_deadline': task.dev_deadline.strftime('%Y-%m-%d') if task.dev_deadline else None,
                'qc_deadline': task.qc_deadline.strftime('%Y-%m-%d') if task.qc_deadline else None,
                'status': task.status,
                'description': task.description,
            }

            return Response(
                json.dumps({
                    "status": "success",
                    "message": "Task updated successfully",
                    "data": task_data_update
                }),
                headers={'Content-Type': 'application/json'},
                status=200
            )
        except Exception as e:
            _logger.error(f"Error updating task: {str(e)}")
            return Response(
                json.dumps({
                    "status": "error",
                    "message": f"An error occurred: {str(e)}"
                }),
                headers={'Content-Type': 'application/json'},
                status=500
            )


