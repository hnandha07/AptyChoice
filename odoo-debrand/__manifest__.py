# -*- coding: utf-8 -*-


{
    'name': "Odoo Debranding",
    'version': "13.0.1.2.2",
    'summary': """Odoo Backend and Front end Debranding""",
    'description': """Debrand Odoo,Debranding, odoo13""",
    'live_test_url': '',
    'author': "Silvercom",
    'company': "Silvercom",
    'maintainer': "Silvercom",
    'website': "https://silvercomsmartconsultancy.com/",
    'category': 'Tools',
    'depends': ['website', 'base_setup'],
    'data': [
        'views/views.xml',
        'views/res_config_views.xml',
        'views/ir_module_views.xml'
    ],
    'qweb': ["static/src/xml/base.xml"],
    'images': ['static/description/banner.gif'],
    'license': "AGPL-3",
    'installable': True,
    'application': False
}
