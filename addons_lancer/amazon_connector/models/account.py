# -*- coding: utf-8 -*-
import logging
logger = logging.getLogger('amazon')

from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import UserError
class AccountInvoice(models.Model):
    _inherit = "account.move"

    is_amazon = fields.Boolean(string='Is Amazon')
    fullfilment_shop = fields.Selection([('MFN','MFN'),('AFN','AFN')],'Fullfillment Shop',track_visibility='always')

    def invoice_pay_customer_base(self):
        order_obj = self.env['sale.order']
        for rec in self:
            ctx = self._context.copy()
            if rec.type == 'out_invoice' and (rec.fullfilment_shop=='MFN' or rec.fullfilment_shop=='AFN'):
             
                self.env.cr.execute("SELECT invoice_id, order_id FROM sale_order_invoice_rel WHERE invoice_id =%d" % (rec.id,))
                saleorder_res = dict(self.env.cr.fetchone())
                saleorder_id = saleorder_res[saleorder_res[1]]
                order = order_obj.browse(saleorder_id)
                 
                ctx['type'] = 'out_invoice'
                journal_id = self.with_context(ctx)._get_journal()
                currency_id = self.with_context(ctx)._get_currency()
                ctx['currency_id'] = currency_id
                if rec.state == 'draft':
                    rec.signal_workflow('invoice_open')
                rec.with_conetxt(ctx).pay_and_reconcile(journal_id, rec.amount_total)
                order.write({'state':'done'})
        return True
    
    
    
    def create(self, vals):
        if vals.get('type') =='out_refund':
            origin_id = self.search([('number','=',vals.get('origin'))])
            if origin_id:
                vals.update({'is_amazon':True})
        if self._context.get('from_amazon',False):
            vals.update({'is_amazon':True})
        return super(AccountInvoice, self).create(vals)
    
    def invoice_pay_customer(self):
        order_obj = self.env['sale.order']
        purchase_obj = self.env['purchase.order']
        for invoice in self:
            if invoice.type == 'out_invoice':
                self.env.cr.execute("SELECT invoice_id, order_id FROM sale_order_invoice_rel WHERE invoice_id =%d" % (invoice.id,))
                saleorder_res = dict(self.env.cr.fetchone())
                saleorder_id = saleorder_res[1]
                order = order_obj.browse(saleorder_id)
                journal = order.journal_id.id
                acc_id = journal.default_credit_account_id and journal.default_credit_account_id.id
                if not acc_id:
                    raise UserError(_('Your journal must have a default credit and debit account.'))
                invoice.signal_workflow('invoice_open')
                invoice.pay_and_reconcile(journal, invoice.amount_total)
                order.write({'state': 'done'})
    
            elif invoice.type == 'in_invoice':
                self.env.cr.execute("SELECT invoice_id, purchase_id FROM purchase_invoice_rel WHERE invoice_id =%d" % (invoice.id,))
                purchase_res = dict(self.env.cr.fetchone())
                purchase_id = purchase_res[1]
                purchase = purchase_obj.browse(purchase_id)
                journal = purchase.journal_id
                acc_id = journal.default_credit_account_id and journal.default_credit_account_id.id
                if not acc_id:
                    raise UserError(_('Your journal must have a default credit and debit account.'))
                paid = True
                picking_ids = purchase.picking_ids
                if picking_ids:
                    for picking in picking_ids:
                        picking.write({'invoice_state':'invoiced'})
                        if picking.state == 'done':
                            purchase.write({'state':'done'})
                        else:
                            purchase.write({'state':'invoiced'})
                else:
                    purchase.write({'state':'invoiced'})
                invoice.pay_and_reconcile(journal, invoice.amount_total)
        return True
    
    def get_taxes_values(self):
        sale_obj=self.env['sale.order']
        tax_grouped = {}
        for line in self.invoice_line_ids:
            price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            sale_id = sale_obj.search([('name','=',self.origin)]) 
#             if sale_id.amazon_order or sale_id.magento_order:
#                  taxes = line.invoice_line_tax_ids.with_context({'new_amount_tax':line}).compute_all(price_unit, self.currency_id, line.quantity, line.product_id, self.partner_id)['taxes']
#             else:
            taxes = line.invoice_line_tax_ids.compute_all(price_unit, self.currency_id, line.quantity, line.product_id, self.partner_id)['taxes']
            for tax in taxes:
                val = self._prepare_tax_line_vals(line, tax)
                key = self.env['account.tax'].browse(tax['id']).get_grouping_key(val)
 
                if key not in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key]['amount'] += val['amount']
                    tax_grouped[key]['base'] += val['base']
        return tax_grouped

    
    def confirm_paid(self):
        order_obj = self.env['sale.order']
        res = super(AccountInvoice, self).confirm_paid()
        for rec in self:
            if res.type == 'out_invoice':
                self.env.cr.execute("SELECT invoice_id, order_id FROM sale_order_invoice_rel WHERE invoice_id =%d" % (rec.id,))
                saleorder_res = dict(self.env.cr.fetchone())
                saleorder_id = saleorder_res[saleorder_res[1]]
                order = order_obj.browse(saleorder_id).order_policy
                if order.order_policy == 'prepaid':
                    order.write({'state':'progress'})
                else:
                    order.write({'state':'done'})
                    order.picking_ids.write({'invoice_state':'invoiced'})
        return res
    
