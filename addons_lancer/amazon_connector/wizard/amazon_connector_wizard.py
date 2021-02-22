# -*- coding: utf-8 -*-
import time
from odoo.addons.amazon_connector.amazon_api import amazonerp_osv as amazon_api_obj
from odoo import api, fields, models, _
import time

class AmzonConnectorWizard(models.TransientModel):
    _name = "amazon.connector.wizard"
    
    
    shop_ids = fields.Many2many('sale.shop', string="Select Shops")
    
    import_orders = fields.Boolean('Import Orders')
    import_products = fields.Boolean('Import Products')
    import_browsenode = fields.Boolean('Import Category')
    import_inventory = fields.Boolean('Import Inventory')
    import_FBA_inventory = fields.Boolean('Import FBA Inventory')
    
    update_product = fields.Boolean('Update Simple&Variants Products')
    update_inventory = fields.Boolean('Update Inventory')
    update_price = fields.Boolean('Update Price')
    update_image = fields.Boolean('Update Images')
    update_order_status = fields.Boolean('Update Order Status')
    
    
    export_product = fields.Boolean('Export Products')
    
#     Last updated Fields on importation part
    last_date_of_product_import = fields.Datetime(string='Last Product Import Date')
    last_amazon_order_import_date = fields.Datetime(string='Last Order Import  Time')

    @api.model
    def default_get(self, fields):
        shop_obj = self.env['sale.shop']
        print ("self._context.get('active_ids')",self._context.get('active_ids'))
        result= super(AmzonConnectorWizard, self).default_get(fields)
        if self._context.get('active_model') == 'sale.shop':
            if len(self._context.get('active_ids')) == 1:
                shop_data = shop_obj.browse(self._context.get('active_ids')[0])
                result.update({'last_date_of_product_import': shop_data.last_date_of_product_import,
                               'last_amazon_order_import_date':shop_data.last_amazon_order_import_date})
            result.update({'shop_ids': self._context.get('active_ids')})
        return result
    
#    @api.multi
    def import_amazon(self): 
        if self.import_browsenode:
            self.shop_ids.importAmazoncategory()
        if self.import_products:
            self.shop_ids.with_context({'last_date_of_product_import': self.last_date_of_product_import}).import_amazon_product()
        if self.import_inventory:
            self.shop_ids.import_amazon_inventory()
        if self.import_FBA_inventory:
            self.shop_ids.import_amazon_FBA_Inventory()
        if self.import_orders:
            self.shop_ids.with_context({'last_amazon_order_import_date': self.last_amazon_order_import_date}).amazon_import_orders()

#     UPDATE FUNCTION
        if self.update_product:
            self.shop_ids.with_context({'from_update_product':True}).export_amazon_products()
        if self.update_inventory:
            self.shop_ids.update_amazonInventory()
        if self.update_price:
            self.shop_ids.update_amazonPrice()
        if self.update_image:
            self.shop_ids.update_amazonImages()
        if self.update_order_status:
            self.shop_ids.update_amazon_orders()
            
#     EXPORT FUNCTION
            
        if self.export_product:
            self.shop_ids.export_amazon_products()
        return True
    
    
    
class PricelistWizard(models.TransientModel):
    _name = "amazon.pricelist.wizard"  
    
    wiz_shop_ids = fields.Many2many('sale.shop','wiz_shops','wiz_shop_id_rel',string='Shops')  

#     @api.multi
#     def get_pricelist_product(self):
#         product_obj = self.env['product.product']
#         pricelist = self.env['product.pricelist']
#         for shops in self.wiz_shop_ids:
#             product_tmpl_ids = []
#             product_ids = product_obj.search([('id','=',177)])#,('amazon_product','=',True),('amazon_export','=',False)])
#             for product in product_ids:
#                 print "product111",product
#                 if product.product_tmpl_id not in product_tmpl_ids:
#                     product_tmpl_ids.append(product.product_tmpl_id)
#             if product_tmpl_ids:
#                 pricelist_active_id = self.env['product.pricelist'].browse(self.env.context.get('active_id'))
#                 print"pricelist_active_id",pricelist_active_id
#                 errr
#                 shops.with_context({'product_tmpl_ids':product_tmpl_ids, 'price_list_id': pricelist_active_id}).update_amazonPrice()
                
