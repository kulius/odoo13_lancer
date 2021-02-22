import urllib
import base64
import logging
from odoo.addons.amazon_connector.amazon_api import amazonerp_osv as amazon_api_obj
logger = logging.getLogger('sale')

from odoo import api, fields, models, _
from datetime import timedelta, datetime, time
from odoo import netsvc
from odoo.tools.translate import _

class AmazonOrderWorkflow(models.Model):
    _name = "amazon.order.workflow"
    
    def _get_marketplace(self):
        shop_obj = self.env['sale.shop']
        for rec in self:
            shop_ids = shop_obj.search([('amazon_workflow_id', '=', rec.id)])
            if shop_ids:
                rec.marketplace_count = len(shop_ids)
                
    def action_get_marketplace_workflow(self):
        market_p_ids = []
        market_p_ids = self.env['sale.shop'].search([('amazon_workflow_id', '=', self[0].id)])
        if market_p_ids:
            market_p_ids = list(market_p_ids._ids)
        imd = self.env['ir.model.data']
        list_view_id = imd.xmlid_to_res_id('amazon_connector.view_sale_shop_tree')
        form_view_id = imd.xmlid_to_res_id('amazon_connector.amazonerp_view_shop_form')
        result = {
                "type": "ir.actions.act_window",
                "res_model": "sale.shop",
                "views": [[list_view_id, "tree"], [form_view_id, "form"]],
                "domain": [["id", "in", market_p_ids]],
        }
        if len(market_p_ids) == 1:
            result['views'] = [(form_view_id, 'form')]
            result['res_id'] = market_p_ids[0]
        return result

    name = fields.Char(string="Name")
    validate_order = fields.Boolean(string="Validate Order")
    create_invoice = fields.Boolean(string="Create Invoice")
    validate_invoice = fields.Boolean(string="Validate Invoice")
    register_payment = fields.Boolean(string="Register Payment")
    complete_shipment = fields.Boolean(string="Complete Shipment")
    invoice_policy = fields.Selection(
        [('order', 'Ordered quantities'),
         ('delivery', 'Delivered quantities'),
         ('cost', 'Invoice based on time and material')],
        string='Invoicing Policy', default='order')
    picking_policy = fields.Selection([
        ('direct', 'Deliver each product when available'),
        ('one', 'Deliver all products at once')],
        string='Shipping Policy', required=True, readonly=True, default='direct')
    sale_journal = fields.Many2one('account.journal')
    marketplace_count = fields.Integer(string="Maketplaces", compute=_get_marketplace, default=0)
    amazon = fields.Boolean(string='Amazon')
    real_inventory_update = fields.Boolean(string='Real Inventory Update')
    
    
    
    
