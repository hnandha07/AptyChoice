## -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
##############################################################################

from odoo import fields, models, api, _
from odoo import SUPERUSER_ID
from datetime import datetime, timedelta

class website_deals_offers(models.Model):
    _name='website.deals.offers'


    @api.model
    def default_pricelist_on_deals(self):
        pricelist_deals = self.env['product.pricelist'].search([], limit=1, order="id desc")
        return pricelist_deals    
        
        
    name  =  fields.Char('Deals Name')
    title = fields.Char('Deals Title')
    start_date = fields.Datetime(string='Start Date', required=True)
    end_date = fields.Datetime(string='End Date', required=True)
    
    offers_pricelist = fields.Many2one('product.pricelist', string='Pricelist', default=default_pricelist_on_deals, required=True)
    offers_products = fields.One2many('product.pricelist.item', 'offers_pricelist_id', string='product Pricelist')
    description = fields.Text('Description')
    banner = fields.Binary(string="Banner")
    show_deals_header = fields.Boolean(string='Show Deals Header', default=True)
    deals_title = fields.Char('Deals Title')
    
    what_to_show = fields.Selection([
        ('banner_only', 'Banner Only'),
        ('products_only', 'Products Only'),
        ('both', 'Both'),
        ], string='What to Display in Deals', default='both')
        
    display_deals_as = fields.Selection([
        ('grid', 'Grid'),
        ('slider', 'Slider'),
        ('attractive', 'Attractive'),
        ], string='How to Display Deals', default='grid')   

    show_deals_message_before_expiry = fields.Boolean(string='Show Deals Message Before Expiry', default=True)
    deals_message_before_expiry = fields.Char('Deals Message Before Expiry')
    
    show_deals_message_after_expiry = fields.Boolean(string='Show Deals Message After Expiry', default=True)     
    deals_message_after_expiry = fields.Char('Deals Message After Expiry')
      
    state = fields.Selection([
        ('draft', 'Draft'),
        ('progress', 'In Progress'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, track_visibility='onchange', default='draft')        



    def button_validate_the_deal(self):
        self.state='progress'      
        
    def cancel_the_deal(self):
        self.state='cancel'  

        
        
class product_pricelist_item(models.Model):
    _inherit='product.pricelist.item'

    offers_pricelist_id = fields.Many2one('website.deals.offers', string='Offers Pricelist')

    @api.model
    def create(self,vals):
        offers = self.env['website.deals.offers'].search([])
        if offers:
            deal = self.env['website.deals.offers'].browse(vals['offers_pricelist_id'])
            if deal:
                vals['pricelist_id'] = deal.offers_pricelist.id
                vals['date_start'] = deal.start_date.strftime("%Y-%m-%d")
                vals['date_end'] = deal.end_date.strftime("%Y-%m-%d")
            return super(product_pricelist_item,self).create(vals)
        else:
            res = super(product_pricelist_item,self).create(vals)
            if res.offers_pricelist_id:
                deal = self.env['website.deals.offers'].browse(res.offers_pricelist_id)
                if deal:
                    res.pricelist_id = deal.offers_pricelist.id
                    res.date_start = deal.start_date.strftime("%Y-%m-%d")
                    res.date_end = deal.end_date.strftime("%Y-%m-%d")
            return res
        
            
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:    