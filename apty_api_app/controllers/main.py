# -*- coding: utf-8 -*-
import random, requests, json
from odoo import http, _
from datetime import datetime
from odoo.http import request
from odoo.addons.website.controllers.main import Website
from odoo.exceptions import _logger
from odoo.addons.website_form.controllers.main import WebsiteForm
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSale(WebsiteSale):

    @http.route('/app/order/history', type='json', auth='none', cors="*", website=True)
    def app_order_history(self):
        try:
            json_data = request.jsonrequest
            if not len(json_data) or not json_data.get('user_id'):
                return {
                    'status': 2001,
                    'message': "Not enough values"
                }
            offset = json_data.get('scroll_count', 0) * 10
            user_id = request.env.user.browse(json_data.get('user_id'))
            if not user_id.id:                return {
                    'status': 2002,
                    'message': "User id not found"
                }
            domain = [('partner_id', '=', user_id.partner_id.id)]
            order_obj = request.env['sale.order'].sudo()
            # domain += [('state', 'in', [status[0] for status in order_obj._fields['state'].selection])]
            orders = order_obj.search_read(domain=domain,
                                                fields=['id', 'display_name', 'date_order', 'amount_total', 'state'],
                                                offset=offset, limit=10, order='create_date desc')
            return orders
        except Exception as e:
            return {
                'status': 2000,
                'message': e
            }

    @http.route('/app/order/cancel', type='json', auth='none', cors="*", website=True)
    def app_order_cancel(self):
        try:
            json_data = request.jsonrequest
            if not len(json_data) or not json_data.get('order_id'):
                return {
                    'status': 2001,
                    'message': "Not enough values"
                }
            order = request.env['sale.order'].browse(json_data.get('order_id')).sudo()
            status = order.action_cancel()
            return status
        except Exception as e:
            return {
                'status': 2000,
                'message': e
            }

    @http.route('/app/order', type='json', auth='none', cors="*", website=True)
    def app_add_order(self):
        try:
            json_data = request.jsonrequest
            if len(json_data):
                if not json_data.get('user_id', False):
                    raise Exception("User Id missing in request data")
                user = request.env['res.users'].sudo().browse(int(json_data.get('user_id')))
                if not user.id:
                    return {
                        'status': 2000,
                        'message': 'User ID not found in the request {}'.format(json_data)
                    }
                if not len(json_data.get('order_line_details')):
                    return {
                        'status': 2000,
                        'message': 'Order line details not found in the request {}'.format(json_data)
                    }
                order = request.website.with_user(user=user).sale_get_order(force_create=1)
                order_lines = []
                for old in json_data.get('order_line_details'):
                    order_lines.append((0,0,{
                        'product_id': old.get('product_id'),
                        'product_uom_qty': old.get('qty'),
                    }))
                if order.id:
                    order.sudo().write({
                        'order_line': order_lines
                    })
                return {'order_id': order.id}
            else:
                return {
                    'status': 2001,
                    'message': 'Not enough values in request {}'.format(json_data)
                }
        except Exception as e:
            return {
                'status': 2000,
                'message': e
            }


class WebsiteForm(WebsiteForm):
    @http.route('/app/contactus', type='json', auth='public', website=True)
    def app_contact_us(self, **kwargs):
        try:
            data = request.jsonrequest
            if len(data):
                data.update(email_to=request.env.company.email)
                request.params = data
                res = super(WebsiteForm, self).website_form(model_name='mail.mail', kwargs=data)
                return {
                    'response': res.status,
                    'status': res.status_code
                }
        except Exception as e:
            return {
                'status': '4003',
                'message': e
            }


