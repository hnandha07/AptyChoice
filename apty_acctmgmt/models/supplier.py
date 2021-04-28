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
from dateutil.relativedelta import relativedelta 
from time import gmtime, strftime
import pytz
from odoo.exceptions import ValidationError, Warning
 

class staff_details(models.Model):
    _name = 'npa.supplier_details'
    _description = 'Supplier details table'

    @api.onchange('country_id')
    def _onchange_country_id(self):
        if self.country_id:
            ids = self.env['res.country.state'].search([('country_id', '=', self.country_id.id)])
            return {
                'domain': {'state_id': [('id', 'in', ids.ids)],}
            }
        else:
            self.state_id=False   

    # Returns the default country
    @api.model
    def _get_default_country(self):
        config_rec = self.env['npa.config'].search([('code_type','=','Sys'),('code','=','DftCountry')],limit=1)
        if config_rec:
            country_rec = self.env['res.country'].search([('code','=',config_rec.parm1)],limit=1)
            if country_rec:
                return country_rec.id
        return

    # Returns age of staff    
    def _compute_birth_years(self):
        for rec in self:
            if rec.date_of_birth:
                s = datetime.strptime(str(rec.date_of_birth),'%Y-%m-%d')
                final = str(relativedelta(datetime.now(), s).years)+' Years'
                rec.staff_age = final
            if rec.create_date:
                s1=datetime.strptime(str(rec.create_date).split('.')[0],"%Y-%m-%d %H:%M:%S")
                final1 = str(s1.strftime('%Y-%m-%d %H:%M:%S'))+'('+str(relativedelta(datetime.now(), s1).years)+' Years,'+str(relativedelta(datetime.now(), s1).months)+' Months,'+str(relativedelta(datetime.now(), s1).days)+' Days)'
                rec.customer_since = final1

    # This function will derive a address field suitable for showing on display or report
    @api.depends('address1','address2','city','zip_code','state_id','country_id')
    def _get_publication_address(self):
        for rec in self:
            if rec.address1:
                addr = rec.address1
                if rec.address2:
                    addr = addr+u',\n'+rec.address2               
                if rec.city:
                    addr = addr+u',\n'+rec.city
                if rec.zip_code:
                    addr = addr+u',\nPostcode '+rec.zip_code
                if rec.state_id:
                    addr = addr+u',\n'+rec.state_id.name
                if rec.country_id:
                    addr = addr+u',\n'+rec.country_id.name
            else:
                addr = u''
                                                    
            rec.display_address = addr

    #field Validation
    @api.constrains("email")
    def customer_field_validation(self):
        for rec in self:
            if rec.email:
                if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,}|[0-9]{1,3})(\\]?)$", rec.email) == None:
                    raise ValidationError ("Invalid email address. Please enter a valid email address!")

    # Disable the DUPLICATE button    
    def copy(self):
        raise ValidationError("Sorry you are unable to duplicate records")

    # Perform a soft delete
    def unlink(self):
        for rec in self:
            rec.active = False

    # fields
    name = fields.Char(string='Supplier Name',index=True)
    code = fields.Char(string='Supplier Code')
    designation = fields.Selection([
        ('Admin', 'Admin'),
        ('Manager', 'Manager'),
        ('Delivery Boy', 'Delivery Boy'),
        ('Junior Chef', 'Junior Chef'),
        ('Senior Chef', 'Senior Chef'), 
        ('Clerk', 'Clerk'),      
        ], string='Designation', default='Admin')
    address1 = fields.Char(string='Address line 1')    
    address2 = fields.Char(string='Address line 2')
    city = fields.Char(string='City') 
    zip_code = fields.Char(string='Zipcode or Pincode') 
    state_id = fields.Many2one(comodel_name='res.country.state', string='State',ondelete='restrict')
    country_id = fields.Many2one(comodel_name='res.country', readonly="1", string='Country',ondelete='restrict',default=_get_default_country)    
    display_address = fields.Char(string='Publication Address',compute='_get_publication_address',store=True)
    phone_num1 = fields.Char(string='Phone Number') 
    phone_num2 = fields.Char(string='Alternate Number')
    mobile_num1 = fields.Char(string='Mobile Number1') 
    mobile_num2 = fields.Char(string='Mobile Number2')
    whatsapp_num = fields.Char(string='WhatsApp Number')
    web_site = fields.Char(string='Web Site')
    email = fields.Char(string='eMail Address')
    contact_person1 = fields.Char(string='Contact Person')
    person1_phone_num = fields.Char(string='Person1 Phone Num')
    contact_person2 = fields.Char(string='Contact Person2')
    person2_phone_num = fields.Char(string='Person2 Phone Num')
    date_of_birth = fields.Date(string='Date of birth')
    customer_since = fields.Char(store=False, compute="_compute_birth_years")
    staff_age = fields.Char(string='Age', compute="_compute_birth_years")
    gender = fields.Selection([
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('N/A', 'Not applicable'),
        ], string='Gender', default='Male')
    marital_status = fields.Selection([
        ('Single', 'Single'),
        ('Married', 'Married'),        
        ], string='Marital status', default='Single')
    geolocation = fields.Char(string='Geo location',help='This can be a GPS location or some map reference')
    geopicture = fields.Binary(string='Picture of geolocation',help='This is the picture of the location.  Can be screen capture of map.')
    picture = fields.Binary(string='Picture',help='Attached picture will automatically be re-sized to 128x128px')
    picture_small = fields.Binary(string='Picture small',compute='_reduce_customer_picture',store=True)
    national_id_no = fields.Char(size=20,string='Naitional ID number',index=True)
    national_id_type_id = fields.Many2one(comodel_name='npa.common_code',string='Naitional ID type',ondelete='restrict',domain="[('code_type','=','IdType')]")
    national_id_expiry = fields.Date(string='National ID expiry')
    other_id_no = fields.Char(size=20,string='Other ID number',index=True)
    other_id_type_id = fields.Many2one(comodel_name='npa.common_code',string='Other ID type',ondelete='restrict',domain="[('code_type','=','IdType')]")
    other_id_expiry = fields.Date(string='Other ID expiry date')
    route_id = fields.Many2one(comodel_name='npa.common_code',string='Route Name',domain="[('code_type','=','RouteDetails')]")
    login_domain = fields.Many2one(comodel_name='res.users',string='Login Domain')
    document_ids= fields.One2many(comodel_name='npa.document',inverse_name='supplier_id',string='Document Details')
    active = fields.Boolean(string='Active',default=True)    
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id) 
    # doc_ids= fields.One2many(comodel_name='npa.document',inverse_name='supplier_id',string='Document Details')   

    # SQL constraint
    _sql_constraints = [('unique_lookup_code','UNIQUE(name,active)','Supplier name must be unique')] 

