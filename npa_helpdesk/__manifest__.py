# -*- coding: utf-8 -*-

{
    'name': 'NPA Helpdesk',
    'version': '1.2',
    'author': 'Nandhakumar',
    'category': 'Newspaper Agency',
    'depends': ['web','npa_base'],
    'description': """

Newspaper Agency Application - Newspaper Management Module
======================================================

This module is referenced by all other modules in the NPA System.  It contains
the core models required by other modules in the NPA application.

Through this module, various application parameters, common data, setups
can be performed.

    """,
    'data': [        
        'security/ir.model.access.csv',
        #'wizards/wizards_helpdesk.xml',
        'views/template.xml',
        'views/views_helpdesk.xml',
        'views/actions_helpdesk.xml',
        'views/menus_helpdesk.xml',              
    ],    
    'qweb': ['static/src/xml/*.xml', ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
