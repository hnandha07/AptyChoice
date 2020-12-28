# MODEL DEFINITION FOR News Paper Ageency APPLICATION
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
 

# Model for COMMON CODE table
class common_code(models.Model):
    _name = 'npa.common_code'
    _description = 'Common code table'
    _order = 'code_type,code'   
        
    # fields
    name = fields.Char(size=100,string='Description',index=True)
    code = fields.Char(size=30,string='Code',index=True)
    code_type = fields.Char(string='Code type',index=True)    
    default_rec = fields.Boolean(string='Default code',default=False)   
    parm1 = fields.Char(string='Parameter 1')
    parm2 = fields.Char(string='Parameter 2')
    parm3 = fields.Char(string='Parameter 3')
    parm4 = fields.Char(string='Parameter 4') 
    active = fields.Boolean(string='Active',default=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id)
   
    # SQL constraint
    _sql_constraints = [('unique_lookup_code','UNIQUE(code_type,code,active,company_id)','Lookup code must be unique'),
                        ('unique_lookup_name','UNIQUE(code_type,name,active,company_id)','Lookup name must be unique')]

    # Perform a soft delete
    def unlink(self):
        for rec in self:
            rec.active = False

class config(models.Model):
    _name = 'npa.config'
    _description = 'config table'
    _order = 'name'

    # fields
    name = fields.Char(string='Description',required=True,index=True)
    code_type = fields.Char(string='Code type',required=True,index=True,default='Sys')
    # Possible values: 'Sys','App','WebSvc','LoginDomain'
    code = fields.Char(string='Code',required=True,index=True)    
    note = fields.Text(string='Notes')
    parm1 = fields.Char(string='Parameter 1')
    parm1_desc = fields.Char(string='Description for parameter 1')
    parm2 = fields.Char(string='Parameter 2')
    parm2_desc = fields.Char(string='Description for parameter 2')
    parm3 = fields.Char(string='Parameter 3')
    parm3_desc = fields.Date(string='Description for parameter 3')
    parm4 = fields.Char(string='Parameter 4')
    parm4_desc = fields.Date(string='Description for parameter 4')
    parm5 = fields.Char(string='Parameter 5')
    parm5_desc = fields.Date(string='Description for parameter 5')
    parm6 = fields.Char(string='Parameter 6')
    parm6_desc = fields.Date(string='Description for parameter 6')
    amt1 = fields.Float(string='Amount 1')
    amt2 = fields.Float(string='Amount 2')
    amt3 = fields.Float(string='Amount 3')
    amt4 = fields.Float(string='Amount 4')
    amt5 = fields.Float(string='Amount 5')
    amt1_desc = fields.Char(string='Description for amount 1')
    amt2_desc = fields.Char(string='Description for amount 2')
    amt3_desc = fields.Char(string='Description for amount 3')
    amt4_desc = fields.Char(string='Description for amount 4')
    amt5_desc = fields.Char(string='Description for amount 5')
    int1 = fields.Integer(string='Integer 1') 
    int1_desc = fields.Char(string='Description for integer 1')
    int2 = fields.Integer(string='Integer 2')
    int2_desc = fields.Char(string='Description for integer 2')
    int3 = fields.Integer(string='Integer 3')
    int3_desc = fields.Char(string='Description for integer 3')
    date1 = fields.Date(string='Date 1')
    date1_desc = fields.Char(string='Description for date 1')
    date2 = fields.Date(string='Date 2')
    date2_desc = fields.Char(string='Description for date 2')
    date3 = fields.Date(string='Date 3')
    date3_desc = fields.Char(string='Description for date 3')
    default_rec = fields.Boolean(string='Default code',default=False) 
    active = fields.Boolean(string='Active',default=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id)  

    #SQL constraint
    _sql_constraints = [('unique_lookup_code','UNIQUE(code,code_type,active,company_id)','Lookup code must be unique')]
    
    # Perform a soft delete
    def unlink(self):
        for rec in self:
            rec.active = False

