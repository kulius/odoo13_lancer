# -*- coding: utf-8 -*-
from odoo import api, fields, models,_
from odoo.tools.translate import _

class CreateAmazonShop(models.TransientModel):
    _name = "create.amazon.shop"
    _description = "Create Amazon Shop"

#    @api.multi
    def create_amazon_shop_action(self):
        shop_obj = self.env['sale.shop']
        
        for rec in self:
            shop_vals = {
                'name' : rec.name,
                'payment_default_id': rec.payment_default_id.id,
                'code': rec.name,
                'warehouse_id' : rec.warehouse_id.id,
                'cust_address' : rec.cust_address.id,
                'company_id' : rec.company_id.id,
                'amazon_picking_policy' : rec.picking_policy,
                'amazon_order_policy' : rec.order_policy,
                'amazon_invoice_quantity' : rec.invoice_quantity,
                'amazon_instance_id' : self._context.get('active_id') and self._context['active_id'] or False,
                'amazon_shop' : True,
            }
            amazon_shop_id = shop_obj.create(shop_vals)
            if amazon_shop_id:
                message = _('%s Shop Successfully Created!')% (rec.name)
                return {'type': 'ir.actions.act_window_close'}
            else:
                message = _('Error creating amazon shop')
                return False
            
    name = fields.Char('Shop Name', size=64, required=True)
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse',required=True)
    cust_address = fields.Many2one('res.partner', 'Address', required=True)
    company_id = fields.Many2one('res.company', 'Company', required=False, default=lambda s: s.env('res.company')._company_default_get('stock.warehouse'))
    payment_default_id = fields.Many2one('account.payment.term', 'Default Payment Term', required=True)
    picking_policy = fields.Selection([('direct', 'Deliver each product when available'), ('one', 'Deliver all products at once')], 'Shipping Policy', required=True,
                                        help="""Pick 'Deliver each product when available' if you allow partial delivery.""")
    order_policy = fields.Selection([
            ('manual', 'On Demand'),
            ('picking', 'On Delivery Order'),
            ('prepaid', 'Before Delivery'),
        ], 'Create Invoice',
        help="""On demand: A draft invoice can be created from the sales order when needed. \nOn delivery order: A draft invoice can be created from the delivery order when the products have been delivered. \nBefore delivery: A draft invoice is created from the sales order and must be paid before the products can be delivered.""")
    invoice_quantity = fields.Selection([('order', 'Ordered Quantities'), ('procurement', 'Shipped Quantities')], 'Invoice on', help="The sale order will automatically create the invoice proposition (draft invoice). Ordered and delivered quantities may not be the same. You have to choose if you invoice based on ordered or shipped quantities. If the product is a service, shipped quantities means hours spent on the associated tasks.",required=True)
    
