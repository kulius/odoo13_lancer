# -*- coding: utf-8 -*-
from odoo import api, fields, models,_

class AddListingProducts(models.TransientModel):
    _name = "add.listing.products"
    _description = "Add Listing Products"
    
    supplier_id = fields.Many2one('res.partner', 'Supplier')
    listing_ids = fields.Many2many('product.product', 'product_list_rel', 'list_wiz_id', 'prod_id', 'Product')
    act_list_id = fields.Many2one('upload.amazon.products', 'Listing ID')
    
    @api.onchange('supplier_id')
    def clearProduct(self):
        self.listing_ids = []
    
#    @api.model
    def default_get(self, fields):
        res = super(AddListingProducts, self).default_get(fields)
        if self._context.get('active_id'):
            res.update({'act_list_id' : self._context.get('active_id')})
        return res
    
    @api.onchange('listing_ids')
    def add_products(self):
        if self.supplier_id:
            supplier_info_obj = self.env['product.supplierinfo']
            sup_info_ids = supplier_info_obj.search([('name','=', self.supplier_id)])
            if sup_info_ids:
                product_ids = [(0,0,{'product_id' : sup.product_id.id }) for sup in sup_info_ids]
                self.listing_ids =  product_ids
    
#    @api.multi
    def select(self):
        list_obj = self.env['products.amazon.listing.upload']
        c_id = self._context.get('active_id')
        for line in self[0].listing_ids:
            list_obj.create({
                'is_new_listing' : True,
                'product_id' : line.id,
                'fulfillment_by' : 'MFN',
                'listing_id' : c_id
            })
        return True
    
    