class common_wizard(models.TransientModel):
    _name = 'npa.common_wizard'
    _description = 'Common Wizard'

    
    # fields for use on a range basis
    post_date = fields.Date(string="Post date",default=lambda *a: (datetime.today() + relativedelta(hours=8)).strftime('%Y-%m-%d'))    
    start_date1 = fields.Date(string="From date")
    end_date1 = fields.Date(string="To date")
    start_date2 = fields.Date(string="From date")
    end_date2 = fields.Date(string="To date")
    start_customer = fields.Char(string="From customer")
    end_customer = fields.Char(string="To customer")    
    start_code = fields.Char(string="From code")
    end_code = fields.Char(string="To code")
    start_refno = fields.Char(string="From reference")
    end_refno = fields.Char(string="To reference")
    start_appno = fields.Char(string="From applied-to reference")
    end_appno = fields.Char(string="To applied-to reference")
    start_datetime = fields.Datetime(string="From when",default=datetime.now())
    end_datetime = fields.Datetime(string="To when",default=datetime.now())
    # shop_id = fields.Many2one(comodel_name='npa.shop_details', string='Shops')
    # publication_id = fields.Many2one(comodel_name='npa.publication_details', string='Publication Group')
    int1 = fields.Integer(string="Int Value")
    state = fields.Char(string="Status")
    state1 = fields.Selection([
        ('New', 'New'),
        ('Posted', 'Posted'),
        ('Void', 'Void'),       
        ('Active', 'Active'),
        ('Rejected', 'Rejected'),        
        ('Suspended', 'Suspended'),
        ('Dormant', 'Dormant'),
        ('Closed', 'Closed'),
        ('Archived-Rejected', 'Archived-Rejected'),
        ], string='Status')
    state4 = fields.Selection([
        ('pdf', 'PDF'),
        ('xls', 'XLS'),
        ('csv', 'CSV'),        
        ], string='Report Type', default='pdf')
    file_name = fields.Char(string='File Name', size=64)
    file =  fields.Binary('File')
    reason_suspend=fields.Text(string="Suspended Reason")
    reason_closed = fields.Text(string="Closed Reason")
    reason_uplift = fields.Text(string="Uplift Reason")
    reason_reject = fields.Text(string="Rejected Reason")
    note = fields.Text(string='Note')
    user_ids = fields.Many2many('res.users', 'wizard_users_rel', 'wizard_id', 'resusers_id', string='User')
    no_of_days = fields.Integer(string='No Of Days')
    # customer_ids = fields.Many2many('res.partner', 'wizard_customer_rel', 'wizard_id', 'partner_id', string='Customers')
    cust_id = fields.Many2one('res.partner', 'Customer Name')
    route_id = fields.Many2one('npa.common_code', 'Route Name', domain="[('code_type','=','RouteDetails')]")
    # shop_ids = fields.Many2many('npa.shop_details', 'wizard_shop_rel', 'wizard_id', 'shop_id', string='Shop Name')
    message= fields.Char('message')
    start_dt = fields.Datetime(string="From date",default=(datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d 09:00:00'))
    end_dt = fields.Datetime(string="To date",default=datetime.now().strftime('%Y-%m-%d 09:00:00'))
    # month = fields.Selection([('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'),
    #                       ('5', 'May'), ('6', 'June'), ('7', 'July'), ('8', 'August'),
    #                       ('9', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December'), ],
    #                       string='Month',default=str((date.today().replace(day=1)).month))
    # year = fields.Selection([(num, str(num)) for num in range((datetime.now().year)-1, (datetime.now().year)+1 )], string='Year',
    #                         default=lambda self: datetime.now().year)

    # month2 = fields.Selection([('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'),
    #                       ('5', 'May'), ('6', 'June'), ('7', 'July'), ('8', 'August'),
    #                       ('9', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December'), ],
    #                       string='Month',default=str((date.today().replace(day=1) - timedelta(days=1)).month))
    # year2 = fields.Selection([(num, str(num)) for num in range((datetime.now().year)-1, (datetime.now().year)+1 )], string='Year',
    #                         default=lambda self: datetime.now().year)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id)


class branch(models.Model):
    _name = 'npa.branch'
    _description = 'Company branch'
    _order = 'name'
    
    # Returns the default calendar
    @api.model
    def _get_default_calendar(self):
        rec = self.env['npa.calendar'].search([('default_rec','=',True)],limit=1)
        if rec:
            return rec.id
        return
    
    # Returns the default country
    @api.model
    def _get_default_country(self):
        config_rec = self.env['npa.config'].search([('code_type','=','Sys'),('code','=','DftCountry')],limit=1)
        if config_rec:
            country_rec = self.env['res.country'].search([('code','=',config_rec.parm1)],limit=1)
            if country_rec:
                return country_rec.id
        return

    @api.constrains('branch_type')
    def check_main_branch(self):
        if self.branch_type == 'Main':
            recs = self.env['npa.branch'].search([('id','!=',self.id)])
            for rec in recs:
                if rec.branch_type == 'Main':
                    raise ValidationError('There is already a main branch')
    
    # Disable the DUPLICATE button    
    def copy(self):
        raise ValidationError("Sorry you are unable to duplicate records")
    
    # Perform a soft delete    
    def unlink(self):
        for rec in self:
            rec.active = False
        
    # This function will derive a address field suitable for showing on display or report
    @api.depends('address1','address2','address3','city','postcode','state_id','country_id')
    def _get_branch_address(self):
        for rec in self:
            if rec.address1:
                addr = rec.address1
                if rec.address2:
                    addr = addr+u',\n'+rec.address2
                if rec.address3:
                    addr = addr+u',\n'+rec.address3
                if rec.city:
                    addr = addr+u',\n'+rec.city
                if rec.postcode:
                    addr = addr+u',\nPostcode '+rec.postcode
                if rec.state_id:
                    addr = addr+u',\n'+rec.state_id.name
                if rec.country_id:
                    addr = addr+u',\n'+rec.country_id.name
            else:
                addr = u''
                                                    
            rec.display_address = addr
            
    # fields
    name = fields.Char(size=100,string='Branch name',index=True)
    code = fields.Char(size=20,string='Branch code',index=True)
    branch_type = fields.Selection([
        ('Kiosk', 'Kiosk'),
        ('Branch', 'Physical branch'),
        ('Main', 'Main'),
        ], string='Branch type', default='Branch',help='There should only be on main branch.  The company address is obtained from the main branch.')
    mgr_name = fields.Char(size=100,string='Name of manager')
    mgr_mobile = fields.Char(size=20,string='Mobile number of manager')
    mgr_email = fields.Char(size=40,string='Email of manager')
    address1 = fields.Char(size=100,string='Address 1',)
    address2 = fields.Char(size=100,string='Address 2')
    address3 = fields.Char(size=100,string='Address 3')
    city = fields.Char(size=100,string='City',)
    postcode = fields.Char(size=20,string='Postal code',)
    state_id = fields.Many2one(comodel_name='res.country.state', string='State',ondelete='restrict')
    country_id = fields.Many2one(comodel_name='res.country', string='Country',default=_get_default_country,ondelete='restrict')
    calendar_id = fields.Many2one(comodel_name='npa.calendar',string='Calendar',default=_get_default_calendar,ondelete='restrict')
    display_address = fields.Char(string='Display address',compute='_get_branch_address',store=True)
    phone1 = fields.Char(size=15,string='Primary phone')
    phone2 = fields.Char(size=15,string='Alternate phone')
    fax = fields.Char(size=15,string='Branch fax phone')
    active = fields.Boolean(string='Active',default=True)    
    geolocation = fields.Char(string='Geo location',help='This can be a GPS location or some map reference')
    geopicture = fields.Binary(string='Picture of geolocation',help='This is the picture of the location.  Can be screen capture of map.')
    state = fields.Selection([
        ('New', 'New'),
        ('Active', 'Activated'),
        ('Inactive', 'Inactive'),
        ('Closed', 'Closed'),
        ], string='Status', default='New')
    # 20-Jan-2017
    website = fields.Char(string='Web site address')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id) 

    # SQL constraint
    _sql_constraints = [('unique_branch_code','UNIQUE(code,active)','Another branch with the same code already exist'),
                        ('unique_branch_name','UNIQUE(name,active)','Another branch with the same name already exist')]

# Model for CALENDAR table
# This table store various calendars used by the system.  Each calendar will define the days of rest and will
# be associated to one for more holidays.  Also, each calendar is associated to a country and maybe even to a particular state.

class calendar(models.Model):
    _name = 'npa.calendar'
    _description = 'Calendar'
    _order = 'country_id,name'

    @api.constrains('default_rec')
    def check_default_rec(self):
        if self.default_rec ==True:
            obj = self.env['npa.calendar'].search([('id','!=',self.id)])
            for rec in obj:
                if rec.default_rec == True:
                    raise ValidationError("Sorry there is already existing default calendar")
                    break

    # Returns the default country
    @api.model
    def _get_default_country(self):
        config_rec = self.env['npa.config'].search([('code_type','=','Sys'),('code','=','DftCountry')],limit=1)
        if config_rec:
            country_rec = self.env['res.country'].search([('code','=',config_rec.parm1)],limit=1)
            if country_rec:
                return country_rec.id
        return    
    
    # Disable the DUPLICATE button    
    def copy(self):
        raise ValidationError("Sorry you are unable to duplicate records")
    
    # Perform a soft delete    
    def unlink(self):
        for rec in self:
            rec.active = False
    
    # fields
    name = fields.Char(size=100,string='Calendar name',index=True)
    country_id = fields.Many2one(comodel_name='res.country', string='Country',default=_get_default_country,ondelete='restrict',index=True)
    state_id = fields.Many2one(comodel_name='res.country.state', string='State',ondelete='restrict',
                               help='Leave blank if calendar applies to all states in country.')
    rest_on_mon = fields.Boolean(String='Rest on Monday',default=False)
    rest_on_tue = fields.Boolean(String='Rest on Tuesday',default=False)
    rest_on_wed = fields.Boolean(String='Rest on Wednesday',default=False)
    rest_on_thu = fields.Boolean(String='Rest on Thursday',default=False)
    rest_on_fri = fields.Boolean(String='Rest on Friday',default=False)
    rest_on_sat = fields.Boolean(String='Rest on Saturday',default=True)
    rest_on_sun = fields.Boolean(String='Rest on Sunday',default=True)
    holiday_ids = fields.One2many(comodel_name='npa.holiday', inverse_name='calendar_id', string="Holidays")
    default_rec = fields.Boolean(string='Default calendar',default=False)
    active = fields.Boolean(string='Active',default=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id)       

    # SQL constraint
    _sql_constraints = [('unique_calendar','UNIQUE(name,active,company_id)','Another calendar with same name already exist')]
    
# Model for HOLIDAY table
# This table store holidays for each calendar.  There are two types of holiday - 'Public holiday' which is a national gazetted holiday
# and 'non-work day' which is holiday declared by the company. 

class calendar_holiday(models.Model):
    _name = 'npa.holiday'
    _description = 'Holiday'
    _order = 'calendar_id,date_start'
    
    # fields
    calendar_id = fields.Many2one(comodel_name='npa.calendar',string='Calendar',index=True,ondelete='cascade')
    name = fields.Char(size=100,string='Date description',required=True)
    date_start = fields.Date(string='Date start',index=True)
    date_end = fields.Date(string='Until')
    holiday_type = fields.Selection([
        ('NoWork', 'Non-work day'),
        ('Holiday', 'Full-day holiday'),
        ('HalfDay', 'Half-day holiday'),
        ], string='Holiday type', default='Holiday')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id) 
    
    _sql_constraints = [('unique_holiday','UNIQUE(calendar_id,date_start,company_id)','Holiday for a date must be unique')]

    # If end date entered, ensure it is not earlier that start date
    @api.constrains('date_start', 'date_end')
    def _check_rate_range(self):
        for rec in self:
            if rec.date_end:
                date_start = datetime.strptime(rec.date_start,'%Y-%m-%d')
                date_end = datetime.strptime(rec.date_end,'%Y-%m-%d')
                if date_end < date_start:
                    raise models.ValidationError('Entered end date cannot be earlier than start date!')

class common_page(models.Model):
    _name = 'npa.common_page'
    _description = 'Common Page'
    _rec_name = 'name'

    name = fields.Char('Name')

