# -*- coding: utf-8 -*-

import json
from math import floor
from urllib.parse import urlencode
from requests import request as py_request
from odoo.tools.safe_eval import safe_eval
from odoo import fields, models, api, _
from odoo.exceptions import _logger
from ..controllers.main import _get_current_time


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    payment_acquirer_id = fields.Many2one("payment.acquirer", string="Payment Acquirer")
    order_delivery_charge = fields.Float(string="Delivery Charge")

    @api.model
    def _get_order_details(self):
        delivery_product = self.env.ref('delivery.product_product_delivery_product_template').id
        order_lines = [{'product_id': ol.product_id.id,
                        'product_image': '/web/image/product.product/{0}/image_128'.format(ol.product_id.id),
                        'product_name': ol.product_id.name, 'qty': ol.product_uom_qty,
                        'price': ol.price_unit, 'sub_total': ol.price_subtotal} for ol in
                       self.order_line.filtered(lambda x: x.product_id.product_tmpl_id.id != delivery_product)]
        return {
            'state': self.state,
            'order_lines': order_lines,
            'amount_untaxed': self.amount_untaxed,
            'taxes': self.amount_tax,
            'total': self.amount_total,
            'delivery_charge': self.order_delivery_charge
        }

    def get_google_distance(self, partner_cords=[], company_cords=[]):
        if len(partner_cords) == 2 and len(company_cords) == 2:
            config_obj = self.env['ir.config_parameter'].sudo()
            api_key = config_obj.get_param('base_geolocalize.google_map_api_key', '')
            api_url = config_obj.get_param('apty_api_app.google_distance_url', '')
            if not all([len(api_url), len(api_key)]):
                raise ("Configuration missing for google distance API key-{0} ---- URL-{1}".format(api_key, api_url))
            query_string = urlencode({
                'key': api_key,
                'units': 'metric',
                'origins': ','.join(company_cords),
                'destinations': ','.join(partner_cords),
            })
            google_map_url = "{}?{}".format(api_url, query_string)
            response = py_request("GET",url=google_map_url, data={}, headers={})
            if response.status_code:
                json_response = json.loads(response.text)
                _logger.info("Google Distance API response:{0}".format(json_response))
                response_distance = []
                rows = json_response.get('rows')
                for row in rows:
                    response_distance.append(self._get_rows_distance(row))
                return min(response_distance)

    def _get_rows_distance(self, row=False):
        return row['elements'][0]['distance']['value']

    def calc_distance_amt(self, geo_distance=0):
        amount = 0
        if geo_distance > 0:
            delivery_config = self.env.ref('npa_base.npa_config_delivery', raise_if_not_found=False)
            if delivery_config.id:
                for record in range(1, 4):
                    condition = getattr(delivery_config, 'parm{}'.format(record),'').lower()
                    if len(condition) and 'km' in condition:
                        condition = condition.replace('km', str(geo_distance))
                        result = safe_eval(condition)
                        if result:
                            amount = getattr(delivery_config,'amt{}'.format(record),0)
                            break;
        return amount

    def get_shipping_amount(self, partner_id=False):
        try:
            if partner_id and partner_id.id:
                delivery_charge = self.env['regional.delivery.charge'].search(
                    [('regional_ids.name', '=', partner_id.zip)], limit=1)

                if not delivery_charge:
                    delivery_charge = self.company_id.order_delivery_charge
                else:
                    delivery_charge = delivery_charge.delivery_charge

                return delivery_charge
                # partner_id.geo_localize()
                # search_cords = self.partner_id.search_read([('id', 'in', [partner_id.id, self.company_id.partner_id.id])],
                #                                            ['partner_latitude', 'partner_longitude'],order='id asc')
                # partner_cords = [str(search_cords[-1].get(sco)) for sco in ['partner_latitude','partner_longitude']]
                # company_cords = [str(search_cords[0].get(sco)) for sco in ['partner_latitude','partner_longitude']]
                # geo_distance = self.get_google_distance(partner_cords=partner_cords,company_cords=company_cords)
                # geo_distance = geo_distance/1000
                # return self.calc_distance_amt(geo_distance=geo_distance) * floor(geo_distance)
        except Exception as e:
            _logger.info("Exception occurred while getting distance {0}".format(e))
            return 0

    def write(self, values):
        if values.get('state',False):
            if values.get('state') not in  ['sale','done']:
                values.update({
                    'apty_order_state':'draft'
                })
        res = super(SaleOrder, self).write(values)
        if values.get('partner_shipping_id', False):
            for record in self:
                partner = record.partner_shipping_id.browse(values.get('partner_shipping_id'))
                if not partner.id:
                    _logger.info("Could not find the partner for the order.")

                delivery_price = self.get_shipping_amount(partner_id=partner)
                delivery_product = self.env.ref('delivery.product_product_delivery_product_template')
                delivery_line = self.order_line.filtered(
                    lambda x: x.product_id.product_tmpl_id.id == delivery_product.id)
                if not delivery_line.id:
                    delivery_line.create({
                        'product_id': delivery_product.product_variant_ids.id,
                        'product_uom_qty': 1.0,
                        'price_unit': delivery_price,
                        'order_id': record.id,
                    })
                else:
                    delivery_line.write({
                        'price_unit': delivery_price
                    })
        return res

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        self.write({
            'apty_order_state':'order',
        })
        return res

    @api.model
    def get_unavailable_lines(self):
        lines = []
        try:
            for ol in self.order_line.filtered(lambda x: x.product_id.id != self.env.ref(
                    self.env.ref('delivery.product_product_delivery_product_template').id)):
                if not (
                        ol.product_id.availability_time_start < _get_current_time() < ol.product_id.availability_time_end):
                    lines.append(ol.id)
        except Exception as e:
            _logger.info("Exception occurred while preparing unavailable lines {}".format(e))
        return lines

    def prepare_order_lines(self, ol_details=[]):
        order_lines = []
        if len(ol_details) and self.id:
            if not len(self.order_line):
                for old in ol_details:
                    order_lines.append((0,0,{
                        'product_id':old.get('product_id'),
                        'product_uom_qty':old.get('qty'),
                    }))
            else:
                for old in ol_details:
                    product = old.get('product_id')
                    write_action = 3
                    ol = self.order_line.filtered(lambda x:x.product_id.id == product).id
                    if ol:
                        write_action = 1
                    if not ol:
                        write_action, ol = 0, 0
                    values = {'product_id':product,'product_uom_qty':old.get('qty')}
                    order_lines.append((write_action,ol,values))
                check_product_ids = map(lambda x:x.get('product_id'),ol_details)
                remove_lines = self.order_line.filtered(lambda x:x.product_id.id not in check_product_ids)
                if len(remove_lines.ids):
                    _logger.info(
                        "Removing order lines - {0} with product - {1} for order - {2}".format(remove_lines.mapped('id'),
                                                                                               remove_lines.mapped(
                                                                                                   'product_id.name'),
                                                                                               self.name))

                    order_lines += [(2, rol.id) for rol in remove_lines]
        return order_lines


class PaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'

    def _prepare_app_values(self, order_id=False, transaction=False):
        if order_id and transaction:
            return {
                'reference': transaction.reference,
                'partner_id': order_id.partner_id.id,
                'amount':order_id.amount_total,
                'partner_email':order_id.partner_id.email,
                'partner_phone':order_id.partner_id.phone
            }
