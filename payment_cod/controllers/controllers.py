# -*- coding: utf-8 -*-
import pprint, werkzeug
from odoo import http
from odoo.http import request
from odoo.exceptions import _logger


class PaymentCodController(http.Controller):
    @http.route([
        '/payment/transfer/cod',
    ], type='http', auth='public', csrf=False)
    def cod_feedback(self, **post):
        _logger.info('Beginning Website COD with post data %s', pprint.pformat(post))  # debug
        request.env['payment.transaction'].sudo().form_feedback(post, 'cash_on_delivery')
        return werkzeug.utils.redirect('/shop/confirmation')

    @http.route('/app/payment/cod', type='json', auth='public')
    def app_payment_cod(self, **kwargs):
        try:
            json_data = request.jsonrequest
            if len(json_data) and json_data.get('order_id'):
                order = request.env['sale.order'].sudo().browse(int(json_data.get('order_id')))
                if order.id:
                    partner_country_id = order.partner_id.country_id.id
                    partner_country_id and partner_country_id and partner_country_id or order.company_id.country_id.id
                    order._create_payment_transaction(vals={'acquirer_id': request.env.ref(
                        'payment_cod.payment_acquirer_cod').id, 'partner_country_id':partner_country_id})
                    order.action_confirm()
                    order._create_invoices()
                    return {
                        'status': 2001,
                        'result': True
                    }
                raise UserWarning("Order not found")
            raise UserWarning("Not enough values")
        except Exception as e:
            _logger.info("Exception occured during COD payment - {}".format(e))
            return {
                'status': 2000,
                'result': e
            }