# Model for CUSTOMER LOGIN table
# This model is to store the login information for each customer.
# Login information is further separated by domain.  There would be at least one login domain (e.g. for member-site)
# Targeted number of records: Large - average 1 record per customer

class npa_expenses(models.Model):
    _name = 'npa.expense_details_hdr'
    _description = 'Apty Expense details table'
    _order = 'name'    
    
    # Disable the DUPLICATE button    
    def copy(self):
        raise ValidationError("Sorry you are unable to duplicate records")

    # Perform a soft delete    
    def unlink(self):
        for rec in self:
            rec.active = False

    # Returns age of staff 
    api.depends('to_date','from_date')    
    def _compute_days(self):
        for rec in self:        
            if rec.from_date and rec.to_date:
                dur = rec.to_date - rec.from_date
                rec.age = dur.days + 1

    # Method to payment wizard
    def create_service_payment(self):
        mod_obj = self.env['ir.model.data']
        form_res = mod_obj.get_object_reference('apty_acctmgmt', 'view_shop_payment_form')[1]
        return{
            'name': "Create Payment",
			   'view_type': 'form',
			   'view_mode':"[form]",
			   'view_id': form_res,
			   'res_model': 'npa.shop_payment_amt',
			   'type': 'ir.actions.act_window',
			   'views': [(form_res, 'form')],
			   'target': 'new',
			   'context':{'default_service_id':self.id}
        }        

    # Method to post purchase request
    def get_service_request_wizard(self):
        try:
            form_id = self.env['ir.model.data'].get_object_reference('apty_acctmgmt', 'post_service_request_wizard')[1]
        except ValueError:
            form_id = False
            raise Warning(_("Cannot locate required 'post_service_request_wizard'. Please contact IT Support"))
        return{
                    'name': "Post Service Transaction",
                    'view_type': 'form',
                    'view_mode':"[form]",
                    'view_id': False,
                    'res_model': 'npa.common_wizard',
                    'type': 'ir.actions.act_window',
                    'target':'new',
                    'views': [(form_id, 'form')],
                    }
    
    @api.model
    def create(self, vals):
        if not vals:
            vals = {}        
        vals['name'] = self.env['ir.sequence'].\
            next_by_code('npa.expense_details_hdr') or 'New'
        return super(npa_expenses, self).create(vals)

    # Calculate total transaction and total payment amount
    @api.depends('expense_ids.service_amt','payment_ids.payment_amt')
    def _compute_total_amt(self):
        total_amt = 0.0
        total_payment = 0.0
        for record in self:
            for line in record.expense_ids:
                total_amt += line.service_amt
            for line in record.payment_ids:
                total_payment += line.payment_amt
            print('****** payment total',total_payment)
            record.total_service_amt = total_amt
            record.payment_amt = total_payment
            record.amount_residual = total_amt - total_payment
                    

    # field
    name = fields.Char(size=80,string='Service Order',readonly=True, required=True, copy=False, default='New')
    service_name = fields.Char(size=80,string='Service Name') 
    from_date = fields.Date(string="From date/time")
    to_date = fields.Date(string="To date/time")    
    age = fields.Integer(string='No. Of Days', readonly=True, store=False)
    service_desc = fields.Text(string="Service Description")    
    active = fields.Boolean(string='Active',default=True)
    expense_ids = fields.One2many(comodel_name='npa.expense_details_sumry',inverse_name='service_id', string='Services')
    payment_ids=fields.One2many(comodel_name='npa.shop_payment_amt', inverse_name='service_id', string='Payment Amount') 
    date_posted = fields.Date(string='Posted Date')
    posted_by = fields.Many2one(comodel_name='res.users',string='Posted by',ondelete='restrict')
    total_service_amt = fields.Float(string='Total Amount',digits=(5,2),compute='_compute_total_amt',store=True)
    payment_amt = fields.Float(string='Amount Paid',digits=(5,2),compute='_compute_total_amt',store=True)
    amount_residual = fields.Float(string='Amount Due',digits=(5,2),compute='_compute_total_amt',store=True)   
    state = fields.Selection([
        ('New', 'New'),
        ('Posted', 'Posted'),
        ('Cancel', 'Cancel'),
        ], string='State', default='New')

