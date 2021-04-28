from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _create_new_no_code_promo_reward_lines(self):
        '''Apply new programs that are applicable'''
        self.ensure_one()
        get_coupon_single_user = self.env['sale.coupon.program'].sudo().search([('single_user_coupon', '=', True)],limit=1)
        order = self
        programs = order._get_applicable_no_code_promo_program()
        programs = programs._keep_only_most_interesting_auto_applied_global_discount_program()
        if not self.partner_id.coupon_used and get_coupon_single_user.single_user_coupon:
            for program in programs:
                # VFE REF in master _get_applicable_no_code_programs already filters programs
                # why do we need to reapply this bunch of checks in _check_promo_code ????
                # We should only apply a little part of the checks in _check_promo_code...
                error_status = program._check_promo_code(order, False)
                if not error_status.get('error'):
                    if program.promo_applicability == 'on_next_order':
                        order.state != 'cancel' and order._create_reward_coupon(program)
                    elif program.discount_line_product_id.id not in self.order_line.mapped('product_id').ids:
                        self.write({'order_line': [(0, False, value) for value in self._get_reward_line_values(program)]})
                    order.no_code_promo_program_ids |= program