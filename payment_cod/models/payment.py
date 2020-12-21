# -*- coding: utf-8 -*-
import random
from odoo import models, fields, _
from odoo.exceptions import ValidationError, _logger


class PaymentCOD(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('cash_on_delivery', 'Cash On Delivery')])

    def cash_on_delivery_form_generate_values(self, values=False):
        if self.provider == 'cash_on_delivery' and values:
            payment_transaction = self.env['payment.transaction'].search([('reference', '=', values.get('reference'))])
            cod_ref = values['reference'].split('-')[0] + '-' +  str(random.randint(1,9999))
            if payment_transaction.id:
                payment_transaction.write({
                    'cod_payment_reference': cod_ref
                })
            return {'cod_payment_reference': cod_ref}

    def cash_on_delivery_get_form_action_url(self):
        return '/payment/transfer/cod'


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    cod_payment_reference = fields.Char(string="COD Payment Reference", required=False, )

    def _cash_on_delivery_form_get_tx_from_data(self, data=False):
        reference = data.get('cod_payment_reference', False)
        payment_tx = self.search([('cod_payment_reference', '=', reference)])
        if not payment_tx or len(payment_tx) > 1:
            error_msg = _('Sips: received data for reference %s') % reference
            if not payment_tx:
                error_msg += _('; no order found')
            else:
                error_msg += _('; multiple order found')
            _logger.error(error_msg)
            raise ValidationError(error_msg)
        return payment_tx

    def _cash_on_delivery_form_validate(self, data=False):
        if data:
            self._set_transaction_pending()
            order = self.sale_order_ids
            order.action_confirm()
            order._create_invoices()
            return {
                'transaction': self.id
            }
