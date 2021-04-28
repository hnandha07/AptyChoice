# -*- coding: utf-8 -*-

{
    'name': 'APTY AcctMgmt',
    'version': '1.2',
    'author': 'Nandhakumar',
    'category': 'Apty Choice',
    'depends': ['web','sale_management','npa_base','npa_helpdesk'],
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
        'data/apty_sequence_code.xml',
        'wizards/wizards_stock.xml',        
        'views/views_supplier.xml',
        'views/actions_acctmgmt.xml',
        'views/menus_acctmgmt.xml',              
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
