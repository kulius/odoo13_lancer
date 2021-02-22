# -*- coding: utf-8 -*-
from odoo.exceptions import UserError
from odoo import api, fields, models, _

class  UploadAmazonAllProducts(models.TransientModel):
    _name = "upload.amazon.all.products"

#    @api.multi
    def upload_amazon_products(self):
        self.shop_ids.with_context({'prodduct_ids': self._context.get('active_ids')}).export_amazon_products()   
        self.upload_inventory()
        return True

    def upload_shipping_price(self):
        self.shop_ids.with_context({'pruduct_ids': self._context.get('active_ids')}).upload_shipping_price()
        return True

#    @api.multi
    def upload_inventory(self):
        self.shop_ids.with_context({'product_ids': self._context.get('active_ids')}).update_inventory_on_amazon()
        return True

#    @api.multi
    def upload_pricing(self):
        self.shop_ids.with_context({'product_ids': self._context.get('active_ids')}).update_amazon_product_price()
        return True

    def update_image(self):
        product_obj = self.env['product.product']
        images = []
        for product in product_obj.browse(self._context.get('active_ids')):
            images.extend(product.image_ids.ids)
        self.shop_ids.with_context({'image_ids': images}).update_images_on_amazon()
        return True
    
    
#    @api.multi
    def upload_zero_inventory(self):
        shop_obj = self.env['sale.shop']
        product_obj = self.env['product.product']
        suppl_price_obj = self.env['update.supplier.price']
        
        shop_ids = shop_obj.search([('amazon_shop','=',True)])
        if not shop_ids:
            return False
        
        if self.ids:
            if not self.bulk_upload:
                product_ids = self._context['active_ids']
                self._context['active_ids'] = []
            else:
                product_ids = product_obj.search([('asin','!=',False),('active','=',True)])
        else:
            product_ids = product_obj.search([('asin','!=',False),('active','=',True)])
        
        shop_ids.with_context({'product_ids': product_ids}).upload_zero_inventory_on_amazon
        suppl_price_obj.send_email_admin('Stock Updated on Amazon','Stock Update on Amazon')
        return True

    name = fields.Char(string='Name', size=100, readonly=True)
    bulk_upload = fields.Boolean(string='Bulk Upload')
    sku_file = fields.Binary(string='SKU File', size=100)
    shop_ids = fields.Many2many('sale.shop', string="Select Shops")
      

