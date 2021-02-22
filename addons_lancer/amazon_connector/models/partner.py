# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import logging
logger = logging.getLogger('__name__')
class ResPartner(models.Model):
    _name = "res.partner"
    _inherit = "res.partner"

    amazon_customer=fields.Boolean('Amazon Customer')
    amazon_access_key= fields.Char('Amazon Access Key',size=256)
    amazon_shop_ids= fields.Many2many('sale.shop','partner_shop_id','partner_id','shop_id','Amazon Shops',readonly=True)
    street3 = fields.Char('Street3')
    
    def managepartner(self, resultval):
        # create a partner if partner is not available and return Partner ID
        logger.info('partner resultval : %s', resultval)
        res_country_obj = self.env['res.country']
        res_state_obj = self.env['res.country.state']
        pricelist_obj = self.env['product.pricelist']
        c_id = False
        if resultval.get('CountryCode'):
            print("resultval.get('CountryCode')",resultval.get('CountryCode'))
            c_ids = res_country_obj.search([('code', '=', resultval.get('CountryCode'))])
            if c_ids:
                c_id = c_ids[0].id
            else:
                code = resultval.get('CountryCode')[0:2].upper()
                c_m_ids = res_country_obj.search([('code','=', code)])
                if not c_m_ids:
                    code = resultval.get('CountryCode')[0:1]+resultval.get('CountryCode')[-1].upper()
                c_id = res_country_obj.create({'name': resultval.get('CountryCode') or resultval.get('CountryCode'), 'code': code}).id
        if not c_id and resultval.get('Country'):
            print("resultval.get('Country')",resultval.get('Country'))
            c_ids = res_country_obj.search([('name', '=', resultval.get('Country'))])
            if c_ids:
                c_id = c_ids[0].id
            else:
                c_id = res_country_obj.create({'name': resultval.get('Country'), 'code': resultval.get('Country')}).id
        s_id = False
        if resultval.get('StateOrRegion'):
            print("resultval.get('StateOrRegion')",resultval.get('StateOrRegion'))
            print("resultval.get('StateOrRegion').title()",resultval.get('StateOrRegion').title())
            s_ids = res_state_obj.search(['|',('code', '=', resultval.get('StateOrRegion').upper()),('name', '=', resultval.get('StateOrRegion').title()), ('country_id', '=', c_id)])
            if s_ids:
                s_id = s_ids[0].id
            else:
                print ("resultval.get('StateOrRegion')[1:-2].upper()",resultval.get('StateOrRegion').upper())
                s_id = res_state_obj.create({'name': resultval.get('StateOrRegion'), 'code': resultval.get('StateOrRegion').upper(), 'country_id': c_id}).id
        partner_vals = {
                        'name': resultval['Name'],
                        'street': resultval.get('AddressLine1', False),
                        'street2': resultval.get('AddressLine2', False),
                        'phone': resultval.get('Phone'),
                        'email': resultval.get('BuyerEmail'),
                        'customer':True,
                        'zip': resultval['PostalCode'],
                        'city': resultval['City'],
                        'state_id' : s_id,
                        'country_id' : c_id
        }
        
        print( "partner_vals????????", partner_vals)
#         print "partner_vals", partner_vals.state_id
        if self._context.get('shop'):
            pricelist_ids = pricelist_obj.search([('currency_id','=',self._context.get('shop').res_currency.id)])
            if pricelist_ids:
                partner_vals.update({'property_product_pricelist':pricelist_ids[0].id})
        partner_ids = self.search([('email', '=', resultval.get('BuyerEmail'))])
        if partner_ids:
            p_id = partner_ids[0]
        else:
            p_id = self.create(partner_vals)
        return p_id




