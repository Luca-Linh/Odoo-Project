{
    "name":"Real Estate",
    "version":"1.0",
    "category":"Test",
    "description":"""Test 2""",
    "summary":"""
    Exam for test 2
    """,
    "author":"linhvt",
    'depends': ['base','mail','report_xlsx'],
    "data":[
        "data/estate_sequence_data.xml",
        "data/demo.xml",
        "data/estate_property_offer_data.xml",
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "views/assets.xml",
        "views/buyer_offer_report_view.xml",
        "views/estate_property_views.xml",
        "views/estate_property_tag_views.xml",
        "views/estate_property_offer_views.xml",
        "views/estate_property_type_views.xml",
        "views/res_user_views.xml",
        "views/estate_property_report_views.xml",
        "views/buyer_offer_report_wizard.xml",
        "views/demo_widget_views.xml",
        # "views/demo_widget_inherit_view.xml",
        "views/estate_menu_views.xml",
    ],

    'qweb': [
        'static/src/xml/integer_color_picker.xml',
        'static/src/xml/button_alert.xml',
    ],

    'installable': True,
    'application': True
}