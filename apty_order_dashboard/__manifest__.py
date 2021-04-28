# -*- coding: utf-8 -*-
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
    'depends': ['npa_base','website_sale'],
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/asset.xml',
        # 'views/kitchen_screen_view.xml',
        'views/dashboard_views.xml'
    ],
    'qweb': ["static/src/xml/*.xml"],
}
