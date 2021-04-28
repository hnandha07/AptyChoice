from odoo import api, fields, models


class SaleCouponProgramInherit(models.Model):
    _inherit = 'sale.coupon.program'

    single_user_coupon = fields.Boolean(string='Single User Coupon')