# -*- coding: utf-8 -*-

from odoo import fields, models, api


class RegionalPostalCode(models.Model):
    _name = 'regional.postal.code'
    _description = 'Postal Code for Regions'

    name = fields.Char(string="Region Code")


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sms_api_key = fields.Char(string="SMS API Key")
    valid_regional_code_ids = fields.Many2many(comodel_name="regional.postal.code", string="Valid Regional Code", )

    @api.model
    def get_values(self):
        conf_obj = self.env['ir.config_parameter'].sudo()
        res = super(ResConfigSettings, self).get_values()
        res.update({
            'sms_api_key':conf_obj.get_param('apty_api_app.sms_api_key'),
            'valid_regional_code_ids':[(6, 0 , eval(conf_obj.get_param('apty_api_app.valid_regional_code_ids','[]')))]
        })
        return res

    def set_values(self):
        self.env['ir.config_parameter'].sudo().set_param('apty_api_app.sms_api_key', self.sms_api_key)
        self.env['ir.config_parameter'].sudo().set_param('apty_api_app.valid_regional_code_ids', self.valid_regional_code_ids.ids)
        super(ResConfigSettings, self).set_values()

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _get_order_details(self):
        order_lines = [{'product_id': ol.product_id, 'product_name': ol.product_id.name, 'qty': ol.product_uom_qty,
                        'price': ol.price, 'sub_total': ol.sub_total} for ol in self.order_lines]
        return {
            'state': self.state,
            'total': self.amount_total,
            'order_lines': order_lines
        }