#    @api.multi
    def get_pricelist_product(self):
        product_obj = self.env['product.product']
        template_obj = self.env['product.template']
        pricelist = self.env['product.pricelist']
        for shops in self.wiz_shop_ids:
            pricelist_id = self.env['product.pricelist'].browse(self.env.context.get('active_id'))
            print("pricelist_id",pricelist_id)
            for pricelist_item in pricelist_id.item_ids:
                if pricelist_item.applied_on=='1_product':
                    template = template_obj.search([('id','=',pricelist_item.product_tmpl_id.id)])
                    print("template",template)
                    if template:
                        product_obj.with_context({'price_list_id': pricelist_id}).StandardSalePrice([],shops,template)
                elif pricelist_item.applied_on=='0_product_variant':
                    product = product_obj.search([('id','=',pricelist_item.product_id.id)])
                    print ('product',product)
                    if product:
                        product_obj.with_context({'price_list_id': pricelist_id}).StandardSalePrice(product,shops,[])
                elif pricelist_item.applied_on=='3_global':
                    template_ids = template_obj.search([('amazon_product','=',True),('amazon_export','=',False)])
                    print("template_ids",template_ids)
                    for tem_data in template_ids:
                        print("tem_data",tem_data)
                        product_ids = product_obj.search([('product_tmpl_id','=',tem_data.id)])
                        product_obj.with_context({'price_list_id': pricelist_id}).StandardSalePrice(product_ids,shops,tem_data)
                
#                price_rule = pricelist_active_id._compute_price_rule([(product, 1, 1)])
#                 print"price_rule",price_rule
#                 item = self.env['product.pricelist.item'].browse(price_rule.get(product.id)[1])
#                 print"item",item.start_date,item.end_date,
#                 itemprice = price_rule.get(product.id)[0]
#                 print"itemprice",itemprice
#                 err
#                 shops.StandardSalePrice(product,shops,pricelist_active_id)
    
    
#    @api.multi
    def AmazonSalePrice(self,product,instance,active_id):
        str=''
        merchant_string ="<MerchantIdentifier>%s</MerchantIdentifier>"%(instance.amazon_instance_id.aws_merchant_id)
        message_information = ''
        message_id = False
        message_information += """<MessageType>Price</MessageType>"""
        message_id = message_id +1
        offer = ''
#             off_price = product.with_context(pricelist=instance.pricelist_id.id).price
#             if off_price !=  product.standard_price:
        price_rule = active_id._compute_price_rule([(product, 1, 1)])
        item_date = self.env['product.pricelist.item'].browse(price_rule.get(product.id)[1])
        print("item_date",item_date)
        itemprice = price_rule.get(product.id)[0]
        print("itemprice",itemprice)

        if itemprice < product.amazon_standard_price:
            offer = """<Sale>
                        <StartDate>%s</StartDate>
                        <EndDate>%s</EndDate>
                         <SalePrice currency="%s">%s</SalePrice>
                        </Sale>"""%(item_date.date_start,item_date.date_end,instance.res_currency.name, itemprice)
            print("offer",offer)
        message_information += """<Message>
                                <MessageID>%s</MessageID>
                                <Price>
                                <SKU>%s</SKU>
                                <StandardPrice currency="%s">%s</StandardPrice>
                                %s
                                </Price>
                                </Message>
                            """%(message_id, product.default_code,instance.res_currency.name, product.amazon_standard_price,offer)

        print("message_information",message_information)
        if templat.e:
            message_id = message_id +1
    #             offer1 = ''
    #             off1_price = template.with_context(pricelist=instance.pricelist_id.id).price
    #             if off1_price !=  template.tem_standard_price:
            offer1 = """<Sale> 
                        <StartDate>2018-02-14T00:00:00Z</StartDate>
                        <EndDate>2018-03-27T00:00:00Z</EndDate>
                         <SalePrice currency="%s">%s</SalePrice>
                        </Sale>"""%(instance.res_currency.name, template.amazon_price)
            message_information += """<Message>
                                    <MessageID>%s</MessageID>
                                    <Price>
                                    <SKU>%s</SKU>
                                    <StandardPrice currency="%s">%s</StandardPrice>%s
                                    </Price>
                                </Message>
                                """%(message_id, template.amazon_sku,instance.res_currency.name,template.tem_standard_price,offer1)
                            
        str = """<?xml version="1.0" encoding="utf-8" ?>
    <AmazonEnvelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="amznenvelope.xsd">
    <Header>
    <DocumentVersion>1.01</DocumentVersion>"""+merchant_string+"""
            </Header>
            """+message_information+"""
            """
        str +="""</AmazonEnvelope>"""
        print("str",str)
        if str:
            relation_submission_id = amazon_api_obj.call(instance, 'POST_PRODUCT_PRICING_DATA',str)
            print("price_submission_id",relation_submission_id)
    
