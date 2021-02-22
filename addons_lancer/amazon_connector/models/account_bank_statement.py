from odoo import models, fields, api

class account_bank_statement(models.Model):
    _inherit = 'account.bank.statement'
    settlement_ref = fields.Char(size=350, string='Amazon Settlement Ref')

#    @api.multi 
    def button_cancel(self):
        statement_obj=self.env['settlement.report.ept']
        statements=statement_obj.search([('statement_id','in',self.ids)])
        statements and statements.write({'state':'processed'})
        return super(account_bank_statement,self).button_cancel()
#    @api.multi
    def button_draft(self):
        statements=self.env['settlement.report.ept'].search([('statement_id','in',self.ids)])
        statements and statements.write({'state':'processed'})
        return super(account_bank_statement,self).button_draft()
#    @api.multi
    def button_confirm_bank(self):
        statement_obj=self.env['settlement.report.ept']
        statements=statement_obj.search([('statement_id','in',self.ids)])
        statements and statements.write({'state':'closed'})
        return super(account_bank_statement,self).button_confirm_bank()

class amazon_bank_statement_line(models.Model):
    _inherit="account.bank.statement.line"
    
    amazon_code=fields.Char("Amazon Code")
    is_refund_line=fields.Boolean("Is Refund Line ?",default=False,copy=False)
    amazon_order_ids=fields.Many2many("sale.order","statement_order_rel","line_id","order_id")
    return_picking_ids=fields.Many2many("stock.picking","statement_picking_ref","line_id","picking_id")
    refund_invoice_id=fields.Many2one('account.move',string="Invoice")
    refund_invoice_ids=fields.Many2many('account.move','statement_refund_invoice_ref','line_id','invoice_id')

    def _prepare_reconciliation_move(self, move_ref):
        result=super(amazon_bank_statement_line,self)._prepare_reconciliation_move(move_ref)
        settlement = self.env['settlement.report.ept'].search([('statement_id','=',self.statement_id.id)])
        if settlement:
            result.update({'seller_id':settlement.seller_id and settlement.seller_id.id or False,
                           'global_channel_id':settlement.seller_id and settlement.seller_id.global_channel_id and settlement.seller_id.global_channel_id.id or False,
                           'amazon_instance_id':settlement.instance_id and settlement.instance_id.id or False})
        return result
        
    def _prepare_reconciliation_move_line(self,move, st_line_amount):
        result=super(amazon_bank_statement_line,self)._prepare_reconciliation_move_line(move,st_line_amount)
        settlement = self.env['settlement.report.ept'].search([('statement_id','=',self.statement_id.id)])
        if settlement:
            result.update({'seller_id':settlement.seller_id and settlement.seller_id.id or False,
                           'global_channel_id':settlement.seller_id and settlement.seller_id.global_channel_id and settlement.seller_id.global_channel_id.id or False,
                           'amazon_instance_id':settlement.instance_id and settlement.instance_id.id or False})
        return result
        
