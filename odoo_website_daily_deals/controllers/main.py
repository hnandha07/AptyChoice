# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
##############################################################################

from odoo import fields ,SUPERUSER_ID, http, tools, _
from odoo.http import request
from datetime import datetime


class OdooWebsiteDealsOffers(http.Controller):


    # deals_offers Menu
    @http.route(['/deals'], type='http', auth="public", website=True)
    def deals(self, page=0, category=None, search='', **post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry


        pricelist_context = dict(request.env.context)
        pricelist = False
        if not pricelist_context.get('pricelist'):
            pricelist = request.website.get_current_pricelist()
            pricelist_context['pricelist'] = pricelist.id
        else:
            pricelist = request.env['product.pricelist'].browse(pricelist_context['pricelist'])

        request.context = dict(request.context, pricelist=pricelist.id, partner=request.env.user.partner_id)
            	
        from_currency = request.env.user.company_id.currency_id
        to_currency = pricelist.currency_id
        compute_currency = lambda price: from_currency._convert(price, to_currency, request.env.user.company_id, fields.Date.today())

        values = {
            'compute_currency': compute_currency,
            'pricelist_context':pricelist_context,
            'pricelist' : pricelist
            }
        return request.render("odoo_website_daily_deals.deals",values)



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
