# -*- coding: utf-8 -*-
from odoo import api, fields, models,_
import ast
import random

class UpdateProd(models.TransientModel):
    _name = "update.prod"
    
    name = fields.Float('Start Price',required=True)
    end_price = fields.Float('End Price',required=True)
    is_ebay = fields.Boolean('Ebay')
    is_amazon = fields.Boolean('Amazon')
    is_buy = fields.Boolean('Buy')
    is_random = fields.Boolean('Random')

#    @api.one
    def get_price(self, data, list_data):
        if data.is_random:
            price  = '%2f' % random.uniform(data.name,data.end_price)
        else:
            if str(data.name).find('-') == -1 :
                price = list_data.price + float(data.name)
            else:
                price = list_data.price + float(data.name)
        return price

#    @api.multi
    def update_price(self):
        amazon_prod_list_obj = self.env['amazon.product.listing']
        ebay_prod_list_obj = self.env['product.listing']
        buy_prod_list_obj = self.env['buy.product.listing']
        
        for data in self:
            if data.is_amazon:
                amazon_list_ids = amazon_prod_list_obj.search([('product_id', '=', self.context['active_id'])])
                for amazon_list_id in amazon_list_ids:
                    price  = self.get_price(data,amazon_list_id)
                    amazon_list_id.write({'price':price})
                    
            if data.is_ebay:
                ebay_list_ids = ebay_prod_list_obj.search([('prod_list', '=', self._context['active_id'])])
                for ebay_list_id in ebay_list_ids:
                    price  = self.get_price(data, ebay_list_id)
                    ebay_list_id.write({'price':price})
                    
            if data.is_buy:
                buy_list_ids = buy_prod_list_obj.search([('product_id', '=', self._context['active_id'])])
                for buy_list_id in buy_list_ids:
                    price  = self.get_price(data,buy_list_id)
                    buy_list_id.write({'price':price})
        return {'type': 'ir.actions.act_window_close'}
