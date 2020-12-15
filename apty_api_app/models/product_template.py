# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_available_full_day = fields.Boolean(string="Is Available Full Day", )
    is_available = fields.Boolean(string="Is Available", )
    availability_time = fields.Float(string="Availability Time", )


class ResCompany(models.Model):
    _inherit = 'res.company'

    shop_time_open = fields.Float(string="Shop Open Time")
    shop_time_close = fields.Float(string="Shop Close Time")
