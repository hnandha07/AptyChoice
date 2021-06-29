# -*- coding: utf-8 -*-
import datetime
from datetime import timedelta as td
from odoo import http
from odoo.http import request
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class AptyChoiceDashboard(http.Controller):

    @http.route("/get_order_list", type="json", auth="user")
    def get_order_list(self, **kwargs):
        apty_order_state = kwargs.get('state')
        so_domain = [('state', '=', 'sale'), ('apty_order_state', '=', apty_order_state)]
        pos_domain = [('state', '=', 'paid'), ('apty_order_state', '=', apty_order_state)]
        if kwargs.get('state') in ['delivered', 'cancel']:
            today = datetime.datetime.now()
            last_order_date = (today - td(days=5)).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            so_domain.append(('write_date', '>=', last_order_date))
            pos_domain.append(('write_date', '>=', last_order_date))
        sale_orders = request.env['sale.order'].search_read(so_domain, ['id', 'name', 'partner_id', 'write_date', 'transaction_ids', 'team_id'])
        for so in sale_orders:
            so['model'] = 'sale.order'
            so['order_source'] = so.get('team_id')[-1]
            if so.get('transaction_ids'):
                payment_trans = request.env['payment.transaction'].search([('id', '=', so.get('transaction_ids')[0])])
                if payment_trans:
                    so['payment_mode'] = payment_trans.acquirer_id.name
                else:
                    so['payment_mode'] = 'None'
            else:
                so['payment_mode'] = 'None'
        pos_orders = request.env['pos.order'].search_read(pos_domain, ['id', 'name', 'partner_id', 'write_date'])
        for po in pos_orders:
            po['model'] = 'pos.order'
            po['payment_mode'] = 'Cash'
            po['order_source'] = 'Point of Sale'
            if not po.get('partner_id'):
                po['partner_id'] = ('', '')
            # if po.get('company_id')[0]:
            #     company_details = request.env['res.company'].sudo().search([('id', '=', po.get('company_id')[0])])
            #     po['company_id'] = (company_details.name, company_details.phone, company_details.vat, company_details.email, company_details.website)
            #     print('----company_details--', company_details)
        res = sorted(sale_orders + pos_orders, key=lambda d: d['write_date'], reverse=True)
        return {"orders": res or []}

    @http.route("/get_delivery_partners", type="json", auth="user")
    def get_delivery_partners(self, **kwargs):
        partners = []
        delivery_partner_group = request.env['ir.model.data'].xmlid_to_object('apty_order_dashboard.npa_group_delivery_person')
        for user in delivery_partner_group.users:
            partners.append({
                'id': user.id,
                'name': user.name,
                'email': user.email
            })
        return { 'partners': partners}

    @http.route("/order/process/cod", type="json", auth="user")
    def order_process_cod(self, **kwargs):
        if kwargs and kwargs.get('order_id'):
            order_id = request.env[kwargs.get('model')].sudo().search([('id', '=', kwargs.get('order_id'))])
            payment_transaction_id = request.env['payment.transaction'].sudo().search([('reference', 'ilike', order_id.name)], order='id desc', limit=1)
            payment_transaction_id._set_transaction_done()
            payment_transaction_id._post_process_after_done()
            order_id.write({
                'apty_order_state': 'delivered',
                'delivered_by': request.uid,
                'delivered_date': datetime.datetime.now()
            })
        return {"status": True}
