# -*- coding: utf-8 -*-
import urllib
import base64
import logging
logger = logging.getLogger('sale')

from odoo import api, fields, models, _
from datetime import timedelta, datetime, time
from odoo import netsvc
from odoo.tools.translate import _
from odoo.addons.amazon_connector.amazon_api import amazonerp_osv as amazon_api_obj

# class PosSaleReport(models.Model):
#     _inherit = 'report.all.channels.sales'
#
#     state_id= fields.Many2one('res.country.state', string='Parnter State', readonly=True)
#     amount_tax= fields.Float(string='Taxes', readonly=True)
#
#     def _so(self):
#         so_str = """
#             WITH currency_rate as (%s)
#                 SELECT sol.id AS id,
#                     so.name AS name,
#                     so.partner_id AS partner_id,
#                     sol.product_id AS product_id,
#                     pro.product_tmpl_id AS product_tmpl_id,
#                     so.date_order AS date_order,
#                     so.user_id AS user_id,
#                     pt.categ_id AS categ_id,
#                     so.company_id AS company_id,
#                     sol.price_total / COALESCE(cr.rate, 1.0) AS price_total,
#                     so.amount_tax / COALESCE (cr.rate, 1.0) AS amount_tax,
#                     so.pricelist_id AS pricelist_id,
#                     rp.country_id AS country_id,
#                     rp.state_id AS state_id,
#                     sol.price_subtotal / COALESCE (cr.rate, 1.0) AS price_subtotal,
#                     (sol.product_uom_qty / u.factor * u2.factor) as product_qty,
#                     so.analytic_account_id AS analytic_account_id,
#                     so.team_id AS team_id
#
#             FROM sale_order_line sol
#                     JOIN sale_order so ON (sol.order_id = so.id)
#                     LEFT JOIN product_product pro ON (sol.product_id = pro.id)
#                     JOIN res_partner rp ON (so.partner_id = rp.id)
#                     LEFT JOIN product_template pt ON (pro.product_tmpl_id = pt.id)
#                     LEFT JOIN product_pricelist pp ON (so.pricelist_id = pp.id)
#                     LEFT JOIN currency_rate cr ON (cr.currency_id = pp.currency_id AND
#                         cr.company_id = so.company_id AND
#                         cr.date_start <= COALESCE(so.date_order, now()) AND
#                         (cr.date_end IS NULL OR cr.date_end > COALESCE(so.date_order, now())))
#                     LEFT JOIN product_uom u on (u.id=sol.product_uom)
#                     LEFT JOIN product_uom u2 on (u2.id=pt.uom_id)
#         """ % self.env['res.currency']._select_companies_rates()
#         return so_str
#
#     def get_main_request(self):
#         request = """
#             CREATE or REPLACE VIEW %s AS
#                 SELECT id AS id,
#                     name,
#                     partner_id,
#                     product_id,
#                     product_tmpl_id,
#                     date_order,
#                     user_id,
#                     categ_id,
#                     company_id,
#                     price_total,
#                     amount_tax,
#                     pricelist_id,
#                     analytic_account_id,
#                     country_id,
#                     state_id,
#                     team_id,
#                     price_subtotal,
#                     product_qty
#                 FROM %s
#                 AS foo""" % (self._table, self._from())
#         return request
    
class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    def _default_journal(self):
        accountjournal_obj = self.env['account.journal']
        accountjournal_ids = accountjournal_obj.search([('name','=','Sales Journal')])
        if accountjournal_ids:
            return accountjournal_ids[0]
        return False
        
