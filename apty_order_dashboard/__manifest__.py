{
    'name': "Apty Order Process",
    'summary': """
        Dashboard to show all incoming orders and process it.
    """,
    'description': """
        Manage Orders and process from the dashboard.
    """,
    'author': "Apty Choice / Krutarth",
    'website': "http://www.aptychoice.com",
    'category': 'Extra Tools',
    'version': '1.0',
    'depends': ['npa_base','website_sale', 'point_of_sale', 'pos_sale'],
    'data': [
        'security/user_group.xml',
        # 'security/ir.model.access.csv',
        'views/dashboard_views.xml',
        'views/pos_order_view.xml',
        'views/sale_order_view.xml',
    ],
    'qweb': ["static/src/xml/*.xml"],
}
# -*- coding: utf-8 -*-
