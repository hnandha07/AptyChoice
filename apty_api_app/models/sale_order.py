# -*- coding: utf-8 -*-

from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    payment_acquirer_id = fields.Many2one("payment.acquirer", string="Payment Acquirer")

    @api.model
    def _get_order_details(self):
        order_lines = [{'product_id': ol.product_id.id,
                        'product_image': '/web/image/product.product/{0}/image_128'.format(ol.product_id.id),
                        'product_name': ol.product_id.name, 'qty': ol.product_uom_qty,
                        'price': ol.price_unit, 'sub_total': ol.price_subtotal} for ol in self.order_line]
        return {
            'state': self.state,
            'total': self.amount_total,
            'order_lines': order_lines
        }


class PaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'

    def _prepare_app_values(self, order_id=False, transaction=False):
        if order_id and transaction:
            return {
                'reference': transaction.reference,
                'partner_id': order_id.partner_id.id,
                'amount':order_id.amount_total,
                'partner_email':order_id.partner_id.email,
                'partner_phone':order_id.partner_id.phone
            }
