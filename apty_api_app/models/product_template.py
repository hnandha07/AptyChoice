# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_available_full_day = fields.Boolean(string="Is Available Full Day", )
    is_available = fields.Boolean(string="Is Available", )
    availability_time_start = fields.Float(string="Availability Time Start", )
    availability_time_end = fields.Float(string="Availability Time End", )


class ResCompany(models.Model):
    _inherit = 'res.company'

    shop_time_open = fields.Float(string="Shop Open Time")
    shop_time_close = fields.Float(string="Shop Close Time")

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
