# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class AptyChoiceDashboard(http.Controller):

    @http.route("/get_order_list", type="json", auth="user")
    def get_order_list(self, **kwargs):
        apty_order_state = kwargs.get('state')
        sale_orders = request.env['sale.order'].search_read([('state', '=', 'sale'), ('apty_order_state', '=', apty_order_state)], ['id', 'name', 'partner_id', 'write_date'])
        for so in sale_orders:
            so['model'] = 'sale.order'
        pos_orders = request.env['pos.order'].search_read([('state', '=', 'paid'), ('apty_order_state', '=', apty_order_state)], ['id', 'name', 'partner_id', 'write_date'])
        for po in pos_orders:
            po['model'] = 'pos.order'
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
    