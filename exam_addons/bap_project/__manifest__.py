{
    "name":"Training Project",
    "version":"1.0",
    "category":"Project",
    "description":"""Last Project""",
    "summary":"""
    Exam for Project
    """,
    "author":"linhvt",
    'depends': ['base','mail','report_xlsx','website'],
    "data":[
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "security/bap_project_security.xml",
        "data/sequence_data.xml",
        "data/ir_cron_report_task_weekly.xml",
        "data/res_users_data.xml",
        "data/project_data.xml",
        "data/project_mail_template_data.xml",
        "views/assets.xml",
        "views/bap_project_views.xml",
        "views/bap_project_task_views.xml",
        "views/bap_project_sprint_views.xml",
        "views/bap_project_request_open_views.xml",
        "views/bap_project_request_close_views.xml",
        "views/bap_project_request_open_cancel_wizard_view.xml",
        "views/bap_project_request_close_cancel_wizard_view.xml",
        "views/bap_project_task_type_views.xml",
        "views/bap_project_member_views.xml",
        "report/report_deadline_urgent_view.xml",
        "report/report_task_sprint_view.xml",
        "wizard/report_deadline_urgent_wizard_view.xml",
        "wizard/report_task_sprint_wizard_view.xml",
        "wizard/report_task_sprint_xlsx_wizard_view.xml",
        "wizard/import_task_wizard_view.xml",
        "views/bap_project_menu_views.xml",
    ],

    'qweb': [
        'static/src/xml/button_task.xml',
    ],

    'installable': True,
    'application': True
}