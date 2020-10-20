# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools


class OdooDebrand(models.Model):
    """
     Fields to access from the database manager.
    """
    _inherit = "website"

    def get_company_logo(self):
        self.company_logo_url ="/web/image/res.company/%s/logo"%(self.id)

    def get_favicon(self):
        id = self.env['website'].sudo().search([])
        self.favicon_url ="/web/image/website/%s/favicon"%(id[0].id)

    favicon_url = fields.Text("Url", compute='get_favicon')
    company_logo_url = fields.Text("Url", compute='get_company_logo')
