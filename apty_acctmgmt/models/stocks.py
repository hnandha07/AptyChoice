# MODEL DEFINITION FOR Apty Choice APPLICATION
# ==========================================
#
# Base models
#
# Author: Nandhakumar
# Initiated date: 29-03-2020
#
# ==========================================

from odoo import models, fields, api, tools, _
from datetime import datetime, date, timedelta
import re
from odoo.exceptions import ValidationError, Warning
from dateutil.relativedelta import relativedelta
from time import gmtime, strftime
import pytz

class npa_products(models.Model):
    _name = 'npa.stock_details'
    _description = 'Apty Stock details table'
    _order = 'name'
    
    # Disable the DUPLICATE button    
    def copy(self):
        raise ValidationError("Sorry you are unable to duplicate records")

    # Perform a soft delete    
    def unlink(self):
        for rec in self:
            rec.active = False

    # field
    name = fields.Char(size=100,string='Stock Name')
    stock_code = fields.Char(size=80,string='Stock Code')
    stock_desc = fields.Text(string="Stock Description")
    category_id = fields.Many2one(comodel_name='npa.common_code',string='Stock Category',ondelete='restrict',domain="[('code_type','=','StockCategory')]")
    picture = fields.Binary(string='Picture',help='Attached picture will automatically be re-sized to 128x128px')
    picture_small = fields.Binary(string='Picture Small',compute='_reduce_customer_picture',store=True)    
    stock_price = fields.Float(string='Stock Price',digits=(15,2),default=0)
    last_price = fields.Float(string='Last Purchase Price',digits=(15,2),default=0)
    purchase_date = fields.Date(string="Last Purchase Date")
    purchase_qty = fields.Float(string='Last Purchase Quantity',digits=(5,2),default=0) 
    stock_gst = fields.Float(string='Stock Quantity',digits=(5,2),default=0)    
    stock_qty = fields.Float(string='Stock Quantity',digits=(5,2),default=0)    
    unit_type_id = fields.Many2one(comodel_name='npa.common_code',string='Unit Type',ondelete='restrict',domain="[('code_type','=','UnitId')]")
    active = fields.Boolean(string='Active',default=True)
    #Sql Constraints
    _sql_constraints = [('unique_stock_name','UNIQUE(name,active)','Stock name must be unique')]

class npa_stock_movement(models.Model):
    _name = 'npa.stock_moves'
    _description = 'Apty Stock Moves table'
    _order = 'date_moved desc'
    
    # Disable the DUPLICATE button    
    def copy(self):
        raise ValidationError("Sorry you are unable to duplicate records")

    # Perform a soft delete    
    def unlink(self):
        for rec in self:
            rec.active = False

    # get unit type
    @api.onchange('stock_id')
    def _onchange_unit_type(self): 
        if self.stock_id:                  
            unit_type = self.env['npa.stock_details'].search([('id','=',self.stock_id.id)],limit=1)
            stock_price_val = self.env['npa.purchase_list'].search([('stock_id','=',self.stock_id.id)],limit=1,order='id desc')                  
            if unit_type:
                self.unit_type_id=unit_type.unit_type_id.id 
            if  stock_price_val:
                self.stock_price=stock_price_val.stock_price                

    # get stock amount
    @api.onchange('stock_qty')
    def _onchange_stock_amount(self):        
        self.stock_amount=self.stock_price*self.stock_qty


    # field
    stock_id = fields.Many2one(comodel_name='npa.stock_details',string='Stock Name',ondelete='restrict')    
    reference = fields.Text(string="Stock Description")
    date_moved = fields.Date(string="Moved Date",default=lambda *a: datetime.now(pytz.timezone('Asia/Kolkata')).date().strftime('%Y-%m-%d'))
    stock_qty = fields.Float(string='Stock Quantity',digits=(5,2),default=0) 
    unit_type_id = fields.Many2one(comodel_name='npa.common_code',string='Unit Type',ondelete='restrict')
    stock_price = fields.Float(string='Stock Price',digits=(5,2))
    stock_amount = fields.Float(string='Stock Amount',digits=(5,2))
    active = fields.Boolean(string='Active',default=True)
    move_from = fields.Selection([
        ('Store Room', 'Store Room'),
        ('Kitchen', 'Kitchen')        
        ], string='Move From', default='Store Room')
    move_to = fields.Selection([
        ('Store Room', 'Store Room'),
        ('Kitchen', 'Kitchen')        
        ], string='Move To', default='Kitchen')