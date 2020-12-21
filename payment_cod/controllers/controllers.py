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
