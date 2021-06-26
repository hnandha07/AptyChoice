# -*- coding: utf-8 -*-
import requests, json
from pytz import timezone
from datetime import datetime, timedelta
from pprint import pprint, pformat
from odoo import http, _
from odoo.osv import expression
from odoo.http import request
from odoo.addons.website.controllers.main import Website
from odoo.exceptions import _logger
from odoo.addons.website_form.controllers.main import WebsiteForm
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.addons.website_sale.controllers.main import WebsiteSale

def _get_json_values(fields_to_check=[]):
    json_data = request.jsonrequest
    if not len(json_data) or (len(fields_to_check) and not all([json_data.get(ftc, False) for ftc in fields_to_check])):
        raise UserWarning("Not enough values {0}".format(json_data))
    return json_data

def _get_current_time():
    current_time = datetime.now(timezone('UTC')).astimezone(timezone('Asia/Kolkata'))
    return timedelta(hours=current_time.hour,minutes=current_time.minute).seconds/3600


class WebsiteSale(WebsiteSale):

    def check_unavailable_lines(self):
        status = False
        order = request.website.sale_get_order()
        if order.id and len(order.get_unavailable_lines()):
            status = True
        return status

    def checkout_form_validate(self, mode, all_form_values, data):
        res = super(WebsiteSale, self).checkout_form_validate(mode=mode, all_form_values=all_form_values, data=data)
        if len(all_form_values['zip']):
            pincode = request.env['regional.postal.code'].sudo().search([('name','=',all_form_values['zip'])])
            if not len(pincode.ids):
                res[0].update({
                    'zip': 'error'
                })
                res[1].append(_("We not started service to this area code."))
        else:
            res[0].update({'zip':'missing'})
        return res

    @http.route(['/shop/address'], type='http', methods=['GET', 'POST'], auth="public", website=True, sitemap=False)
    def address(self, **kw):
        if self.check_unavailable_lines():
            return request.redirect("/shop/cart")
        return super(WebsiteSale, self).address(**kw)


    @http.route(['/shop/payment'], type='http', auth="public", website=True, sitemap=False)
    def payment(self, **post):
        if self.check_unavailable_lines():
            return request.redirect("/shop/cart")
        return super(WebsiteSale, self).payment(**post)

    @http.route(['/shop/checkout'], type='http', auth="public", website=True, sitemap=False)
    def checkout(self, **post):
        if self.check_unavailable_lines():
            return request.redirect("/shop/cart")
        return super(WebsiteSale, self).checkout(**post)

    def _get_search_domain(self, search, category, attrib_values, search_in_description=True):
        res = super(WebsiteSale, self)._get_search_domain(search=search, category=category, attrib_values=attrib_values,
                                                          search_in_description=search_in_description)
        current_time = _get_current_time()
        return res + [('is_available', '=', True)]

    @http.route(['/apply/coupon'], type='json', auth="none")
    def apply_coupon(self):
        json_data = _get_json_values(fields_to_check=['order_id', 'promo'])
        order = request.env['sale.order'].sudo().browse(int(json_data.get('order_id')))
        promo = json_data.get('promo', '')
        status = {
            'status': False,
            'message': ''
        }
        if not len(promo):
            status['message'] = 'Invalid Promo Code'
            return status

        if order.id:
            if order.state == 'draft':
                coupon_status = request.env['sale.coupon.apply.code'].sudo().apply_coupon(order, promo)
                if len(coupon_status):
                    if coupon_status.get('not_found', False):
                        status['message'] = 'Invalid Promo Code'
                    elif coupon_status.get('error', False):
                        status['message'] = coupon_status.get('error')
                else:
                    status = {
                        'status': True,
                        'message': "Coupons Applied Successfully."
                    }
            else:
                status['message'] = 'Order is not in draft state'
        else:
            status['message'] = 'Order not found'
        return status

    @http.route('/app/zip/check', type='json', auth='none', cors="*")
    def check_zip_code(self):
        try:
            json_data = _get_json_values(fields_to_check=['pincode'])
            pincode = request.env['regional.postal.code'].sudo().search([('name','=',json_data.get('pincode'))])
            return {
                'status': len(pincode) and True or False
            }
        except Exception as e:
            _logger.info("Exception occurred while checking zip code {0}".format(e))
            return {
                'status': 2000,
                'message': e
            }

    @http.route('/app/address/list', type='json', auth='none', cors="*")
    def get_address_list(self):
        try:
            partner_address = []
            json_data = _get_json_values(fields_to_check=['user_id'])
            partner = request.env['res.users'].sudo().search([('id','=', int(json_data.get('user_id')))])
            if partner.id:
                partner = partner.partner_id
                partner_address.append(partner._get_address_values())
                for child in partner.child_ids.filtered(lambda x:x.type == 'delivery' and x.active == True):
                    partner_address.append(child._get_address_values())
                return partner_address
            else:
                raise UserWarning("User not found")
        except Exception as e:
            _logger.info("Exception occurred while checking preparing address: {0}".format(e))
            return {
                'status': 2000,
                'message': e
            }

    @http.route('/app/user/address', type='json', auth='none', cors="*", website=True)
    def app_user_address(self):
        try:
            json_data = {}
            if request.jsonrequest.get('mode', False) and request.jsonrequest.get('mode','') == 'new':
                json_data = _get_json_values(fields_to_check=['partner_id', 'mode', 'type', 'address'])
            if request.jsonrequest.get('mode', False) and request.jsonrequest.get('mode', '') == 'edit':
                json_data = _get_json_values(fields_to_check=['partner_id', 'mode', 'address'])
            else:
                json_data = _get_json_values(fields_to_check=['partner_id'])
            partner = request.env['res.partner'].sudo()
            values = json_data.get('address')
            status = False
            partner_id = partner.browse(int(json_data.get('partner_id')))
            if not partner_id.id:
                raise UserWarning("Partner not found")
            if json_data.get('mode') == 'delete':
                order = request.env['sale.order'].search([('partner_shipping_id','=',partner_id.id)])
                if not len(order.ids):
                    status = partner_id.unlink()
                else:
                    partner_id.active = False
                    status = not partner_id.active
            if json_data.get('mode') == 'new':
                values.update({
                    'company_id': False,
                    'lang': request.lang.code,
                    'country_id':request.env.ref('base.in').id,
                    'state_id':request.env.ref('base.state_in_tn').id,
                })
                if json_data.get('type') == 'shipping':
                    values.update({
                        'parent_id': partner_id.commercial_partner_id.id,
                        'type': 'delivery',
                    })
                ctx = request.env.context.copy()
                company_id = partner_id.company_id.id and partner_id.company_id.id or request.website.company_id.id
                ctx.update({
                    'mail_create_nosubscribe':True,
                    'force_company':company_id,
                })
                partner_id = partner.with_context(ctx).create(values).id
                status = bool(partner_id)
            elif json_data.get('mode') == 'edit':
                status = partner_id.write(values)
            if json_data.get('order_id', False):
                order = request.env['sale.order'].sudo().browse(int(json_data.get('order_id')))
                order.partner_shipping_id = partner_id.id
            return {
                'status': status
            }
        except Exception as e:
            _logger.info("Exception occurred while user address action: {0} - {1}".format(e, pprint(json_data)))
            return {
                'status': False,
                'message': e
            }

    @http.route('/app/order/history', type='json', auth='none', cors="*")
    def app_order_history(self):
        try:
            json_data = _get_json_values(fields_to_check=['user_id'])
            offset = json_data.get('scroll_count', 0) * 10
            user_id = request.env.user.browse(json_data.get('user_id'))
            if not user_id.id:
                return {
                    'status': 2002,
                    'message': "User id not found"
                }
            if json_data.get('order_id', False):
                order = request.env['sale.order'].sudo().browse(int(json_data.get('order_id')))
                if not order.id:
                    request
                    {
                        'status': 4004,
                        'message': "Order not found"
                    }
                return order._get_order_details()
            domain = [('partner_id', '=', user_id.partner_id.id)]
            order_obj = request.env['sale.order'].sudo()
            orders = order_obj.search_read(domain=domain,
                                                fields=['id', 'display_name', 'date_order', 'amount_total', 'state'],
                                                offset=offset, limit=10, order='create_date desc')
            return orders
        except Exception as e:
            return {
                'status': 2000,
                'message': e
            }

    @http.route('/app/order/cancel', type='json', auth='none', cors="*")
    def app_order_cancel(self):
        try:
            json_data = _get_json_values(fields_to_check=['order_id'])
            order = request.env['sale.order'].browse(json_data.get('order_id')).sudo()
            order.action_cancel()
            return order.state == 'cancel' and True or False
        except Exception as e:
            return {
                'status': 2000,
                'message': e
            }

    @http.route('/app/order', type='json', auth='none', cors="*", website=True)
    def app_add_order(self):
        try:
            json_data = _get_json_values(fields_to_check=['user_id','mode'])
            _logger.info("Values for App Order: {0}".format(json_data))
            values ={}
            mode = json_data.get('mode')
            ctx = request.env.context.copy()
            user = request.env['res.users'].sudo().browse(int(json_data.get('user_id')))
            if not user.id:
                return {
                    'status': 2000,
                    'message': 'User ID not found in the request {}'.format(json_data)
                }
            if mode == 'set_shipping_partner':
                json_data = _get_json_values(fields_to_check=['order_id', 'partner_id'])
                order = request.env['sale.order'].browse(int(json_data.get('order_id'))).sudo()
                if not order.id:
                    raise UserWarning("Order not found")
                values.update({
                    'partner_shipping_id':int(json_data.get('partner_id'))
                })
            order_lines = []
            if mode == 'new':
                request.session.sale_order_id = False
                order = request.website.with_user(user=user).sale_get_order(force_create=1)
            elif mode == 'edit':
                order = request.env['sale.order'].browse(int(json_data.get('order_id'))).sudo()
            if not order.id:
                raise UserWarning("Order not found")
            if len(json_data.get('order_line_details',[])):
                order_lines = order.prepare_order_lines(ol_details= json_data.get('order_line_details',[]))
                values={
                    'order_line': order_lines
                }
            if len(json_data.get('delivery_date', '')):
                values.update({
                    'commitment_date': json_data.get('delivery_date')
                })
            if order and order.partner_id and mode == 'new': 
                if not order.partner_id.coupon_used:
                    discount_product = request.env['product.product'].sudo().search([('name', 'ilike', 'discount')], limit=1, order='id desc')
                    order_line = {
                        'product_id': discount_product.id,
                        'product_uom_qty': 1,
                        'price_unit': -100,
                        'price_subtotal': -100
                    }
                    order.write({
                        'order_line': [(0, 0, order_line)]
                    })
            ctx.update({
                'force_company': order.company_id.id,
                'allowed_company_ids':[order.company_id.id]
            })
            request.env.user = user
            order.sudo().with_context(ctx).write(values)
            return {
                'order_id': order.id,
            }
        except Exception as e:
            return {
                'status': 2000,
                'message': e
            }

