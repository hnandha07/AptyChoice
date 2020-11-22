# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sms_api_key = fields.Char(string="SMS API Key")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            sms_api_key=self.env['ir.config_parameter'].sudo().get_param('apty_api_app.sms_api_key'),
        )
        return res

    def set_values(self):
        self.env['ir.config_parameter'].sudo().set_param('apty_api_app.sms_api_key', self.sms_api_key)
        super(ResConfigSettings, self).set_values()
