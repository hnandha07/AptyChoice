import re
import tempfile
import os
import base64
from shutil import copyfile,move
from odoo import models, fields, api, _
from datetime import datetime, time, date, timedelta
from odoo.exceptions import ValidationError
from json import dumps
import json
from odoo.http import request
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
import sys
# from werkzeug.routing import ValidationError

# This model will store any quick information (such as help info line, emergency contacts, etc)
# that the service desk person needs (besides assessing the Knowledge base)

# This model stores the activities that is associated with the case.  Activities can be Pending,

# This model stores the details of the cases in this helpdesk module.  This is the primary model for this module.

class helpdesk_case(models.Model):
    _name = 'npa.helpdesk_case'
    _description = 'Helpdesk case'
    _rec_name = 'name'

    def name_get(self):
        res = super(helpdesk_case, self).name_get()
        result=[]
        if self.env.context and self.env.context.get('name_get_case_ref'):
            for rec in self:
                result.append((rec.id,u"%s (%s)" % (rec.name,rec.case_ref))) 
        else:
            for rec in self:
                result.append((rec.id,u"%s"%(rec.name)))    
        return result

    # Compute age of the case
    @api.depends('case_date') 
    def _compute_day_diff(self):
        for rec in self:
            d1 = datetime.strptime(str(rec.case_date),'%Y-%m-%d')
            d2 = datetime.today()
            d3 = lambda d2: fields.datetime.now()
            rec.age=abs((d3(d2) - d1).days + 1)

    @api.onchange('partner_id')
    def get_customer_info(self):
        self.acct_id = ''
        if self.partner_id:
            rec = self.env['res.partner'].search([('id','=',self.partner_id.id)])
            if rec:
                self.contact_person = rec.name
                self.contact_email = rec.email
                self.contact_phone = rec.mobile_num1                
        else:
            self.contact_person =  self.contact_phone = self.contact_email = False or ''

    # fields
    name = fields.Char(size=100,string='Case title',index=True)
    case_ref = fields.Char(size=20,string='Case reference')
    case_date = fields.Date(string='Case date',default=lambda *a: (datetime.today() + relativedelta(hours=8)).strftime('%Y-%m-%d'))
    case_type_id = fields.Many2one(comodel_name='npa.common_code', string='Case type',ondelete='restrict',index=True, domain="[('code_type','=','CaseMgtType')]")
    category_id = fields.Many2one(comodel_name='npa.common_code', string='Case category',ondelete='restrict',index=True, domain="[('code_type','=','CaseCat')]")
    source_type_id = fields.Many2one(comodel_name='npa.common_code', string='Source of channel',ondelete='restrict',index=True, domain="[('code_type','=','SourceMgtType')]")
    state = fields.Selection([
        ('New', 'New'),
        ('Open', 'Open'),
        ('Closed', 'Closed'),
        ('Cancel', 'Cancelled'),
        ], string='Status', default='New')
    partner_id = fields.Many2one(comodel_name='res.partner', string='Customer',ondelete='cascade',index=True)
    general_desc = fields.Char(size=100,string='General description')
    detail_desc = fields.Text(string='Detail description')
    when_requested = fields.Datetime(string='Date/Time requested',default=lambda *a: (datetime.today() + relativedelta(hours=8)).strftime('%Y-%m-%d'))
    who_requested = fields.Char(string='Who Requested', related='requested_by_id.name', store=True, readonly=True)
    how_requested = fields.Selection([
        ('WebSite','Web site'),
        ('Email', 'Email'),
        ('Phone', 'Phone'),
        ('Message', 'Messaging'),
        ], string='How requested',default='Email')
    case_severity = fields.Selection([
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low'),
        ('None', 'None'),
        ], string='Severity',default='Medium')
    due_date = fields.Datetime(string='Date/Time to resolved')
    contact_person = fields.Char(size=100,string='Contact name', index=True)
    contact_email = fields.Char(size=100,string='Contact email')
    contact_phone = fields.Char(size=20,string='Contact phone')
    contact_title = fields.Char(size=20,string='Contact title')
    customer_ref = fields.Char(size=20,string='Customer reference')
    when_resolved = fields.Datetime(string='Date/Time resolved')
    resolve_note = fields.Text('Resolution notes')
    age = fields.Integer(string='Age', compute='_compute_day_diff', readonly=True, store=False)
    activity_ids = fields.One2many(comodel_name='npa.case_activity',inverse_name='case_id', string='Activities')
    escalation_ids = fields.One2many(comodel_name='npa.case_escalate',inverse_name='case_id', string='Escalations')
    document_ids = fields.One2many(comodel_name='npa.document',inverse_name='case_id', string='Related documents')
    active = fields.Boolean(string='Active record',default=True)
    assigned_to_id = fields.Many2one(comodel_name='res.users',string='User assigned to',index=True)    
    notified_on_new = fields.Boolean(string='Notified on new')
    notified_date = fields.Datetime(string='Date/Time notified')   
    escalated_to_id = fields.Many2one(comodel_name='res.users',string='Internal party')
    escalated_to = fields.Char(string='External party')
    escalated_email = fields.Char(string='Email of external party')
    when_escalated = fields.Datetime(string='Date/Time escalated')
    category_id_code = fields.Char(related='category_id.code')    
    report_tag_id = fields.Many2one(comodel_name='npa.common_code', string='Type of Report Tag',ondelete='restrict',index=True)
    requested_by_id = fields.Many2one(comodel_name='res.users', string='Requested by')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id)
    source_type = fields.Selection([
        ('Call', 'Call'),
        ('Email', 'Email'),
        ('Internal', 'Internal'),
        ], string='Source of channel',default='')

    
    def copy(self):
        raise ValidationError("Sorry you are unable to duplicate records")

