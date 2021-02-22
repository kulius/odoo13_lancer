# -*- coding: utf-8 -*-
from odoo import api, fields, models,_

class SaleAmazon(models.TransientModel):
    _name='sale.amazon'
    
#    @api.model
    def default_get(self, fields_list):
        res = super(SaleAmazon, self).default_get(fields)
        
        if self._context.get('active_id',[]) and self._context.get('active_model') =='sale.order':
            sale_rec = self.env[self._context.get('active_model')].browse(self._context.get('active_id',[]))
            lines = []
            for line in sale_rec.order_line:
                if line.product_id:
                    lines.append({
                        'seller_sku':line.product_id.default_code,
                        'quantity': line.product_uom_qty,
                        })
        res.update({
                'partner_id':sale_rec.partner_id and sale_rec.partner_id.name or False,
                'address_line1':sale_rec.partner_id.street or '',
                'address_line2':sale_rec.partner_id.street2 or '',
                'city':sale_rec.partner_id.city or '',
                'state':sale_rec.partner_id.state_id and sale_rec.partner_id.state_id.name or False,
                'postal_code':sale_rec.partner_id.zip or '',
                'country_code':sale_rec.partner_id.country_id and sale_rec.partner_id.country_id.name or False,
              
                })
        if lines:
            res.update({'order_line1':lines})
        return res
    
#    @api.multi()    
    def create_inbound_shipment(self,cr,uid,ids,context):
        return {
                'type': 'ir.actions.act_window_close'
         }

        partner_id = fields.Char('Name')
        address_line1 = fields.Char('Address Line1')
        address_line2 = fields.Char('Address Line2')
        city = fields.Char('City')
        state = fields.Char('State')
        postal_code = fields.Char('Postal Code')
        country_code = fields.Char('Country Code')
        order_line1 = fields.One2many('amazon.ship.process','ship_2','Order Lines')
            
class AmazonShipProcess(models.TransientModel):
    _name='amazon.ship.process'
    
    ship_2 = fields.Many2one('sale.amazon','Shipping id')
    seller_sku = fields.Char('Seller Sku')
    quantity = fields.Char('Quantity')

