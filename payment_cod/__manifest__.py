# -*- coding: utf-8 -*-
{
    'name': "AptyChoice Payment COD",
    'summary': "Payment Cash On Delivery",
    'description': """
        Add Cash On Delivery payment option to the website as well android app.
    """,
    'author': "AptyChoice",
    'website': "http://www.yourcompany.com",
    'category': 'Accounting/Payment',
    'version': '0.1',
    'depends': ['payment'],
    'application':True,
    'data': [
        'views/payment_cod_templates.xml',
        'data/payment_cod_data.xml'
    ],
}