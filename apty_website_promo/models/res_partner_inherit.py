from odoo import api, fields, models


class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    coupon_used = fields.Boolean(string='First Order Promo Used')
