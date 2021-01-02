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


