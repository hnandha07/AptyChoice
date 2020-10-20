# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
##############################################################################

from odoo import fields, models, api, _
from odoo import SUPERUSER_ID
from datetime import date, time, datetime, timedelta

class websiteinherit(models.Model):
    _inherit = 'website'
    
    def get_deals_offers(self):  
        offers_ids=self.env['website.deals.offers'].search([('state', '=', 'progress')])

        deal_ids = []

        if offers_ids:
            for offer in offers_ids:
                DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
                now = str(datetime.now().replace(microsecond=0,second=0))
                current_time = datetime.strptime(now, DATETIME_FORMAT)
                start_date_offer = offer.start_date
                end_date_offer = offer.end_date
                if start_date_offer <= current_time and current_time <= end_date_offer:
                    deal_ids.append(offer)
            
            
            return deal_ids


    def get_current_pricelist(self):
        values = super(websiteinherit, self).get_current_pricelist()
        pricelist_deals = self.env['product.pricelist'].search([], limit=1, order="id desc")
        offers_ids=self.env['website.deals.offers'].search([('state', '=', 'progress')])
        if offers_ids:
            for i in offers_ids:
                for j in i.offers_products:
                    if i.end_date> datetime.now():
                        if j.date_end>date.today():
                            if i.offers_pricelist.id == pricelist_deals.id:
                                values= pricelist_deals
        else:
            values = super(websiteinherit, self).get_current_pricelist()
                
        return values

class ProductTemplate(models.Model):
    _inherit = ["product.template"]

    website_price = fields.Float('Website price', compute='_website_price', digits='Product Price')               

    def _website_price(self):
        current_website = self.env['website'].get_current_website()
        for template in self.with_context(website_id=current_website.id):
            res = template._get_combination_info()
            template.website_price = res.get('price')
            template.website_public_price = res.get('list_price')
            template.website_price_difference = res.get('has_discounted_price')
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:    