# -*- coding: utf-8 -*-
import logging
logger = logging.getLogger('amazon')
from odoo.addons.amazon_connector.amazon_api import amazonerp_osv as amazon_api_obj
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class AmazonSellerInstance(models.Model):
    _name = 'amazon.seller.instance'
    
    def _get_marketplace_count(self):
        market_p_ids = []
        for market in self:
            print("------- get_marketplace_count===>>>>>>",market, market.id)
            market_p_ids = self.env['sale.shop'].search([('amazon_instance_id', '=', market.id)])
            print("----market_p_ids--->>>>",market_p_ids)
            market.marketplace_count = len(market_p_ids)
    
    name =  fields.Char(string='Name', size=64)
    aws_access_key_id = fields.Char(string="Access Key", size=64)
    aws_secret_access_key = fields.Char(string="Secret Key", size=64)
    marketplace_count = fields.Integer(string="Marketplace Count", compute=_get_marketplace_count)
    aws_merchant_id = fields.Char(string="Merchant ID", size=64)
    amazon = fields.Boolean(string='Amazon')
    domain = fields.Selection([("ca", "Canada"),
                                ("com.mx", "Mexico"),
                                ("com", "US"),
                                ("fr", "France"),
                                ("de", "Germany"),
                                ("it", "Italy"),
                                ("es", "Spain"),
                                ("co.uk", "UK"),
                                ("com.br", "Brazil"),
                                ("cn", "China"),
                                ("co.jp", "Japan"),
                                ("in", "india")], string="Domain" , size=64)  
    
    def marketplace_list(self):
        shop_obj = self.env['sale.shop']
        currency_obj = self.env['res.currency']
        price_list_obj = self.env['product.pricelist']
        def_pricelist_ids = price_list_obj.search([])
        for market in self:
            results = amazon_api_obj.call(market, 'ListMarketplaceParticipations')
            logger.info("results------ %s",results)
            if isinstance(results, dict):
                if results.get('Error'):
                    error = results.get('Code')
                    raise UserError(_('Error -->  %s')%(error))
            for insta_res in results:
                    vals={
                          'name': insta_res['Name'],
                          'aws_market_place_id': insta_res['MarketplaceId'],
                          'domain_name': insta_res['DomainName'],
                          'amazon_instance_id': market[0].id,
                          'amazon_shop' : True,
                          'prefix': insta_res['Name'][:2].upper(),
                          'pricelist_id': def_pricelist_ids and def_pricelist_ids[0].id,
                    }
                    if  insta_res['DefaultCountryCode'] == 'US':
                        vals.update({'domain':'com'})

                    elif insta_res['DefaultCountryCode'] == 'CA':
                        vals.update({'domain':'ca'})

                    elif insta_res['DefaultCountryCode'] == 'MX':
                        vals.update({'domain':'com.mx'})

                    elif insta_res['DefaultCountryCode'] == 'FR':
                        vals.update({'domain':'fr'})            

                    elif insta_res['DefaultCountryCode'] == 'DE':
                        vals.update({'domain':'de'})

                    elif insta_res['DefaultCountryCode'] == 'IT':
                        vals.update({'domain':'it'})      

                    elif insta_res['DefaultCountryCode'] == 'ES':
                        vals.update({'domain':'es'}) 

                    elif insta_res['DefaultCountryCode'] in ['UK', 'GB']:
                        vals.update({'domain':'co.uk'})

                    elif insta_res['DefaultCountryCode'] == 'CN':
                        vals.update({'domain':'cn'})

                    elif insta_res['DefaultCountryCode'] == 'BR':
                        vals.update({'domain':'com.br'})

                    elif insta_res['DefaultCountryCode'] == 'JP':
                        vals.update({'domain':'com.jp'})
                    
                    elif insta_res['DefaultCountryCode'] == 'IN':
                        vals.update({'domain':'in'})
                    
                    currency = insta_res['DefaultCurrencyCode']
                    query = "select id from res_currency where name = '%s'"%(currency.strip())
                    self.env.cr.execute(query)
                    currency_id = self.env.cr.fetchone()
                    if currency_id:
                        vals.update({'res_currency': currency_id[0]})
                    else:
                        c_id = currency_obj.create({'name': currency, 'symbol': currency.strip()})
                        vals.update({'res_currency': c_id[0].id})

                    country = insta_res['DefaultCountryCode']
                    country_id = self.env['res.country'].search([('code','=',country)])
                    if country_id:
                        vals.update({'res_country' : country_id[0].id})

                    language = insta_res['DefaultLanguageCode']
                    language_id = self.env['res.lang'].search([('code','=',language)])
                    if language_id:
                        vals.update({'res_lang' : language_id[0].id})
                    shop_id  = shop_obj.create(vals)
                    print("-----shop_idshop_id------>>>",shop_id,shop_id.active_shop)
        self.env.cr.commit()
        #import Category