class npa_expenses_summary(models.Model):
    _name = 'npa.expense_details_sumry'
    _description = 'Apty Expense summary table'        
    
    # Disable the DUPLICATE button    
    def copy(self):
        raise ValidationError("Sorry you are unable to duplicate records")

    # Perform a soft delete    
    def unlink(self):
        for rec in self:
            rec.active = False

    #Service Amount calculation
    @api.depends('service_cost','service_qty', 'service_gst')
    def _compute_service_amt(self):
        for rec in self:            
            ser_amt = rec.service_cost * rec.service_qty
            ser_wtgst = ser_amt + (ser_amt * (rec.service_gst/100))
            rec.service_amt = ser_wtgst             

    # field
    service_id = fields.Many2one(comodel_name='npa.expense_details_hdr',string='Service Name',ondelete='cascade',index=True)
    person_name = fields.Char(size=80,string='Person Name') 
    service_cost = fields.Float(string='Service Price',digits=(15,2),default=0)
    service_gst = fields.Float(string='GST %',digits=(5,2),default=0)
    service_qty = fields.Float(string='Service Quantity',digits=(5,2),default=0)    
    service_amt = fields.Float(string='Service Amount',digits=(15,2),compute='_compute_service_amt',store=True)
    unit_type_id = fields.Many2one(comodel_name='npa.common_code',string='Unit type',ondelete='restrict',domain="[('code_type','=','UnitId')]")
    active = fields.Boolean(string='Active',default=True)

