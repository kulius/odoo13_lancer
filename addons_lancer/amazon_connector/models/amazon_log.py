# -*- coding: utf-8 -*-
import logging
logger = logging.getLogger('amazon')

from odoo import api, fields, models, _

class AmazonLog(models.Model):
    _name='amazon.log'
   
    name = fields.Char('name')
    description = fields.Char('Log Description')
    res_id = fields.Integer('Resource')
    marketplace_id = fields.Many2one('sale.shop','MarketPlace Id')
    res_model_id = fields.Many2one('ir.model','Model')
    log_type = fields.Selection([('import_order', 'Import Order'),
                             ('import_product', 'Import Product'),
                             ('import_inventory', 'Import Inventory'),
                             ('import_browsenode', 'Import Category')], string='Operation Type')
    create_date = fields.Datetime(string="Create Date")
    
    
#     @api.model
#     def create(self, vals):
#         if not vals.get('name'):
#             vals['name']= self.env['ir.sequence'].next_by_code('amazon.log') or 'Log Sequence'
#         res = super(AmazonLog, self).create(vals)
#         return res
