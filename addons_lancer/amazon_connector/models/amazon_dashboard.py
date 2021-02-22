# -*- coding: utf-8 -*-
import json
from odoo import api, fields, models, _


class SaleShop(models.Model):
    _inherit = "sale.shop"
    
    amazon_kanban_dashboard = fields.Text(compute='_amazon_kanban_dashboard')

    # Method To Show all Count of Menu on dashboard
    def _amazon_kanban_dashboard(self):
        order_obj = self.env['sale.order']
        prodcut_listing_obj = self.env['amazon.product.listing']
        product_obj = self.env['product.product']
        product_temp_obj = self.env['product.template']
        invoice_obj = self.env['account.move']
        order_id = order_obj.search([('shop_id','=',self[0].id)])
        listing_id = prodcut_listing_obj.search([('shop_id','=',self[0].id)])
        product_ids = [listing.product_id.id for listing in listing_id]

        all_prod_ids = product_obj.search([('id','in',product_ids),('amazon_product','=',True)])
        all_prod_temp_ids = product_temp_obj.search([('amazon_product','=',True)])
        exported_prod_ids = product_obj.search([('id','in',product_ids),('amazon_product','=',True),('updated_data','=',True)])
        to_exported_prod_ids = product_obj.search([('id','in',product_ids),('amazon_product','=',True),('updated_data','!=',True)])

        all_order_ids = order_obj.search([('shop_id','=',self[0].id)]) 
        pending_order_ids = order_obj.search([('shop_id','=',self[0].id),('amazon_order','!=',False),('state','!=','done')])       
        complete_order_ids = order_obj.search([('shop_id','=',self[0].id),('amazon_order','=',True),('state','=','done')])
        cancel_order_ids = order_obj.search([('shop_id','=',self[0].id),('amazon_order','=',True),('state','=','cancel')])
        
        origin_list = [s.name for s in order_id]
        all_invoice_id = invoice_obj.search([('is_amazon','=',True),('invoice_origin', 'in', origin_list)])#,('origin', 'in', origin_list)
        all_refund_id = invoice_obj.search([('is_amazon','=',True),('type','=','out_refund')])#,('origin', 'in', origin_list)
        marketplace_order_count ={
        'all_order': len(all_order_ids),
        'pending_order': len(pending_order_ids),
        'complete_order': len(complete_order_ids),
        'cancel_order': len(cancel_order_ids),

        'all_products': len(all_prod_temp_ids),
        'exported_product': len(exported_prod_ids),
        'to_exported_product': len(to_exported_prod_ids),
        'id': self[0].id,
        
        'all_invoice':len(all_invoice_id),
        'all_refund':len(all_refund_id),
        }
        
        self.amazon_kanban_dashboard = json.dumps(marketplace_order_count)


#    All Dashboard Method for Orders, products and invoices

    def action_view_order(self):
        order_obj = self.env['sale.order']
        order_id = order_obj.search([('shop_id','=',self[0].id)])
        imd = self.env['ir.model.data']
        list_view_id = imd.xmlid_to_res_id('amazon_connector.amazon_sale_order_tree_view')
        form_view_id = imd.xmlid_to_res_id('sale.view_order_form')
        model, action_id = imd.get_object_reference('amazon_connector', "action_amazon_sale_view")
        [action] = self.env[model].browse(action_id).read()
        if len(order_id) > 1:
            action['domain'] = "[('id','in',%s)]" % order_id.ids
        elif len(order_id) == 1:
            action['res_id'] = order_id.ids[0]
        else:
            return {'type': 'ir.actions.act_window_close'}
        return action
    
    
    def action_amazon_pending_order(self):
        order_obj = self.env['sale.order']
        order_id = order_obj.search([('shop_id','=',self[0].id),('amazon_order','=',True),('state','!=','done')])
        imd = self.env['ir.model.data']
        model, action_id = imd.get_object_reference('amazon_connector', "action_amazon_sale_pending")
        [action] = self.env[model].browse(action_id).read()
        if len(order_id) > 1:
            action['domain'] = "[('id','in',%s)]" % order_id.ids
        elif len(order_id) == 1:
            action['res_id'] = order_id.ids[0]
        else:
            return {'type': 'ir.actions.act_window_close'}
        return action
    
    
    
    def action_amazon_complete_order(self):
        order_obj = self.env['sale.order']
        order_id = order_obj.search([('shop_id','=',self[0].id),('amazon_order','=',True),('state','=','done')])
        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object('amazon_connector.action_amazon_sale_done')
        list_view_id = imd.xmlid_to_res_id('amazon_connector.amazon_sale_order_tree_view')
        form_view_id = imd.xmlid_to_res_id('sale.view_order_form')
        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form'], [False, 'kanban'], [False, 'pivot']],
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }
        if len(order_id) > 1:
            result['domain'] = "[('id','in',%s)]" % order_id.ids
        elif len(order_id) == 1:
            result['views'] = [(form_view_id, 'form')]
            result['res_id'] = order_id.ids[0]
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result
    
    
    def action_view_cance_order(self):
        order_obj = self.env['sale.order']
        order_id = order_obj.search([('shop_id','=',self[0].id),('amazon_order','=',True),('state','=','cancel')])
        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object('amazon_connector.action_amazon_orders_cancel')
        list_view_id = imd.xmlid_to_res_id('amazon_connector.amazon_sale_order_tree_view')
        form_view_id = imd.xmlid_to_res_id('sale.view_order_form')
        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form'], [False, 'kanban'], [False, 'pivot']],
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }
        if len(order_id) > 1:
            result['domain'] = "[('id','in',%s)]" % order_id.ids
        elif len(order_id) == 1:
            result['views'] = [(form_view_id, 'form')]
            result['res_id'] = order_id.ids[0]
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result