#     @api.depends('order_line.price_total')
#     def _amount_all(self):
#         """
#         Compute the total amounts of the SO.
#         """
#         for order in self:
#             amount_untaxed = amount_tax = 0.0
#             amazon_tax = 0.0
#             for line in order.order_line:
#                 print("amazon_taxamazon_tax",line.new_tax_amount)
#                 amount_untaxed += line.price_subtotal
#                 amount_tax += line.price_tax
#                 amazon_tax += line.new_tax_amount
#             if order.amazon_order or order.magento_order:
#                 amount_tax = amazon_tax
#             else:
#                 amount_tax = amount_tax
#             order.update({
#                 'amount_untaxed': order.pricelist_id.currency_id.round(amount_untaxed),
#                 'amount_tax': order.pricelist_id.currency_id.round(amount_tax),
#                 'amount_total': amount_untaxed + amount_tax,
#             })    

    def _get_amazon_staus(self):
        for order in self:
            if order.picking_ids:
                order.updated_in_amazon=True
            else:
                order.updated_in_amazon=False
            for picking in order.picking_ids:
                if picking.state =='cancel':
                    continue
                if picking.picking_type_id.code!='outgoing':
                    continue
                if not picking.updated_in_amazon:
                    order.updated_in_amazon=False
                    break

    def _search_order_ids(self,operator,value):
        #                inner join amazon_sale_order_ept on sale_order_id=sale_order.id

        query="""
                select sale_order.id from stock_picking               
                inner join sale_order on sale_order.procurement_group_id=stock_picking.group_id
                inner join stock_location on stock_location.id=stock_picking.location_dest_id and stock_location.usage='customer'                
                where stock_picking.updated_in_amazon=False and stock_picking.state='done'    
              """
        self._cr.execute(query)
        results = self._cr.fetchall()
        order_ids=[]
        for result_tuple in results:
            order_ids.append(result_tuple[0])
        return [('id','in',order_ids)]

#         Settlement report 

    amazon_reference = fields.Char(size=350, string='Amazon Order Ref')    
    amz_send_order_acknowledgment=fields.Boolean("Acknowledgment required ?")
    amz_allow_adjustment=fields.Boolean("Allow Adjustment ?")
    amz_instance_id = fields.Many2one("amazon.instance.ept","Instance")
    updated_in_amazon = fields.Boolean("Updated In Amazon",compute=_get_amazon_staus,search='_search_order_ids')
    amz_shipment_service_level_category=fields.Selection([('Expedited','Expedited'),('NextDay','NextDay'),('SecondDay','SecondDay'),('Standard','Standard'),('FreeEconomy','FreeEconomy')],"Shipment Service Level Category",default='Standard')
    amz_fulfillment_by = fields.Selection([('MFN','Manufacturer Fulfillment Network')],string="Fulfillment By",default='MFN')
    is_amazon_canceled=fields.Boolean("Canceled In amazon ?",default=False)
    amz_fulfillment_instance_id=fields.Many2one('amazon.instance.ept' ,string="Fulfillment Instance")
    sale_order_report_id=fields.Many2one("amazon.sale.order.report.ept",string="Sale Order Report")
    
    amazon_order_id = fields.Char(string='Order ID', size=256)
    shipping_submission_feedid = fields.Char(string='Submission Feed ID',size=15)
    journal_id = fields.Many2one('account.journal', string='Journal',readonly=True)
    faulty_order = fields.Boolean(string='Faulty')
    confirmed = fields.Boolean(string='Confirmed')
    fullfillment_method = fields.Selection([('MFN','MFN'),('AFN','AFN')], string='Fullfillment Shop', track_visibility='always')
    ship_service = fields.Char(string='ShipServiceLevel', size=64)
    ship_category = fields.Char(string='ShipmentServiceLevelCategory')
    late_ship_date = fields.Datetime(string='LatestShipDate')
    shipped_by_amazon = fields.Boolean(string='ShippedByAmazonTFM')
    order_type = fields.Char(string='OrderType')
    amazon_order_status = fields.Char(string='OrderStatus')
    earlier_ship_date = fields.Datetime(string='EarliestShipDate')
    amazon_payment_method = fields.Char(string='PaymentMethod')
    amazon_order = fields.Boolean(string='Amazon ORder')
    updated = fields.Boolean(string='Updated Orders', default=False)
    item_shipped = fields.Char(string='Number of item shipped')
    item_unshipped = fields.Char(string='Number of item unshipped')
    is_prime = fields.Boolean(string='Is Prime')
    fullfillment_shop = fields.Char(string='Fullfillment Shop')
