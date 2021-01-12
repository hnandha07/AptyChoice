# -*- coding: utf-8 -*-
from odoo import http


class AptyKitchenScreenController(http.Controller):
    @http.route('/kitchen_screen', type='http', auth='user', methods=['POST'], csrf=False)
    def get_kitchen_screen(self, **kw):
        return "Hello, world"
