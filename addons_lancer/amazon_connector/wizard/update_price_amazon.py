# -*- coding: utf-8 -*-
from odoo import api, fields, models,_
from odoo.addons.amazon_connector.amazon_api import amazonerp_osv as amazon_api_obj
import logging
logger = logging.getLogger('update_price_amazon')

class UpdateAmazonPrice(models.TransientModel):
    _name = "update.amazon.price"

#    @api.multi
    def update_amazon_price(self):
        sale_shop_obj = self.env['sale.shop']
        amazon_shop_ids = sale_shop_obj.search([('amazon_shop','=',True)])
        if not len(amazon_shop_ids):
            return True

        amazon_shop_ids.with_context({'product_ids': self._context['active_ids']}).update_amazon_product_price()
        return {'type': 'ir.actions.act_window_close'}

#    @api.multi
    def update_amazon_price_single(self):
        amazon_prod_list_obj=self.env['amazon.product.listing']
        product_obj=self.env['product.product']
        sale_shop_obj=self.env['sale.shop']
        
        amazon_shop_ids = sale_shop_obj.search([('amazon_shop','=',True)])
        if not len(amazon_shop_ids):
            return True

        merchant_string ="<MerchantIdentifier>%s</MerchantIdentifier>"%(amazon_shop_ids[0].amazon_instance_id.aws_merchant_id)
        price_str = """<MessageType>Price</MessageType>"""
        for product_data in product_obj.browse(self._context['active_ids']):
            message_id = 1
            price_string = ''
            amazon_list_ids = amazon_prod_list_obj.search([('product_id','=',product_data.id)])
            for amazon_list_data in amazon_list_ids:
                if float(product_data.amazon_price_new) != 0.0:
                    price_string += """<Message>
                            <MessageID>%s</MessageID>
                            <Price>
                            <SKU>%s</SKU>
                            <StandardPrice currency="USD">%.2f</StandardPrice>
                            </Price>
                            </Message>"""% (message_id,amazon_list_data.name,product_data.amazon_price_new)
                    message_id += 1

            price_data = sale_shop_obj.xml_format(price_str,merchant_string,price_string)
            logger.error('price_data---%s', price_data)
            price_submission_id = amazon_api_obj.call(amazon_shop_ids[0], 'POST_PRODUCT_PRICING_DATA',price_data)
            logger.error('price_submission_id---%s', price_submission_id)
        return True