#         market_p_ids = shop_obj.search([('amazon_instance_id', '=', self[0].id)])
#         if market_p_ids:
#             market_p_ids.import_category()
        return True
    
    def action_get_market_place(self):
        market_p_ids = []
        market_p_ids = self.env['sale.shop'].search([('amazon_instance_id', '=', self[0].id)])
        if market_p_ids:
            market_p_ids = list(market_p_ids._ids)
        imd = self.env['ir.model.data']
        list_view_id = imd.xmlid_to_res_id('amazon_connector.view_sale_shop_tree')
        form_view_id = imd.xmlid_to_res_id('amazon_connector.amazonerp_view_shop_form')
        result = {
                "type": "ir.actions.act_window",
                "res_model": "sale.shop",
                "views": [[list_view_id, "tree"], [form_view_id, "form"]],
                "domain": [("id", "in", market_p_ids)],
        }
        if len(market_p_ids) == 1:
            result['views'] = [(form_view_id, 'form')]
            result['res_id'] = market_p_ids[0]
        return result
    
#
##    def amazon_oe_status(self, cr, uid, order_id, paid=True, context = None, defaults = None):
##        saleorder_obj = self.pool.get('sale.order')
##        order = saleorder_obj.browse(cr, uid, order_id, context)
##        if order.ext_payment_method:
##            payment_settings = saleorder_obj.payment_code_to_payment_settings(cr, uid, order.ext_payment_method, context)
##            wf_service = netsvc.LocalService("workflow")
##            print'payment_settings',payment_settings
##            print'1-------------------'
##            if payment_settings:
##                 if payment_settings.order_policy == 'prepaid':
##                    cr.execute("UPDATE sale_order SET order_policy='prepaid' where id=%d"%(order_id,))
##                    cr.commit()
##                    if payment_settings.validate_order:
##                        try:
##                            wf_service.trg_validate(uid, 'sale.order', order_id, 'order_confirm', cr)
##                        except Exception, e:
##                            self.log(cr, uid, order_id, "ERROR could not valid order")
##                        print "order.invoice_ids: ",order.invoice_ids
##                    print'2----------------------------'
##                    if payment_settings.validate_invoice:
##                        for invoice in order.invoice_ids:
##                            wf_service.trg_validate(uid, 'account.invoice', invoice.id, 'invoice_open', cr)
##                            print'3------------------'
##                            if payment_settings.is_auto_reconcile and paid:
##                                self.pool.get('account.invoice').invoice_pay_customer(cr, uid, [invoice.id], context=context)
##                                print "invoice state: ",self.pool.get('account.invoice').browse(cr,uid,invoice.id).state
##                                print'4---------------------'
##
##        return True
#
#
#    def do_partial(
#        self,
#        cr,
#        uid,
#        ids,
#        context=None,
#        ):
#
#        # no call to super!
#
#        stock_pick_obj = self.pool.get('stock.picking')
#        assert len(ids) == 1, \
#            'Partial move processing may only be done one form at a time.'
#        print ids
#        partial = stock_pick_obj.browse(cr, uid, ids[0],
#                context=context)
#        print partial
#        partial_data = {'delivery_date': partial.date}
#        print partial.move_lines
#        moves_ids = []
#        for move in partial.move_lines:
#            move_id = move.id
#            partial_data['move%s' % move_id] = \
#                {'product_id': move.product_id.id,
#                 'product_qty': move.product_qty,
#                 'product_uom': move.product_uom.id}
#
##                'prodlot_id': move.prodlot_id.id,
#
#            moves_ids.append(move_id)
#            if move.picking_id.type == 'in' \
#                and move.product_id.cost_method == 'average':
#                partial_data['move%s'
#                             % move_id].update(product_price=move.cost,
#                        product_currency=move.currency.id)
#        self.pool.get('stock.move').do_partial(cr, uid, moves_ids,
#                partial_data, context=context)
#        return True
#    def onchange_partner_id(self, cr, uid, ids, part, context=None):
#        if not part:
#            return {'value': {'partner_invoice_id': False, 'partner_shipping_id': False,  'payment_term': False, 'fiscal_position': False}}
#
#        part = self.pool.get('res.partner').browse(cr, uid, part, context=context)
#        addr = self.pool.get('res.partner').address_get(cr, uid, [part.id], ['delivery', 'invoice', 'contact'])
#        pricelist = part.property_product_pricelist and part.property_product_pricelist.id or False
#        val = {
#            'partner_invoice_id': addr['invoice'],
#            'partner_shipping_id': addr['delivery'],
#        }
#        if pricelist:
#            val['pricelist_id'] = pricelist
#        return {'value': val}
    

#        'ftp_username' : fields.char('FTP User Name',size=64,required=True),
#        'ftp_password' : fields.char('FTP Password',size=64,required=True),
#        'ftp_link' : fields.char('Link',size=64,required=True),