#     amazon_orderlisting_ids = fields.One2many('amazon.order.listing', 'sale_id','Order Listing')
    stateorigin = fields.Char(string='State Or Region')
    amazonstate_id= fields.Many2one(related='partner_id.state_id', string='State', store=True)
    recipient_name = fields.Char(string='Recipient Name')
    
      
    def oe_status(self):
        self.action_confirm()
        return True
    
    def oe_status_invoice(self, cr, uid, ids):
        for order in self:
            order.invoice_ids.signal_workflow('invoice_open')
            order.invoice_ids.invoice_pay_customer_base()
        return True
    
    # def create(self, vals):
    #     print ("valsvalsvalsvalsvals",vals)
    #     res = super(SaleOrder, self).create(vals)
    #     print ("resresresresresres",res)
    #     return res
    

class amazon_sale_order_fee_ept(models.Model):
    _name="amazon.sale.order.fee.ept"
    
    fee_type=fields.Char(string="Fee Type")
    amount=fields.Float(string="Amount")
    is_refund=fields.Boolean(string="Is Refund")
    amazon_sale_order_line_id=fields.Many2one("sale.order.line",string="Amazon Sale Order Line")    

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    

    order_item_id = fields.Char(string='Order Item ID', size=256)
    asin = fields.Char(string='Asin', size=256)
    notes = fields.Char(string='Notes',size=256)
    item_price = fields.Float(string='Item Price')
    shipping_price = fields.Float(string='Shipping Price')
    gift_cost = fields.Float(string='Gift Costs')
    new_tax_amount = fields.Float(string='New Tax')
    
    
    
    def _prepare_invoice_line(self, qty):
        """
        Prepare the dict of values to create the new invoice line for a sales order line.

        :param qty: float quantity to invoice
        """
        self.ensure_one()
        res = {}
        account = self.product_id.property_account_income_id or self.product_id.categ_id.property_account_income_categ_id
        if not account:
            raise UserError(_('Please define income account for this product: "%s" (id:%d) - or for its category: "%s".') %
                (self.product_id.name, self.product_id.id, self.product_id.categ_id.name))

        fpos = self.order_id.fiscal_position_id or self.order_id.partner_id.property_account_position_id
        if fpos:
            account = fpos.map_account(account)

        res = {
            'name': self.name,
            'sequence': self.sequence,
            'origin': self.order_id.name,
            'account_id': account.id,
            'price_unit': self.price_unit,
            'new_tax_amount':self.new_tax_amount,
            'quantity': qty,
            'discount': self.discount,
            'uom_id': self.product_uom.id,
            'product_id': self.product_id.id or False,
#             'layout_category_id': self.layout_category_id and self.layout_category_id.id or False,
            'invoice_line_tax_ids': [(6, 0, self.tax_id.ids)],
            'account_analytic_id': self.order_id.analytic_account_id.id,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
        }
        return res
    
#     @api.multi
#     def name_get(self):
#         result = []
#         for so_line in self:
#             name = '%s - %s' % (so_line.order_id.name, so_line.name.split('\n')[0] or so_line.product_id.name)
#             if so_line.order_partner_id.ref:
#                 name = '%s (%s)' % (name, so_line.order_partner_id.ref)
#             result.append((so_line.id, name))
#         return result
# 
#     @api.model
#     def name_search(self, name='', args=None, operator='ilike', limit=100):
#         if operator in ('ilike', 'like', '=', '=like', '=ilike'):
#             args = expression.AND([
#                 args or [],
#                 ['|', ('order_id.name', operator, name), ('name', operator, name)]
#             ])
#         return super(SaleOrderLine, self).name_search(name, args, operator, limit)
    
    
    
    
    
    
    
