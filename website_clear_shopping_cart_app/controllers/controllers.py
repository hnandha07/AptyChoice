# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json

class websitecartempty(http.Controller):
	@http.route('/shop/cartempty',type='http', auth='public', website=True)
	def new_web(self, **kw):
		sale_order= request.website.sale_get_order(force_create=True)
		if sale_order:
			for line in sale_order.website_order_line:
				line.unlink()
		return[]