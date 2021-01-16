# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import _logger,ValidationError

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
            'order_lines': order_lines,
            'amount_untaxed': self.amount_untaxed,
            'taxes': self.amount_tax,
            'total': self.amount_total
        }

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        self.write({
            'apty_order_state':'order',
        })
        return  res

    def prepare_order_lines(self, ol_details=[]):
        order_lines = []
        if len(ol_details) and self.id:
            if not len(self.order_line):
                for old in ol_details:
                    order_lines.append((0,0,{
                        'product_id':old.get('product_id'),
                        'product_uom_qty':old.get('qty'),
                    }))
            else:
                for old in ol_details:
                    product = old.get('product_id')
                    write_action = 3
                    ol = self.order_line.filtered(lambda x:x.product_id.id == product).id
                    if ol:
                        write_action = 1
                    if not ol:
                        write_action, ol = 0, 0
                    values = {'product_id':product,'product_uom_qty':old.get('qty')}
                    order_lines.append((write_action,ol,values))
                check_product_ids = map(lambda x:x.get('product_id'),ol_details)
                remove_lines = self.order_line.filtered(lambda x:x.product_id.id not in check_product_ids)
                if len(remove_lines.ids):
                    _logger.info(
                        "Removing order lines - {0} with product - {1} for order - {2}".format(remove_lines.mapped('id'),
                                                                                               remove_lines.mapped(
                                                                                                   'product_id.name'),
                                                                                               self.name))

                    order_lines += [(2, rol.id) for rol in remove_lines]
        return order_lines


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