class AccountInvoiceLine(models.Model):
    _inherit='account.move.line'
        
    shipping_price=fields.Float('Shipping Price')
    ship_discount=fields.Float('Shipping Discount')
    gift_cost=fields.Float('Gift Cost')
    new_tax_amount = fields.Float(string="New tax")
    
    
    
class AccountTax(models.Model):
    _inherit='account.tax'
    
    amazon_country_id = fields.Many2one('res.country',string='Amazon Country')
    amazon_state_id = fields.Many2one('res.country.state',string='Amazon State',domain="[('country_id', '=', amazon_country_id)]")

         
    def compute_all(self, price_unit, currency=None, quantity=1.0, product=None, partner=None):
        """ Returns all information required to apply taxes (in self + their children in case of a tax goup).
            We consider the sequence of the parent for group of taxes.
                Eg. considering letters as taxes and alphabetic order as sequence :
                [G, B([A, D, F]), E, C] will be computed as [A, D, F, C, E, G]

        RETURN: {
            'total_excluded': 0.0,    # Total without taxes
            'total_included': 0.0,    # Total with taxes
            'taxes': [{               # One dict for each tax in self and their children
                'id': int,
                'name': str,
                'amount': float,
                'sequence': int,
                'account_id': int,
                'refund_account_id': int,
                'analytic': boolean,
            }]
        } """
        if len(self) == 0:
            company_id = self.env.user.company_id
        else:
            company_id = self[0].company_id
        if not currency:
            currency = company_id.currency_id
        taxes = []
        # By default, for each tax, tax amount will first be computed
        # and rounded at the 'Account' decimal precision for each
        # PO/SO/invoice line and then these rounded amounts will be
        # summed, leading to the total amount for that tax. But, if the
        # company has tax_calculation_rounding_method = round_globally,
        # we still follow the same method, but we use a much larger
        # precision when we round the tax amount for each line (we use
        # the 'Account' decimal precision + 5), and that way it's like
        # rounding after the sum of the tax amounts of each line
        prec = currency.decimal_places

        # In some cases, it is necessary to force/prevent the rounding of the tax and the total
        # amounts. For example, in SO/PO line, we don't want to round the price unit at the
        # precision of the currency.
        # The context key 'round' allows to force the standard behavior.
        round_tax = False if company_id.tax_calculation_rounding_method == 'round_globally' else True
        round_total = True
        if 'round' in self.env.context:
            round_tax = bool(self.env.context['round'])
            round_total = bool(self.env.context['round'])

        if not round_tax:
            prec += 5

        base_values = self.env.context.get('base_values')
        if not base_values:
            total_excluded = total_included = base = round(price_unit * quantity, prec)
        else:
            total_excluded, total_included, base = base_values

        # Sorting key is mandatory in this case. When no key is provided, sorted() will perform a
        # search. However, the search method is overridden in account.tax in order to add a domain
        # depending on the context. This domain might filter out some taxes from self, e.g. in the
        # case of group taxes.
        for tax in self.sorted(key=lambda r: r.sequence):
            if tax.amount_type == 'group':
                children = tax.children_tax_ids.with_context(base_values=(total_excluded, total_included, base))
                ret = children.compute_all(price_unit, currency, quantity, product, partner)
                total_excluded = ret['total_excluded']
                base = ret['base'] if tax.include_base_amount else base
                total_included = ret['total_included']
                tax_amount = total_included - total_excluded
                taxes += ret['taxes']
                continue

            tax_amount = tax._compute_amount(base, price_unit, quantity, product, partner)
            if not round_tax:
                tax_amount = round(tax_amount, prec)
            else:
                tax_amount = currency.round(tax_amount)

            if tax.price_include:
                total_excluded -= tax_amount
                base -= tax_amount
            else:
                total_included += tax_amount

            # Keep base amount used for the current tax
            tax_base = base

            if tax.include_base_amount:
                base += tax_amount
            amount = tax_amount
            if self.env.context.get('new_amount_tax'):
                amount = self.env.context.get('new_amount_tax').new_tax_amount
            taxes.append({
                'id': tax.id,
                'name': tax.with_context(**{'lang': partner.lang} if partner else {}).name,
                'amount': amount,
                'base': tax_base,
                'sequence': tax.sequence,
                'account_id': tax.account_id.id,
                'refund_account_id': tax.refund_account_id.id,
                'analytic': tax.analytic,
                'price_include': tax.price_include,
            })

        return {
            'taxes': sorted(taxes, key=lambda k: k['sequence']),
            'total_excluded': currency.round(total_excluded) if round_total else total_excluded,
            'total_included': currency.round(total_included) if round_total else total_included,
            'base': base,
        }    
         
         
         
         
         
         
         
              
