# -*- coding: utf-8 -*-
{
    'name': "APTY API App",
    'summary': """
    Handles API calls for Android devices
    """,
    'description': """
        Handle API Calls for Android devices for 
        synchronizing the process.
    """,
    'author': "AptyChoice",
    'website': "http://www.yourcompany.com",
    'category': 'Extra',
    'version': '0.2',
    'depends': ['base_setup','website_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/home_page_view.xml',
        'views/product_template_view.xml',
        'views/res_config_settings_view.xml',
    ],
}
