from odoo import api, fields, models, _


class SaleOrderDashboardInherit(models.Model):
    """ Inherited to add new functionalities related to the dashboard. """
    _inherit = 'sale.order'

    reason = fields.Char('Reason')

    sale_order_date = fields.Datetime(string='Sale Order Date', related='create_date')
    sale_preparing_date = fields.Datetime(string='Sale Order Preparing Date')
    sale_ready_date = fields.Datetime(string='Sale Order Ready Date')
    sale_picked_date = fields.Datetime(string='Sale Order Picked Date')
    sale_delivered_date = fields.Datetime(string='Sale Order Delivered Date')
    sale_cancelled_date = fields.Datetime(string='Sale Order Cancelled Date')

    # def write(self, vals):
    #     res = super(SaleOrderDashboardInherit, self).write(vals)
    #     if vals and vals.get('state') and vals.get('state') == 'sale':
    #         print("\n\n\n vals : ", vals)
    #         users = self.env['res.users'].search([])
    #         for user in users:
    #             notifications = []
    #             if user.partner_id.im_status == 'online':
    #                 message_string = """New order has been received. Kindly go to Dashboard and check it."""
    #                 notif = {
    #                     'user_id': user.id,
    #                     'message': message_string,
    #                     'title': "New Order Received",
    #                     'sticky': True,
    #                     'type': 'info',
    #                     }

    #     return res

    def get_order_details(self):
        print('---sale order-')
        order = self.search_read([('id', 'in', self.id)], [])
        order_lines = self.env['sale.order.line'].search_read([('order_id', 'in', self.id)], [])
        partner_id = self.env['res.partner'].search_read([('id', '=', order[0].get('partner_id')[0])], [])
        for line in order_lines:
            taxes = ''
            if line.get('tax_id'):
                for tax in line.get('tax_id'):
                    tax = self.env['account.tax'].search([('id', '=', tax)])
                    taxes += tax.name + ', '
            line['tax_id'] = taxes
        transaction_id = self.env['payment.transaction'].search([('sale_order_ids', 'in', order[0].get('id'))], limit=1, order="id DESC")
        print(">>>>>>>>>>. transaction ", transaction_id, transaction_id.acquirer_id)
        order[0]['order_line'] = order_lines
        order[0]['partner_id'] = partner_id
        order[0]['model'] = 'sale.order'
        order[0]['payment_mode'] = transaction_id.acquirer_id.provider
        return order