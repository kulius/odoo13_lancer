# -*- coding: utf-8 -*-
from odoo.exceptions import UserError
from odoo import api, fields, models, _

class  updateOrderStatusOnAmazon(models.TransientModel):
    _name = "update.order.status.on.amazon"

#    @api.multi
    def update_order_status(self):
        for order in self.env['sale.order'].browse(self._context.get('active_ids')):
            order.shop_id.with_context({'order_ids': [order.id]}).update_amazon_orders()
        return True
      