class case_doc(models.Model):
    _name = 'npa.case_doc'
    _description = 'Case document store'
    
    # field
    case_id = fields.Many2one(comodel_name='npa.helpdesk_case',string='Helpdesk case',ondelete='cascade',index=True)
    name = fields.Char(size=100,string='Document title')
    doc_desc = fields.Text(string="General description")
    doc_ref = fields.Char(size=20,string='Document reference')
    doc_date = fields.Char(string='Document date')
    doc_author = fields.Text(string="Author")
    doc_version = fields.Text(string="Version")
    doc_content_bin = fields.Binary(string='File attachment',help='This is for document files such as PDF and DOC')
    file_name_bin = fields.Char(string='File name',help='This is the name of the file attachment')
    notes = fields.Text(string='Notes and comments')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id)

class case_cat(models.Model):
    _name = 'npa.case_category'
    _description = 'Case category'
    
    
    def copy(self):
        raise ValidationError("Sorry you are unable to duplicate records")
    
    # fields
    name = fields.Char(size=100,string="Category name")
    total_cases = fields.Integer(string="Total cases")
    open_cases = fields.Integer(string="Open cases")
    overdue_cases = fields.Integer(string="Overdue cases")
    mtd_new_cases = fields.Integer(string="MTD new cases")
    mtd_closed_cases = fields.Integer(string="MTD Closed cases")
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id)

class case_activity(models.Model):
    _name = 'npa.case_activity'
    _description = 'Case activity'
    
    
    def write(self,vals):
        for rec in self.create_uid:
            if self._uid != self.create_uid.id:
                raise ValidationError("You can't update Activity of other user.")
            else:
                super(case_activity,self).write(vals)

    @api.onchange('activity_date','activity_type_id','activity_note','activity_ref','ext_party','int_party_id','state')
    def checking_user(self):
        for rec in self.create_uid:
            if self._uid != self.create_uid.id:
                raise ValidationError("You can't update Activity of other user.")
    
    # fields
    case_id = fields.Many2one(comodel_name='npa.helpdesk_case',string='Helpdesk case', ondelete='cascade')
    activity_date = fields.Datetime(string='Activity date',default=lambda self: fields.datetime.now())
    activity_type_id = fields.Many2one(comodel_name='npa.common_code',string='Activity type',ondelete='restrict',index=True)
    name = fields.Char(string='Activity type',related="activity_type_id.name",readonly=True)
    activity_note = fields.Text(string='Note',help="Describe the activity and result")
    activity_ref = fields.Char(size=20,string='Reference',help='This may be document reference involved in this activity.')
    ext_party = fields.Char(size=100,string='External party',help='External party assigned to this activity.')
    int_party_id = fields.Many2one(comodel_name='res.users',string='Internal party',help='Internal user assigned to this activity.')
    when_assigned = fields.Datetime(string='Date/Time assigned',default=lambda self: fields.datetime.now())
    when_due = fields.Datetime(string='Date/Time due')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id)
    state = fields.Selection([
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Cancel', 'Cancelled'),
        ], string='Status', default='Pending')

