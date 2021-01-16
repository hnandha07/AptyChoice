# -*- coding: utf-8 -*-
from datetime import date
from pprint import pformat
from odoo import models, fields, api
from odoo.exceptions import _logger
from itertools import groupby as py_groupby

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    apty_order_state = fields.Selection(string="Apty Order State",
                                        selection=[('draft', 'Draft'), ('order', 'Order'), ('preparing', 'Preparing'), (
                                            'ready', 'Ready'), ('picked', 'Picked'), ('delivered', 'Delivered'),
                                                   ('cancel', 'Cancel')])


class apty_kitchen_screen(models.AbstractModel):
    _name = 'apty.kitchen.screen'
    _description = 'Apty Kitchen Screen'

    def prepare_kitchen_screen(self):
        render_view_data, data = {}, {}
        try:
            data = self.get_sale_orders_data()
            render_view_data = {'status':True,'data': data}
        except Exception as e:
            render_view_data = {'status':False}
            _logger.info("Exception occurred while preparing kitchen date: {}".format(pformat(e)))
        return self.env['ir.ui.view'].render_template("apty_kitchen_screen.kitchen_screen_template", render_view_data)

    def get_sale_orders_data(self):
        match_date = date.today()
        # match_date = '2021-01-21'
        query = """
        select order_id, sale_order.name as so_name, product.name as pname, product_uom_qty
        from sale_order_line as sol
        JOIN product_template as product on product.id = sol.product_id
        JOIN sale_order as sale_order on sale_order.id = sol.order_id
        where order_id in (
            select id from sale_order as so where so.commitment_date::TIMESTAMP::DATE = %s 
            and so.apty_order_state = 'order'
        )
        group by order_id, pname, so_name, product_uom_qty order by order_id"""
        self._cr.execute(query, [match_date])
        result = self._cr.dictfetchall()
        result = [{key:list(value)} for key,value in py_groupby(result,lambda x:x['order_id'])]
        return result
