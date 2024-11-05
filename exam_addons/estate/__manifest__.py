{
    "name":"Real Estate",
    "version":"1.0",
    "category":"Test",
    "description":"""Test 2""",
    "summary":"""
    Exam for test 2
    """,
    "author":"linhvt",
    'depends': ['base'],
    "data":[
        "data/estate_sequence_data.xml",
        "data/demo.xml",
        "data/estate_property_offer_data.xml",
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "views/estate_property_views.xml",
        "views/estate_property_tag_views.xml",
        "views/estate_property_offer_views.xml",
        "views/estate_property_type_views.xml",
        "views/estate_menu_views.xml",
    ],
    'installable': True,
    'application': True
}