#All Dashboard Method for Product

    def action_view_all_product(self):
        prodcut_listing_obj = self.env['amazon.product.listing']
        product_obj = self.env['product.product']
        product_temp_obj = self.env['product.template']
        listing_id = prodcut_listing_obj.search([('shop_id','=',self[0].id)])
        product_ids = [listing.product_id.id for listing in listing_id]
        prod_id = product_obj.search([('id','in',product_ids)])
        prod_temp_ids = product_temp_obj.search([('amazon_product', '=', True)])
        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object('amazon_connector.amazon_product_normal_action_inherit')
        list_view_id = imd.xmlid_to_res_id('amazon_connector.amazon_product_product_tree_view_inherit_id')
        form_view_id = imd.xmlid_to_res_id('amazon_connector.product_normal_form_view_inherit')
        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form'], [False, 'kanban'], [False, 'pivot']],
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }
        if len(prod_temp_ids) > 1:
            result['domain'] = "[('id','in',%s)]" % prod_temp_ids.ids
        elif len(prod_temp_ids) == 1:
            result['views'] = [(form_view_id, 'form')]
            result['res_id'] = prod_temp_ids.ids[0]
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result

    def action_view_product_exported(self):
        prodcut_listing_obj = self.env['amazon.product.listing']
        product_obj = self.env['product.product']
        listing_id = prodcut_listing_obj.search([('shop_id','=',self[0].id)])
        product_ids = [l.product_id.id for l in listing_id]
        prod_id = product_obj.search([('id','in',product_ids),('amazon_product','=',True),('updated_data','=',True)])
        # prod_id = product_obj.search([('id','in',product_ids),('amazon_product','=',True),('updated','=',True)])
        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object('amazon_connector.amazon_product_normal_action_inherit')
        list_view_id = imd.xmlid_to_res_id('amazon_connector.amazon_product_product_tree_view_inherit_id')
        form_view_id = imd.xmlid_to_res_id('amazon_connector.product_normal_form_view_inherit')
        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form'], [False, 'kanban'], [False, 'pivot']],
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }
        if len(prod_id) > 1:
            result['domain'] = "[('id','in',%s)]" % prod_id.ids
        elif len(prod_id) == 1:
            result['views'] = [(form_view_id, 'form')]
            result['res_id'] = prod_id.ids[0]
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result

    def action_view_product_tobe_exported(self):
        prodcut_listing_obj = self.env['amazon.product.listing']
        product_obj = self.env['product.product']

        listing_id = prodcut_listing_obj.search([('shop_id','=',self[0].id)])
        product_ids = [listing.product_id.id for listing in listing_id]
        prod_id = product_obj.search([('id','in',product_ids),('amazon_product','=',True),('updated_data','!=',True)])
        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object('amazon_connector.amazon_product_normal_action_inherit')
        list_view_id = imd.xmlid_to_res_id('amazon_connector.amazon_product_product_tree_view_inherit_id')
        form_view_id = imd.xmlid_to_res_id('amazon_connector.product_normal_form_view_inherit')
        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form'], [False, 'kanban'], [False, 'pivot']],
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }
        if len(prod_id) > 1:
            result['domain'] = "[('id','in',%s)]" % prod_id.ids
        elif len(prod_id) == 1:
            result['views'] = [(form_view_id, 'form')]
            result['res_id'] = prod_id.ids[0]
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result
    
    
    def action_view_all_amazon_invoices(self):
        order_obj = self.env['sale.order']
        invoic_obj = self.env['account.move']
        order_id = order_obj.search([('shop_id','=',self[0].id)])
        print("order_idasdassdsddddddd",order_id)
        origin_list = [s.name for s in order_id]
        invoice_id = invoic_obj.search([('is_amazon','=',True),('origin', 'in', origin_list)])#('origin', 'in', origin_list)
        print ("invoice_idssssssssssss", invoice_id)
        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object('amazon_connector.action_amazon_invoice_orders')
        list_view_id = imd.xmlid_to_res_id('account.invoice_tree')
        form_view_id = imd.xmlid_to_res_id('account.invoice_form')
        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form'], [False, 'kanban'], [False, 'pivot']],
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }
        print ("resulttttttttttt", result)
        if len(invoice_id) >= 1:
            result['domain'] = "[('id','in',%s)]" % invoice_id.ids
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result


    def action_view_refund_invoice(self):
        order_obj = self.env['sale.order']
        invoic_obj = self.env['account.move']
        order_id = order_obj.search([('shop_id','=',self[0].id)])
        invoice_id = invoic_obj.search([('is_amazon','=',True),('type','=', 'out_refund')])
        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object('amazon_connector.action_invoice_refund_invoice_orders')
        list_view_id = imd.xmlid_to_res_id('account.invoice_tree')
        form_view_id = imd.xmlid_to_res_id('account.invoice_form')
        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form'], [False, 'kanban'], [False, 'pivot']],
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }
        if len(invoice_id) >= 1:
            result['domain'] = "[('id','in',%s)]" % invoice_id.ids
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result


