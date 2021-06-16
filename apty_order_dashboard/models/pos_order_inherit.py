from odoo import api, fields, models, _


class PoSOrderInherit(models.Model):
    """ Inherited to add new states to the PoS Order """
    _inherit = 'pos.order'

    apty_order_state = fields.Selection(selection=[('draft', 'Draft'), ('order', 'Order'), ('preparing', 'Preparing'), ('ready', 'Ready'), ('picked', 'Picked'), ('delivered', 'Delivered'), ('cancel', 'Cancel')], 
                                        string="Apty Order State", default='order')

    order_date = fields.Datetime(string='Order Date', related='create_date')
    order_by = fields.Many2one('res.users', string='Order By')
    preparing_date = fields.Datetime(string='Preparing Date')
    preparing_by = fields.Many2one('res.users', string='Preparing By')
    ready_date = fields.Datetime(string='Ready Date')
    ready_by = fields.Many2one('res.users', string='Ready By')
    picked_date = fields.Datetime(string='Picked Date')
    picked_by = fields.Many2one('res.users', string='Picked By')
    delivered_date = fields.Datetime(string='Delivered Date')
    delivered_by = fields.Many2one('res.users', string='Delivered By')
    cancelled_date = fields.Datetime(string='Cancelled Date')
    cancelled_by = fields.Many2one('res.users', string='Cancelled By')

    def get_order_details(self):
        order = self.search_read([('id', 'in', self.id)], [])
        order_lines = self.env['pos.order.line'].search_read([('order_id', 'in', self.id)], [])
        if order[0]['company_id']:
            company_details = self.env['res.company'].sudo().search([('id', '=', order[0]['company_id'][0])])
            order[0]['company_id'] = (company_details.name, company_details.phone, company_details.vat, company_details.email, company_details.website)
        if order and order[0].get('partner_id'):
            partner_id = self.env['res.partner'].search_read([('id', '=', order[0].get('partner_id')[0])], [])
        else:
            partner_id = ('', '')
        for line in order_lines:
            taxes = ''
            if line.get('tax_id'):
                for tax in line.get('tax_id'):
                    tax = self.env['account.tax'].search([('id', '=', tax)])
                    taxes += tax.name + ', '
            line['tax_id'] = taxes
            if line.get('product_id'):
                product_id = self.env['product.product'].search([('id', '=', line.get('product_id')[0])])
                line['product_description'] = product_id.description_sale or ''
        order[0]['order_line'] = order_lines
        order[0]['partner_id'] = partner_id
        order[0]['model'] = 'pos.order'

        return order