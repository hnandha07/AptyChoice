# -*- coding: utf-8 -*-
import json
from odoo import http
from odoo.http import request
from odoo.addons.website.controllers.main import Website


class Shop(Website):

    @http.route('/app/home', type='http', auth='public', website=True)
    def get_home_page(self, **kwargs):
        """
        Render home page for App.
        :return: char, rendered home page template
        """
        if kwargs.get('from_app', False):
            return request.render('apty_api_app.home_page_content_app', {'from_app': True})

    @http.route('/app/login', type='json', auth='public', website=True)
    def app_login(self):
        """
        Authenticate user for login
        :return: dict, response including uid, and status code
        """
        login_response = {}
        json_data = request.jsonrequest
        try:
            if not len(json_data):
                raise ValueError("No enough values.")
        except ValueError as ve:
            login_response = {
                "msg": ve,
                "code": 303
            }
        return login_response

    @http.route('/app/shop/products', type='json', auth='public', website=True)
    def get_shop_products(self):
        json_data = request.jsonrequest
        offset = json_data.get('scroll_count', 0) * 10
        product_obj = request.env['product.product'].sudo()
        order = 'create_date'
        domain = [('active', '=', True)]
        if json_data.get('filter_by_category', False):
            domain += [('categ_id', 'in', json_data.get('categ_ids'))]
        if json_data.get('sort_by', False) and json_data.get('', False) and json_data.get('', False):
            order = '{0} {1}'.format(json_data.get('', False), json_data.get('', False))
            return product_obj.search_read(domain=domain,
                                       fields=['id', 'display_name', 'image_512', 'lst_price', 'website_style_ids'],
                                       offset=offset, limit=10, order=order)