class AuthSignupHome(AuthSignupHome):

    def _get_app_login(self, login=False, password=False):
        if login and password:
            uid = request.session.authenticate(request.env.cr.dbname, login, password)
            if not uid:
                raise Exception(_('Authentication Failed.'))
            uid = request.env['res.users'].sudo().browse(uid)
            return {
                'uid': uid.id,
                'login': login,
                'mobile': uid.partner_id.phone and uid.partner_id.phone or uid.partner_id.mobile,
                'email': uid.partner_id.email,
                'name': uid.name,
            }
        return False

    @http.route('/app/change/password', type='json', auth='public', website=True)
    def change_user_password(self):
        try:
            json_data = request.jsonrequest
            request_type  = json_data.get('rtype', False)
            login = json_data.get('login', False)
            # if not len(json_data) or not all[request_type, login]:
            #     raise  UserWarning("Not enough values:{}".format(json_data))
            user = request.env['res.users'].sudo().search([('login', '=', login)])
            if not user.id:
                raise UserWarning("User not found: {}".format(user))
            if request_type == 'update' and request.get('password', False):
                update_status = user.write({'password': request.get('password')})
                return {
                    'status': update_status
                }
        except Exception as e:
            return {
                'message': e,
                'status_code': '4002'
            }

    @http.route('/app/login', type='json', auth='public', website=True)
    def login_app_user(self, **kwargs):
        try:
            json_data = request.jsonrequest
            if not len(json_data) or not json_data.get('login', False) or not json_data.get('password', False):
                raise Exception(_("Not enough values"))
            return self._get_app_login(login=json_data.get('login', False), password=json_data.get('password'))
        except Exception as e:
            return {
                'message': e,
                'status_code': '4002'
            }

    @http.route('/app/mobile/verification', type='json', auth='public', website=True)
    def mobile_verification(self, **kwargs):
        try:
            json_data = request.jsonrequest
            if len(json_data):
                sms_api_key = request.env['ir.config_parameter'].sudo().get_param('apty_api_app.sms_api_key', False)
                if not sms_api_key or not len(sms_api_key):
                    _logger.info("SMS API Key is not set, Please set for mobile number verification")
                    raise UserWarning("Something went wrong")

                url = "https://2factor.in/API/V1"
                if json_data.get('autogen', False):
                    if not json_data.get('mobile', False):
                        raise UserWarning("Not enough values for verification")
                    url = '{0}/{1}/SMS/+91{2}/AUTOGEN'.format(url, sms_api_key, json_data.get('mobile'))
                    response = requests.request("GET", url, headers={}, data={})
                elif json_data.get('verify', False):
                    if not json_data.get('session_id', False) and not json_data.get('otp', False):
                        raise UserWarning("Not enough values for verification")
                    url = '{0}/{1}/SMS/VERIFY/{2}/{3}'.format(url, sms_api_key, json_data.get('session_id'),
                                                              json_data.get('otp'))
                    response = requests.request("GET", url, headers={}, data={})
                return json.loads(response.text)
            else:
                return {"status_code": 2004, "message": "Not enough values"}
        except Exception as e:
            return {
                'message': "{0}".format(e),
                'status_code': "4003"
            }

    @http.route('/app/signup', type='json', auth='public', website=True)
    def signup_app_user(self, **kwargs):
        login = ''
        try:
            json_data = request.jsonrequest
            _logger.error("Sign up process started with following datat: {0}".format(json_data))
            if len(json_data.get('mobile', "")):
                login = json_data.get('mobile')
            if not login and len(json_data.get('email', '')):
                login = json_data.get('email')

            qcontext = self.get_auth_signup_config()
            if not login:
                raise ValueError("Not enough values for signup")

            if 'error' not in qcontext.keys() and qcontext.get('signup_enabled', False) and login:
                qcontext.update(json_data)
                qcontext.update({
                    'login': login
                })
                self.do_signup(qcontext)
                user_data = self._get_app_login(login=login, password=json_data.get('password'))
                uid = request.env['res.users'].sudo().browse(user_data.get('uid'))
                uid.partner_id.write({
                    'email': json_data.get('email', ''),
                    'mobile': json_data.get('mobile', '')
                })
                request.env.cr.commit()
                return user_data
        except Exception as e:
            _logger.error("Error occured while sign up: {0}".format(e))
            return {
                'message': "{0}".format(e),
                'status_code': "4003"
            }


class Shop(Website):

    @http.route('/app/deals', type='json', auth='public', website=True)
    def get_app_deals(self):
        try:
            website_deals = request.env['website'].get_deals_offers()
            if not len(website_deals):
                raise ValueError(_("No deals available"))
            response = []
            for deal in website_deals:
                response.append({
                    'title': deal.deals_title,
                    'description': deal.description,
                    'deals_message_after_expiry': deal.deals_message_after_expiry,
                    'deals_message_before_expiry': deal.deals_message_before_expiry,
                    'offer_products': [
                        {
                            'id': offer.id,
                            'name': offer.product_tmpl_id.name,
                            'price': offer.fixed_price,
                            'image':'/web/image/product.template/{0}/image_128'.format(offer.product_tmpl_id.id),
                            'price_str': offer.price,
                        } for offer in deal.offers_products
                    ],
                })
            return {'result': response}
        except Exception as e:
            return {
                'message': e,
                'code': '4003',
            }

    @http.route('/app/home', type='http', auth='public', website=True)
    def get_home_page(self, **kwargs):
        """
        Render home page for App.
        :return: char, rendered home page template
        """
        if kwargs.get('from_app', False):
            return request.render('apty_api_app.home_page_content_app', {'from_app': True})

    @http.route('/app/shop/products', type='json', auth='public', website=True)
    def get_shop_products(self):
        json_data = request.jsonrequest
        offset = json_data.get('scroll_count', 0) * 10
        product_obj = request.env['product.product'].sudo()
        order = 'create_date'
        domain = [('active', '=', True)]
        if json_data.get('filter_by_category', False):
            domain += [('categ_id', 'in', json_data.get('categ_ids',[]))]
        if json_data.get('custom_search', False) and json_data.get('custom_search_keyword', False):
            domain += [('name', 'ilike', json_data.get('custom_search_keyword'))]
        if json_data.get('sort_by', False) :
            order = '{0}'.format(json_data.get('sort_by', False))
        product_obj = product_obj.search_read(domain=domain,
                                                fields=['id', 'display_name', 'lst_price'],
                                                offset=offset, limit=10, order=order)
        for product in product_obj:
            product.update({
                'image_url': '/web/image/product.product/{0}/image_128'.format(product['id'])
            })
        return {
            'products': product_obj,
            'categories': request.env['product.category'].sudo().search_read(fields=['name', 'id'])
        }