class apty_request_order(models.Model):
    _name = 'npa.stock_request'
    _description = 'Apty Purchase Request'
    _rec_name = 'name'

    # Disable the DUPLICATE button    
    def copy(self):
        raise ValidationError("Sorry you are unable to duplicate records")

    # Perform a soft delete    
    def unlink(self):
        for rec in self:
            rec.active = False

    # Method to payment wizard
    def create_shop_payment(self):
        mod_obj = self.env['ir.model.data']
        form_res = mod_obj.get_object_reference('apty_acctmgmt', 'view_shop_payment_form')[1]
        return{
            'name': "Create Payment",
			   'view_type': 'form',
			   'view_mode':"[form]",
			   'view_id': form_res,
			   'res_model': 'npa.shop_payment_amt',
			   'type': 'ir.actions.act_window',
			   'views': [(form_res, 'form')],
			   'target': 'new',
			   'context':{'default_stock_reqst_id':self.id}
        }

    @api.model
    def create(self, vals):
        if not vals:
            vals = {}        
        vals['name'] = self.env['ir.sequence'].\
            next_by_code('npa.stock_request') or 'New'
        return super(apty_request_order, self).create(vals)

    # Calculate total transaction and total payment amount
    @api.depends('purchase_ids.stock_amt','payment_ids.payment_amt')
    def _compute_total_amt(self):
        total_amt = 0.0
        total_payment = 0.0
        for record in self:
            for line in record.purchase_ids:
                total_amt += line.stock_amt
            for line in record.payment_ids:
                total_payment += line.payment_amt
            print('****** payment total',total_payment)
            record.total_stock_amt = total_amt
            record.payment_amt = total_payment            
            record.total_gst = total_amt * record.stock_gst / 100
            record.gross_amt = (total_amt * record.stock_gst / 100) + total_amt
            record.amount_residual = (total_amt * record.stock_gst / 100) + total_amt - total_payment


    # Method to post purchase request
    def get_purchase_stock_post_wizard(self):
        try:
            form_id = self.env['ir.model.data'].get_object_reference('apty_acctmgmt', 'post_purchase_stock_req_wizard')[1]
        except ValueError:
            form_id = False
            raise Warning(_("Cannot locate required 'post_purchase_stock_req_wizard'. Please contact IT Support"))
        return{
                    'name': "Post stock Transaction",
                    'view_type': 'form',
                    'view_mode':"[form]",
                    'view_id': False,
                    'res_model': 'npa.common_wizard',
                    'type': 'ir.actions.act_window',
                    'target':'new',
                    'views': [(form_id, 'form')],
                    }

    name = fields.Char(size=80,string='Order Number',readonly=True, required=True, copy=False, default='New') 
    supplier_id = fields.Many2one(comodel_name='npa.supplier_details',string='Supplier Name',ondelete='cascade',index=True)
    Order_date = fields.Date(string='Order Date',default=lambda *a: datetime.now(pytz.timezone('Asia/Kolkata')).date().strftime('%Y-%m-%d'))
    received_date = fields.Date(string='Received Date',default=lambda *a: datetime.now(pytz.timezone('Asia/Kolkata')).date().strftime('%Y-%m-%d'))
    purchase_desc = fields.Text(string='Description')
    active = fields.Boolean(string='Active',default=True)
    purchase_ids=fields.One2many(comodel_name='npa.purchase_list', inverse_name='stock_reqst_id', string='Stock Transaction')
    payment_ids=fields.One2many(comodel_name='npa.shop_payment_amt', inverse_name='stock_reqst_id', string='Payment Amount')
    total_stock_amt = fields.Float(string='Total Amount',digits=(5,2),compute='_compute_total_amt',store=True)
    gross_amt = fields.Float(string='Total Amount Inclued GST',digits=(5,2))
    payment_amt = fields.Float(string='Amount Paid',digits=(5,2),compute='_compute_total_amt',store=True)
    amount_residual = fields.Float(string='Amount Due',digits=(5,2),compute='_compute_total_amt',store=True)
    stock_gst = fields.Float(string='GST %',digits=(5,2),default=0)
    total_gst = fields.Float(string='GST %',digits=(5,2),compute='_compute_total_amt',store=True)
    state = fields.Selection([
        ('New', 'New'),
        ('Posted', 'Posted'),
        ('Cancel', 'Cancel'),
        ], string='State', default='New')
    date_posted = fields.Date(string='Posted Date')
    posted_by = fields.Many2one(comodel_name='res.users',string='Posted by',ondelete='restrict')