class case_escalate(models.Model):
    _name = 'npa.case_escalate'
    _description = 'Case escalation'
    _rec_name = 'case_id'

    # fields
    case_id = fields.Many2one(comodel_name='npa.helpdesk_case',string='Helpdesk case', ondelete='cascade',index=True)
    escalated_to_id = fields.Many2one(comodel_name='res.users',string='Internal party')
    escalated_to = fields.Char(size=100,string='External party')
    escalated_email = fields.Char(size=40,string='Email of external party')
    when_escalated = fields.Datetime(string='Date/Time escalated',default=lambda self: fields.datetime.now())
    escalation_note = fields.Text('Escalation notes')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id) 


class document(models.Model):
    _name = 'npa.document'
    _description = 'Central document store'
    _order = 'name'

    # Disable the DUPLICATE button    
    def copy(self):
        raise ValidationError("Sorry you are unable to duplicate records")
    
    #this method to get the default value
    @api.model
    def _get_default_doc_class(self):
        document_class = self.env['npa.common_code'].search([('default_rec','=',True),('code_type','=','DocClass')],limit=1)
        if document_class:
            return document_class.id
        return

    #method to key in only future dates only 
    @api.constrains("date_valid")
    def doc_date_valid(self):
        if self.date_valid:
            d1=datetime.now()
            d2=datetime.strptime(str(self.date_valid), '%Y-%m-%d')
            if d1 > d2:
                raise ValidationError('Document valid until date must be future date.')
        return True

    @api.constrains('file_name')
    def get_type_immediately(self):
        #taking the document 
        ext= self.env['npa.common_code'].search([('code_type','=','DocType')])
        count = 0
        if self.file_name != False:
            for rec in ext:
                filename, file_extension = os.path.splitext(self.file_name)
                if file_extension[1:].lower() == rec.code.lower():
                    count += 1
                    break
            if count == 0:
                raise ValidationError('You have entered improper file')
            if len(self.file_name) > 50:
                #it is 50 but last 4-5 char are reserved by .docx etc
                raise ValidationError ('Please check your file name length it should be less than 45 letters')
        else:
            if self.document == False:
                self.file_name=u''

    #Method to get method allow edit document    
    def get_edit_doc(self):
        try:
            form_id = self.env['ir.model.data'].get_object_reference('npa_helpdesk', '')[1]
        except ValueError:
            form_id = False
        return{
                    'name': "Edit document",                    
                    'view_mode':"[form]",
                    'view_id': False,
                    'res_model': 'npa.common_wizard',
                    'type': 'ir.actions.act_window',
                    'target':'new',
                    'views': [(form_id, 'form')],
                    }
    
    def get_document_directory_path(self):
        '''This method returns you the document directory.'''
        document_directory = self.env['npa.config'].search([('code','=','DocDir'),('code_type','=','Sys')])[0].parm1
        if not os.path.exists(str(document_directory)):
            raise Warning('The Document Directory doesnt exist. Please set the Document Directory in System > System Parameters > document_directory')
        else:
            return document_directory

    def create_directory(self, file_directory):
        '''This method creates a directory if it does not exists.'''
        if not os.path.exists(file_directory):
            os.makedirs(file_directory)
            return True
        return False

    def write_file_to_directory(self, file_name, file_data, folder_name=False):
        '''This method is used to create a new File.
            filename: name of the file
            file_data: The data of the file.
            folder_name: The name of the folder where the document is created.'''
        #Getting the Document Diretory.
        doc_directory_path = self.get_document_directory_path()
        file_directory = os.path.join(doc_directory_path, folder_name or '')

        #Creating the folder if it doesnt exist.
        self.create_directory(file_directory)
        file_path = os.path.join(file_directory, str(file_name))

        #Writing a new file
        with open(file_path, 'wb') as new_file:
            decoded_data = base64.b64decode(file_data)
            new_file.write(decoded_data)
        return file_path
    
    def delete_file(self, file_path):
        '''This method deletes the file from the file_path provided.'''
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    
    def move_to_trash(self, file_path, file_name):
        '''This method moves the file to Trash DIrectory from the file_path provided.'''        
        doc_directory_path = self.get_document_directory_path()
        trash_path = os.path.join(doc_directory_path, 'Trash')
        trash_file_path = os.path.join(trash_path, file_name)
        self.create_directory(trash_path)
        self.delete_file(trash_file_path)
        move(file_path, trash_file_path)
        return True

    @api.model
    def create(self, vals):
        if os.path.isdir(tempfile.gettempdir()) == False:
            new_dir =  tempfile.mkdtemp()
        #for checking about the file size
        if vals.get('document'):
            encode_data = base64.b64decode(vals.get('document'))
            if sys.getsizeof(encode_data) >10000000:
                raise UserError(_('Your selected file more than 10 MB'))
            else:
                doc_directory_path = self.get_document_directory_path()
                folder_name = self.env['npa.common_code'].search([('id','=',vals.get('doc_class_id')),('code_type','=','DocClass')])[0].code
                new_file_path = self.write_file_to_directory(vals.get('file_name'), vals.get('document'), folder_name)
                vals.update({
                                'document':False,
                                'file_loc': new_file_path
                            })
            return super(document, self).create(vals)             
    
    def write(self, vals):        
        if vals.get('document'):
            file_path = tempfile.gettempdir()+'/'+vals.get('file_name')
            encode_data = base64.b64decode(vals.get('document'))
            data = encode_data
            f = open(file_path,'wb')
            f.write(encode_data)
            f.close()
            if os.stat(file_path).st_size >10000000:
                raise ValidationError('Your selected file more than 10 MB')
            else:
                os.remove(file_path)
                #Getting the document directory.
                doc_directory_path = self.get_document_directory_path()
        
                #Setting the folder name where the file will be created.
                if vals.get('doc_class_id'):
                    folder_name = self.env['npa.common_code'].search([('id','=',vals.get('doc_class_id')),('code_type','=','DocClass')])[0].code
                elif self.doc_class_id:
                    folder_name = self.doc_class_id.code
                else:
                    folder_name = False
        
                #This code block is executed when the class type is changed.
                if vals.get('doc_class_id') and not vals.get('document'):
                    if self.file_name:
                        new_folder_path = os.path.join(doc_directory_path, folder_name)
                        self.create_directory(new_folder_path)
                        #Copying the file from old directory to new directory.
                        copyfile(self.file_loc, os.path.join(new_folder_path, self.file_name))
                        #Deleting the old file.
                        self.delete_file(self.file_loc)
                        vals.update({
                                    'file_loc': os.path.join(new_folder_path, self.file_name)
                                    })

        #This code block is executed when the document is uploaded.
        if vals.get('file_name') or vals.get('document'):
            #Creating the document
            new_file_path = self.write_file_to_directory(vals.get('file_name'), vals.get('document'), folder_name or '')
            #Deleting the old file.
            if self.file_loc != new_file_path:
                self.delete_file(self.file_loc)
            vals.update({
                            'document':False,
                            'file_loc': new_file_path
                        })
        return super(document, self).write(vals)
    
    def unlink(self):
        for document_rec in self:
            file_path = document_rec.file_loc
            file_name = document_rec.file_name
            #Calling the move_to_trash method 
            #to move the file to Trash from the path provided.
            if os.path.exists(file_path):
                self.move_to_trash(file_path,file_name)
            document_rec.active = False

    @api.constrains('doc_version')
    def get_version(self):
        if self.doc_version == False:
            self.doc_version = ''
        else:
            check_string = bool(re.search('[a-zA-Z]+',self.doc_version))
            if check_string == True :
                raise ValidationError('Document version value is invalid:\nNumeric values only provided ')
            else:
                #making sure last digit is not a point
                if str(self.doc_version)[-1:] == '.':
                    raise ValidationError('Document version value is invalid:\nYou can not put last digit as point "." ')
                if str(self.doc_version).count('.') > 2 :
                    raise ValidationError('Document version value is invalid:\n2 is the max number of "." ')
                else:
                    if str(self.doc_version).count('.') == 2:
                        if str((self.doc_version)[-4:]).count('.') <2 :
                            raise ValidationError('You can not enter more than one digit after the point')
                    if str(self.doc_version).count('.') == 1 :
                        if str((self.doc_version)[-2:]).count('.') <1 :
                            raise ValidationError('You can not enter more than one digit after the point')
                    else:
                        self.update({'doc_version': str(self.doc_version)+'.0'})

    # fields
    name = fields.Char(size=80,string='Document name',index=True)    
    doc_class_id = fields.Many2one(comodel_name='npa.common_code',string='Document class',ondelete='restrict',domain="[('code_type','=','DocClass')]",default=_get_default_doc_class)
    doc_class_id_code = fields.Char(related='doc_class_id.code')
    doc_code = fields.Char(string='Document code',related='doc_class_id.code',readonly=True)
    doc_type_id = fields.Many2one(comodel_name='npa.common_code',string='Document type',ondelete='restrict',domain="[('code_type','=','DocType')]")
    doc_version = fields.Char(size=20,string='Doc version')
    file_loc = fields.Char(string='File location',help='This is the name of the file attachment')
    file_name = fields.Char(string='File name attachment',help='This is the name of the file attachment')
    file_name_related = fields.Char(related='file_name', string='File name',help='This is a related field only to show data. The data of FileName is in file_name field.')
    notes = fields.Text(string='Notes and comments')
    date_valid = fields.Date(string='Valid until',help='This indicate until when the document content is valid.') 
    partner_id = fields.Many2one(comodel_name='res.partner', string='Customer',ondelete='cascade',index=True)
    staff_id = fields.Many2one(comodel_name='npa.staff_details', string='Staff',ondelete='cascade',index=True)
    submit_date = fields.Datetime(string='Date/time submitted')
    submit_by = fields.Many2one(comodel_name='res.users',string='Submitted by',ondelete='restrict')
    approve_date = fields.Datetime(string='Date/time approved/rejected')
    approve_by = fields.Many2one(comodel_name='res.users',string='Approved/rejected by',ondelete='restrict')
    archived_date = fields.Datetime(string='Date/time archived')
    archived_by = fields.Many2one(comodel_name='res.users',string='Archived by',ondelete='restrict')
    document_sub_type = fields.Selection(string="Document Sub type", selection=[('panel', 'Panel'), ('slide', 'Slide')])
    doc_image = fields.Binary(string="Document Image",  )
    document = fields.Binary('Document', attachment=True)
    permission = fields.Selection([
        ('Public', 'Public'),
        ('MemberAll', 'All members'),
        ('MemberInd', 'Individual member'),
        ('Internal', 'Internal user only'),
        ], string='Permission', default='Internal')
    active = fields.Boolean(string='Active',default=True)
    state = fields.Selection([
        ('New', 'New'),
        ('Approved', 'Checked'),
        ('Rejected', 'Rejected'),
        ('Archived', 'Archived'),
        ], string='Status', default='New')
    doc_date = fields.Date(string='Document date',help='For use with statements')   
    # report_by = fields.Char(string='Report by')
    # report_type_id = fields.Many2one(comodel_name='npa.common_code',string='Publication report type',ondelete='restrict',domain="[('code_type','=','DocRptType')]")
    # report_type = fields.Char(string='Report type',related='report_type_id.name',store=True,readonly=True)  
    download_count = fields.Integer(string='Download/read count')    
    doc_desc = fields.Char(string='Document description')    
    list_code = fields.Char(string="List code", index=True)
    list_seq = fields.Integer(string='List sequence')
    slide1 = fields.Binary('Slide 1', attachment=True)
    slide2 = fields.Binary('Slide 2', attachment=True)
    slide3 = fields.Binary('Slide 3', attachment=True)
    header1 = fields.Char(string="Header")
    header2 = fields.Char(string="Header 2")
    header3 = fields.Char(string="Header 3")
    desc1 = fields.Char(string="Description 1")
    desc2 = fields.Char(string="Description 2")
    desc3 = fields.Char(string="Description 3")
    header1_html = fields.Html(string="Header HTML 1")
    header2_html = fields.Html(string="Header HTML 2")
    desc1_html = fields.Html(string="Description HTML 1")
    desc2_html = fields.Html(string="Description HTML 2")
    main_content_html = fields.Html(string='Main HTML content')
    publish_period = fields.Char(string='Publication period')
    publish_year = fields.Char(string='Publication year')
    case_id = fields.Many2one(comodel_name='npa.helpdesk_case', string='Helpdesk case',ondelete='cascade',index=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id)

    _sql_constraints = [
        ('doc_version_name_uniq', 'unique(name,doc_version,partner_id,file_name,active)', 'Another document with the same name and version and file name already exist !'),
    ]   


class customer_details(models.Model):
    _inherit = 'res.partner'

    doc_ids= fields.One2many(comodel_name='npa.document',inverse_name='partner_id',string='Document Details')

class staff_details(models.Model):
    _inherit = 'npa.staff_details'

    doc_ids= fields.One2many(comodel_name='npa.document',inverse_name='staff_id',string='Document Details')

 

