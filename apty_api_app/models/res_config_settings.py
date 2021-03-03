# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class RegionalPostalCode(models.Model):
    _name = 'regional.postal.code'
    _description = 'Postal Code for Regions'

    name = fields.Char(string="Region Code")


class RegionalDeliveryCharge(models.Model):
    _name = 'regional.delivery.charge'
    _description = 'Postal Code for Regions'

    regional_ids = fields.Many2many("regional.postal.code")
    delivery_charge = fields.Float(string="Delivery Charge")

    @api.onchange('regional_ids')
    def onchange_regional_ids(self):
        return {
            'domain': {
                'regional_ids': [('id', 'not in', self.search([]).mapped('regional_ids.id'))]
            }
        }

    def write(self, vals):
        zip_code_ids = vals.get('regional_ids')
        if zip_code_ids:
            delivery_charge_ids = self.search([]) - self
            for delivery_charge_id in delivery_charge_ids:
                if zip_code_ids[0] and len(zip_code_ids[0]) >= 3:
                    zip_code_list = zip_code_ids[0][2]
                    regional_ids = delivery_charge_id.regional_ids.ids
                    if any([zip_code in regional_ids for zip_code in zip_code_list]):
                        raise UserError(_("This zip code is already added in another delivery charge."))
        return super(RegionalDeliveryCharge, self).write(vals)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sms_api_key = fields.Char(string="SMS API Key")
    google_distance_url = fields.Char(string="Google Distance API")
    valid_regional_code_ids = fields.Many2many(comodel_name="regional.postal.code", string="Valid Regional Code", )
    order_delivery_charge = fields.Float(string="Default Regional Delivery Charge",
                                         related="company_id.order_delivery_charge", readonly=False)

    @api.model
    def get_values(self):
        conf_obj = self.env['ir.config_parameter'].sudo()
        res = super(ResConfigSettings, self).get_values()
        res.update({
            'sms_api_key':conf_obj.get_param('apty_api_app.sms_api_key'),
            'valid_regional_code_ids':[(6, 0 , eval(conf_obj.get_param('apty_api_app.valid_regional_code_ids','[]')))],
            'google_distance_url':conf_obj.get_param('apty_api_app.google_distance_url',''),
        })
        return res

    def set_values(self):
        self.env['ir.config_parameter'].sudo().set_param('apty_api_app.sms_api_key', self.sms_api_key)
        self.env['ir.config_parameter'].sudo().set_param('apty_api_app.valid_regional_code_ids',
                                                         self.valid_regional_code_ids.ids)
        self.env['ir.config_parameter'].sudo().set_param('apty_api_app.google_distance_url', self.google_distance_url)
        super(ResConfigSettings, self).set_values()


