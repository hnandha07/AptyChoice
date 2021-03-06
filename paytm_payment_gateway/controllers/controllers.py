# -*- coding: utf-8 -*-
###################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2019-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################

import logging
import pprint
import werkzeug
from werkzeug.utils import redirect
from odoo import http
from odoo.http import request
_logger = logging.getLogger(__name__)


class AtomController(http.Controller):
    @http.route(['/payment/paytm/return/', '/payment/paytm/cancel/', '/payment/paytm/error/'],
                type='http', auth='public', csrf=False)
    def paytm_return(self, **post):
        """ Paytm."""

        _logger.info(
            'Paytm: entering form_feedback with post data %s', pprint.pformat(post))
        if post:
            request.env['payment.transaction'].sudo().form_feedback(post, 'paytm')
        return werkzeug.utils.redirect('/payment/process')

    @http.route('/app/payment/confirm', type='json', auth='public')
    def app_payment_confirm(self, **kwargs):
        json_data = request.jsonrequest
        staus = False
        _logger.info("Payment Confirm JSON Data".format(pprint.pformat(json_data)))
        if len(json_data) and json_data.get('payment_tx_id'):
            payment_transaction = request.env['payment.transaction'].sudo().browse(int(json_data.get('payment_tx_id')))
            payment_transaction._set_transaction_done()
            payment_transaction._post_process_after_done()
            # payment_transaction._reconcile_after_transaction_done()
            staus = True
            if payment_transaction and payment_transaction.partner_id:
                payment_transaction.partner_id.write({
                    'coupon_used': True
                })
        return staus





    