class apty_purchase_item(models.Model):
    _name = 'npa.purchase_list'
    _description = 'Apty Purchase Items'    

    # Disable the DUPLICATE button    
    def copy(self):
        raise ValidationError("Sorry you are unable to duplicate records")

    # Perform a soft delete    
    def unlink(self):
        for rec in self:
            rec.active = False

    #Service Amount calculation
    @api.depends('stock_price','stock_qty','sgst','cgst')
    def _compute_stock_amt(self):
        for rec in self:                        
            ser_amt = rec.stock_price * rec.stock_qty            
            rec.stock_amt = (ser_amt * rec.sgst / 100) + (ser_amt * rec.cgst / 100) + ser_amt

    # get unit type
    @api.onchange('stock_id')
    def _onchange_unit_type(self): 
        if self.stock_id:                  
            unit_type = self.env['npa.stock_details'].search([('id','=',self.stock_id.id)],limit=1)                    
            if unit_type:
                self.unit_type_id=unit_type.unit_type_id.id           
            

    # field
    stock_reqst_id = fields.Many2one(comodel_name='npa.stock_request',string='Purchase Order',ondelete='cascade',index=True)    
    stock_id = fields.Many2one(comodel_name='npa.stock_details',string='Stock Name',ondelete='cascade',index=True)         
    stock_price = fields.Float(string='Price',digits=(15,2),default=0)    
    stock_qty = fields.Float(string='Quantity',digits=(5,2),default=0) 
    sgst = fields.Float(string='Price',digits=(15,2),default=0) 
    cgst = fields.Float(string='Price',digits=(15,2),default=0)    
    stock_amt = fields.Float(string='Amount',digits=(15,2),compute='_compute_stock_amt',store=True)
    unit_type_id = fields.Many2one(comodel_name='npa.common_code',string='Unit Type',ondelete='restrict')
    supplier_id = fields.Integer(string='Supplier ID', related='stock_reqst_id.supplier_id.id',store=True,readonly=True) 
    active = fields.Boolean(string='Active',default=True)

class shop_payment_amt(models.Model):
    _name = 'npa.shop_payment_amt'
    _description = 'Shop Payment Amount'

    # Perform a soft delete
    def unlink(self):
        for rec in self:
            rec.active = False

    # Disable the DUPLICATE button    
    def copy(self):
        raise ValidationError("Sorry you are unable to duplicate records")
               

    # fields
    stock_reqst_id = fields.Many2one(comodel_name='npa.stock_request',string='Purchase Order',ondelete='cascade',index=True)
    service_id = fields.Many2one(comodel_name='npa.expense_details_hdr',string='Service Name',ondelete='cascade',index=True)
    supplier_id = fields.Integer(string='Supplier ID', related='stock_reqst_id.supplier_id.id',store=True,readonly=True)
    payment_amt = fields.Float(string='Payment Amount',digits=(15,2),default=0)
    remarks = fields.Char(string='Remarks')    
    payment_date = fields.Date(string='Received Date',default=lambda *a: datetime.now(pytz.timezone('Asia/Kolkata')).date().strftime('%Y-%m-%d'))
    active = fields.Boolean(string='Active',default=True)
    payment_method = fields.Selection([
        ('Cash', 'Cash'),
        ('Cheque', 'Cheque'),
        ('Online', 'Online'),
        ('Offline', 'Offline'),
        ('Credit Card', 'Credit Card'),
        ('Debit Cart', 'Debit Card'),
        ], string='Payment Method', default='Cash')
    state = fields.Selection([
        ('New', 'New'),
        ('Confirm', 'Confirm'),
        ('Reject', 'Reject')
        ], string='State', default='New')
    bank_slipno = fields.Char(string='Bank Slip No.')
    bank_name = fields.Char(string='Bank Name')
    tran_refno = fields.Char(string='Refrence Number')
    tran_gst = fields.Float(string='ST',digits=(8,2),default=0.00)
    remarks = fields.Text(string='Description')
    
