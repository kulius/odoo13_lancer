# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class ProductImages(models.Model):
    _inherit = "product.images"
    
    amazon_url_location=fields.Char('Full URL', size=256)
    

