# -*- coding: utf-8 -*-
from odoo import api, fields, models,_
from odoo.tools.translate import _
import ast

class AmazonProductLookup(models.TransientModel):
    _name = "amazon.product.lookup"
    _description = "Details of Amazon product found in Item Search"

    name = fields.Char('Product Name', size=64,readonly=True)
    product_asin = fields.Char('ASIN',size=10,readonly=True)
    product_category = fields.Char('Category', size=64,readonly=True)
    product_id = fields.Many2one('product.product', 'Product')
    product_attributes = fields.Many2many('amazon.products.attributes.master', 'amz_lookup_amzprodatt_rel', 'lookup_id','attribute_id','Amazon Product Attributes',readonly=True)

#    @api.multi
    def assign_asin_to_product(self):
        for rec in self:
            self.env.cr.execute("UPDATE product_product SET amz_type='ASIN',amz_type_value='%s' where id=%d"%(rec.product_asin, rec.product_id.id))
        return {'type': 'ir.actions.act_window_close'}

    @api.model
    def default_get(self, fields):
        amazon_prod_mastre_obj = self.env['amazon.products.master']
        amazon_prod_attributes_master_obj = self.env['amazon.products.attributes.master']
        defaults = super(AmazonProductLookup, self).default_get(fields)
        active_id = self._context.get('active_ids')
        if not active_id:
            return defaults

        amazon_product = amazon_prod_mastre_obj.browse(active_id[0])
        amazon_product_attributes = ast.literal_eval(amazon_product.amazon_product_attributes)

        amazon_prod_attr_ids =[]
        for key in amazon_product_attributes.keys():
                attributeVals = {
                    'attribute_name' : key,
                    'attribute_value' : amazon_product_attributes[key],
                }
                amazon_prod_master_id  = amazon_prod_attributes_master_obj.create(attributeVals)
                amazon_prod_attr_ids.append(amazon_prod_master_id)

        defaults = {
                    'name' :  amazon_product.name,
                    'product_asin' : amazon_product.product_asin,
                    'product_category' : amazon_product.product_category,
                    'product_id' : amazon_product.product_id.id,
                    'product_attributes': amazon_prod_attr_ids,
        }
        return defaults


class amazon_products_attributes_master(models.TransientModel):
    _name = "amazon.products.attributes.master"
    _rec_name = 'attribute_name'
    
    attribute_name = fields.Char('Attribute Name', size=64)
    attribute_value = fields.Char('Attribute Value', size=64)
