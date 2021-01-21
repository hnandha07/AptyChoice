# -*- coding: utf-8 -*-

{
    'name': 'NPA Base',
    'version': '1.2',
    'author': 'Nandhakumar',
    'category': 'Newspaper Agency',
    'depends': ['base','web'],
    'description': """

Newspaper Agency Application - Base Module
======================================================

This module is referenced by all other modules in the NPA System.  It contains
the core models required by other modules in the NPA application.

Through this module, various application parameters, common data, setups
can be performed.

    """,
    'data': [        
        'security/user_groups.xml',
        'security/ir.model.access.csv',        
        'views/views_base.xml',        
        'views/actions_base.xml',
        'views/menus_base.xml',
        'views/template.xml',
        'data/npa_config_delivery.xml'
    ],    
    'qweb': ['static/src/xml/temp.xml', "static/src/xml/base.xml"],
    'installable': True,
    'auto_install': False,
    'application': True,
}
