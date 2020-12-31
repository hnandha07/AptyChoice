import os.path
from odoo import http
from odoo.addons.web.controllers.main import Binary
from odoo.http import request
from odoo.addons.web.controllers.main import content_disposition
import tempfile
import base64
from os import chdir


class Binary(Binary):


    @http.route(['/web/binary/download_document',
        '/web/binary/download_document/<int:doc_id>',], type='http', auth="public")
    def download_document(self, doc_id=None, **kw):
        """ Download link for files stored as binary fields.
        :param str id: field holding the ID of vb_document table
        :returns: :class:`werkzeug.wrappers.Response`
        """
        #Getting the document directory path
        document_directory_path = request.env['npa.document'].get_document_directory_path()
        if doc_id:
            #Getting Document Record
            document_rec = request.env['npa.document'].search([('id','=',int(doc_id))])
            #Checking if the file exists, and then fetching the document.
            if os.path.exists(document_rec.file_loc):
                with open(document_rec.file_loc, 'rb') as doc_file:
                    filecontent = doc_file.read()
                if not filecontent:
                    return request.not_found()
                else:
                    if document_rec.file_name[-3:] == 'pdf':
                    #Return the file and filename to the browser.
                        return request.make_response(filecontent,
                                       [('Content-Type', 'application/pdf'),
                                        ('Content-Disposition', content_disposition(document_rec.file_name))])
                    else:
                        return request.make_response(filecontent,
                                       [('Content-Type', 'attachment'),
                                        ('Content-Disposition', content_disposition(document_rec.file_name))])
            else:
                msg = 'File document {0} not found in NFS server. Please check the file or upload again.'.format(document_rec.file_loc)
                return request.not_found(msg)

    @http.route('/web/binary/open_document/', type='http', auth="public")
    def open_document(self, id, **kw):
        """ Download link for files stored as binary fields.
        :param str id: field holding the ID of vb_document table
        :returns: :class:`werkzeug.wrappers.Response`
        """

        #Getting the document directory path
        document_directory_path = request.env['npa.document'].get_document_directory_path()

        #Getting Document Record
        document_rec = request.env['npa.document'].search([('id','=',int(id))])
        #Checking if the file exists, and then fetching the document.
        if os.path.exists(document_rec.file_loc):
            with open(document_rec.file_loc, 'rb') as doc_file:
                filecontent = doc_file.read()
            if not filecontent:
                return request.not_found()
            else:
                if document_rec.file_name[-3:] == 'pdf':
                #Return the file and filename to the browser.
                    return request.make_response(filecontent,
                                   [('Content-Type', 'application/pdf'),
                                    ('Content-Disposition', 'inline')])
                else:
                    return request.make_response(filecontent,
                                   [('Content-Type', 'attachment'),
                                    ('Content-Disposition', 'inline')])
        else:
            msg = 'File document {0} not found in NFS server. Please check the file or upload again.'.format(document_rec.file_loc)
            return request.not_found(msg)

    @http.route('/web/binary/document_location',type="http",auth="public")
    def location_url(self, file_loc, **kw):
        if file_loc and os.path.exists(file_loc):
            with open(file_loc, 'rb') as doc_file:
                filecontent = doc_file.read()
            if not filecontent:
                return request.not_found()
            else:
                file_name = file_loc.split('/')[-1]
                if file_name[-3:] == 'pdf':
                #Return the file and filename to the browser.
                    return request.make_response(filecontent,
                                   [('Content-Type', 'application/pdf'),
                                    ('Content-Disposition', 'inline')])
                else:
                    return request.make_response(filecontent,
                                   [('Content-Type', 'application/octet-stream'),
                                    ('Content-Disposition', content_disposition(file_loc.split('/')[-1]))])
        else:
            msg = 'File document {0} not found in NFS server. Please check the file or upload again.'.format(file_loc)
            return request.not_found(msg)
