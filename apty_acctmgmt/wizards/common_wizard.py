import sys
import os
import base64
import odoo
from odoo import models, api, fields,_
from datetime import datetime
from odoo.exceptions import Warning
import tempfile
import random
import string
from time import strftime

class common_wizard(models.TransientModel):
    _inherit = 'npa.common_wizard'
    
    def post_stock_transfer_req(self):
        tran_recs = self.env['npa.stock_request'].search([('id','=',self._context.get('active_id'))])
        tran_recs.write({'state':'Posted','posted_by':self._uid, 'date_posted':datetime.now()})

    def post_service_req(self):
        tran_recs = self.env['npa.expense_details_hdr'].search([('id','=',self._context.get('active_id'))])
        tran_recs.write({'state':'Posted','posted_by':self._uid, 'date_posted':datetime.now()})