class WebsiteForm(WebsiteForm):
    @http.route('/app/contactus', type='json', auth='public')
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
                'partner_id': uid.partner_id.id,
                'mobile': uid.partner_id.phone and uid.partner_id.phone or uid.partner_id.mobile,
                'email': uid.partner_id.email,
                'name': uid.name,
            }
        return False

    @http.route('/app/change/password', type='json', auth='public')
    def change_user_password(self):
        try:
            json_data = _get_json_values(fields_to_check=['login', 'request_type','password'])
            request_type  = json_data.get('request_type', False)
            login = json_data.get('login', False)
            user = request.env['res.users'].sudo().search([('login', '=', login)])
            if not user.id:
                raise UserWarning("User not found: {}:".format(user))
            if request_type == 'match':
                status = 1
                try:
                    user.with_user(user.id)._check_credentials(password=json_data.get('password'))
                except Exception as e:
                    _logger.info("Exception raise during password match {0}".format(e))
                    status = 0
                return {
                    'status': status
                }
            if request_type == 'update':
                update_status = user.write({'password': json_data.get('password')})
                return {
                    'status': int(update_status)
                }
        except Exception as e:
            return {
                'message': e,
                'status_code': '4002'
            }

    @http.route('/app/login', type='json', auth='public')
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

    @http.route('/app/mobile/verification', type='json', auth='public')
    def mobile_verification(self, **kwargs):
        try:
            json_data = _get_json_values(fields_to_check=['mobile','request_type'])
            if len(json_data):
                sms_api_key = request.env['ir.config_parameter'].sudo().get_param('apty_api_app.sms_api_key', False)
                if not sms_api_key or not len(sms_api_key):
                    _logger.info("SMS API Key is not set, Please set for mobile number verification")
                    raise UserWarning("Something went wrong")

                url = "https://2factor.in/API/V1"
                if json_data.get('autogen', False):
                    if not json_data.get('mobile', False):
                        raise UserWarning("Not enough values for verification")

                    users = request.env['res.users'].sudo().search([('login', '=', json_data.get('mobile'))])

                    if json_data.get('request_type','') == 'signup' and len(users.ids):
                        raise UserWarning("User already exists with this mobile number")

                    if json_data.get('request_type','') == 'password' and not len(users.ids):
                        raise UserWarning("User does not found with this mobile number")

                    url = '{0}/{1}/SMS/+91{2}/AUTOGEN'.format(url, sms_api_key, json_data.get('mobile'))

                elif json_data.get('verify', False):
                    if not json_data.get('session_id', False) and not json_data.get('otp', False):
                        raise UserWarning("Not enough values for verification")
                    url = '{0}/{1}/SMS/VERIFY/{2}/{3}'.format(url, sms_api_key, json_data.get('session_id'),
                                                              json_data.get('otp'))
                response = requests.request("GET", url, headers={}, data={})
                return json.loads(response.text)
        except Exception as e:
            return {
                'message': "{0}".format(e),
                'status_code': "4003"
            }

    @http.route('/app/email/check', type='json', auth='public')
    def app_email_check(self):
        try:
            json_data = _get_json_values(fields_to_check=['email'])
            return {
                'status': not len(request.env.user.partner_id.search([('email', '=', json_data.get('email'))]))
            }
        except Exception as e:
            return {
                'message': "{0}".format(e),
                'status_code': "4003"
            }

    @http.route('/app/profile/edit', type='json', auth='public')
    def app_edit_profile(self):
        try:
            json_data = _get_json_values(fields_to_check=['values'])
            user = request.env.user.browse(int(json_data.get('user_id')))
            if not user.id:
                raise UserWarning("User not found")
            res = user.partner_id.write(json_data.get('values'))
            return {
                'status': res
            }
        except Exception as e:
            return {
                'message': "{0}".format(e),
                'status_code': "4003"
            }

    @http.route('/app/signup', type='json', auth='public')
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
                user_data.update({
                    'email':uid.partner_id.email,
                    'mobile':uid.partner_id.mobile,
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

    @http.route('/app/deals', type='json', auth='public')
    def get_app_deals(self):
        try:
            website_deals = request.env['website'].get_deals_offers()
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
                            'product_id':offer.product_tmpl_id.id,
                            'name': offer.product_tmpl_id.name,
                            'price': offer.fixed_price,
                            'image': '/web/image/product.template/{0}/image_128'.format(offer.product_tmpl_id.id),
                            'availability_time_start': offer.product_tmpl_id.availability_time_start,
                            'availability_time_end': offer.product_tmpl_id.availability_time_end,
                            'price_str': offer.price,
                            'description_sale':offer.product_tmpl_id.description_sale,
                            'is_available': offer.product_tmpl_id.availability_time_start <
                                            _get_current_time() < offer.product_tmpl_id.availability_time_end,
                        } for offer in deal.offers_products
                    ],
                })
            return response
        except Exception as e:
            return {
                'message': e,
                'code': '4003',
            }

    @http.route('/app/aboutus', type='http', auth='public', website=True)
    def get_about_us(self, **kwargs):
        """
        Render Home Page for App
        :param kwargs:
        :return:
        """
        return request.render('website.aboutus',{'for_mobile':'d-none','display_remove':False})

    @http.route('/app/home', type='json', auth='public')
    def get_home_page(self, **kwargs):
        """
        Render home page for App.
        :return: char, rendered home page template
        """
        result = request.env['npa.document'].sudo().search_read([('doc_class_id.code', '=', 'DOCHOME')],
                                                                   ['document_sub_type', 'name', 'notes'])
        [r.update(image_url='/web/image/npa.document/{0}/doc_image'.format(r['id'])) for r in result]
        return {'data':result}

    @http.route('/app/payment', type='json', auth='public')
    def app_payment(self, **kwargs):
        try:
            json_data = _get_json_values(fields_to_check=['order_id','payment_provider'])
            payment_type = json_data.get('payment_provider')
            order = request.env['sale.order'].sudo().browse(int(json_data.get('order_id')))
            if not order.id:
                raise UserWarning("Order not found")
            partner_country_id = order.partner_id.country_id.id
            partner_country_ifcd = partner_country_id and partner_country_id or order.company_id.country_id.id
            acquirer_id = request.env['payment.acquirer'].sudo().search([('provider','=',payment_type)])
            if not acquirer_id.id:
                raise UserWarning("Payment Acquirer not found")
            payment_tx_id = request.env['payment.transaction']
            py_transc = order._create_payment_transaction(
                vals={'acquirer_id': acquirer_id.id, 'partner_country_id': partner_country_id})
            payment_values = {}
            if py_transc.id:
                if payment_type == 'cash_on_delivery':
                    order.action_confirm()
                    order._create_invoices()
                    py_transc = False
                elif payment_type == 'paytm':
                    payment_values = acquirer_id._prepare_app_values(order_id=order, transaction=py_transc)
                    method = getattr(acquirer_id, '{0}_form_generate_values'.format(acquirer_id.provider))
                    payment_values = method(payment_values, CHANNEL_ID='WAP')
                    payment_tx_id = py_transc
                    py_transc = py_transc.id
            order.write({'payment_acquirer_id':acquirer_id.id})
            return {
                'status': 2000,
                'payment_tx_id': payment_tx_id.id,
                'request_values':payment_values,
                'payment_tx_id': py_transc,
            }
        except Exception as e:
            _logger.info("Exception occurred while initiating app payment - {0}-{1}".format(e, json_data))
            return {
                'status': 2001,
                'result': e
            }

    @http.route('/app/shop/products', type='json', auth='public')
    def get_shop_products(self):
        json_data = request.jsonrequest
        fields = ['id', 'display_name', 'lst_price', 'availability_time_start', 'availability_time_end',
                  'description_sale']
        offset = json_data.get('scroll_count', 0) * 10
        product_obj = request.env['product.product'].sudo()
        order = 'create_date'
        domain = [('active', '=', True),('is_available','=', True), ('is_published', '=', True)]
        if json_data.get('filter_by_category', False):
            domain += [('categ_id', 'in', json_data.get('categ_ids',[]))]
        if json_data.get('custom_search', False) and json_data.get('custom_search_keyword', False):
            domain += [('name', 'ilike', json_data.get('custom_search_keyword'))]
        if json_data.get('sort_by', False) :
            order = '{0}'.format(json_data.get('sort_by', False))
        product_obj = product_obj.search_read(domain=domain, fields=fields,
                                              offset=offset, limit=10, order=order)
        for product in product_obj:
            is_available = False
            start_time = product['availability_time_start']
            end_time = product['availability_time_end']
            if start_time < _get_current_time() < end_time :
                is_available = True
            product.update({
                'image_url': '/web/image/product.product/{0}/image_128'.format(product['id']),
                'is_available': is_available
            })
        return {
            'products': product_obj,
            'categories': request.env['product.category'].sudo().search_read([('app_allowed', '=', True)], fields=['name', 'id'])
        }
