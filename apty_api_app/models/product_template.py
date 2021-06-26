# -*- coding: utf-8 -*-

from odoo import fields, models, tools
from datetime import timedelta
from ..controllers.main import _get_current_time

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_available = fields.Boolean(string="Is Available", )
    availability_time_start = fields.Float(string="Availability Time Start", )
    availability_time_end = fields.Float(string="Availability Time End", )

    def _get_availability(self, message=False):
        status =  self.availability_time_start < _get_current_time() < self.availability_time_end
        return status

class ResCompany(models.Model):
    _inherit = 'res.company'

    shop_time_open = fields.Float(string="Shop Open Time")
    shop_time_close = fields.Float(string="Shop Close Time")
    order_delivery_charge = fields.Float(string="Default Regional Delivery Charge")


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _get_address_values(self):
        if self.id:
            details = {
                'partner_id': self.id
            }
            for field in ['street', 'street2', 'state_id', 'city', 'zip', 'country_id']:
                if field in ['state_id', 'country_id']:
                    details.update({field.split('_')[0]: self[field].name})
                else:
                    details.update({field: self[field]})
            return details


class ProductCategoryInherit(models.Model):
    _inherit = 'product.category'

    app_allowed = fields.Boolean(string="Is allowed in Mobile App", default=True)
