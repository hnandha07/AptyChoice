# -*- coding: utf-8 -*-
{
    'name': "Apty Kitchen Screen",
    'summary': """
        Kitchen Screen to show orders
    """,
    'description': """
        Manage Orders in kitchen using the kanban view
    """,
    'author': "Apty Choice",
    'website': "http://www.aptychoice.com",
    'category': 'Extra Tools',
    'version': '1.0',
    'depends': ['npa_base','website_sale'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/asset.xml',
        'views/kitchen_screen_view.xml',
        'views/sale_order_view.xml'
    ]
}
