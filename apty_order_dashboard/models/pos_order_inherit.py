from odoo import api, fields, models, _


class PoSOrderInherit(models.Model):
    """ Inherited to add new states to the PoS Order """
    _inherit = 'pos.order'

    apty_order_state = fields.Selection(selection=[('draft', 'Draft'), ('order', 'Order'), ('preparing', 'Preparing'), ('ready', 'Ready'), ('picked', 'Picked'), ('delivered', 'Delivered'), ('cancel', 'Cancel')], 
                                        string="Apty Order State",)