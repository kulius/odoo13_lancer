# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import api, fields, models, _


class LancerQuote(models.Model):
    _name = 'lancer.quote'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = "name"
    _description = '報價單'

    state = fields.Selection([
        ('draft', '草稿'),
        ('sent', '己送出'),
        ('done', '完成'),
        ('cancel', '取消')
    ], string='Status', index=True, copy=False, default='draft', tracking=True)

    name = fields.Char(string='報價單編碼', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    version = fields.Char(string='版次')
    active = fields.Boolean(default=True, string='是否啟用')
    user_id = fields.Many2one('res.users', string='報價者', default=lambda self: self.env.user)
    partner_id = fields.Many2one(comodel_name="res.partner", string="客戶", required=True, )
    contact_id = fields.Many2one('res.partner', '連絡人', domain="[('parent_id','=',partner_id)]" )
    product_series_id = fields.Many2one(comodel_name="lancer.product.series", string="產品系列", required=False, )
    product_category_id = fields.Many2one(comodel_name="lancer.product.category", string="產品分類", required=False, )
    product_id = fields.Many2one(comodel_name="lancer.product", string="產品名稱", required=True, )
    handle_material_id = fields.Many2one(comodel_name="lancer.handlematerial.material", string="手柄材質", required=False, )
    metal_spec_id = fields.Many2one(comodel_name="lancer.metal.spec", string="鋼刃材質", required=False, )
    routing_shape_id = fields.Many2one(comodel_name="lancer.routing.shape", string="鋼刃形狀", required=False, )
    routing_coating_id = fields.Many2one(comodel_name="lancer.routing.coating", string="鋼刃鍍層", required=False, )
    product_package = fields.Selection(string="包裝", selection=[('BULK', 'BULK'), ('加吊牌', '加吊牌'), ], required=False, )

    quote_date = fields.Date(string="報價日期", required=True, )

    main_count = fields.Integer(string="自製組件數", required=False, )
    subcontract_count = fields.Integer(string="外購品項數", required=False, )
    routing_amount = fields.Integer(string="自製金額", required=False, )
    subcontract_amount = fields.Integer(string="外購金額", required=False, )
    package_amount = fields.Integer(string="包裝金額", required=False, )

    payment_term_id = fields.Many2one(comodel_name="payment.term", string="付款條件", required=False, )
    moq = fields.Integer(string="MOQ", required=False, )
    shipping_term_id = fields.Many2one(comodel_name="lancer.shipping.term", string="貿易條件", required=False, )
    delivery_before = fields.Integer(string="交貨前置時間", required=False, )
    quote_validdate = fields.Date(string="報價有效期", required=False, )
    mov = fields.Integer(string="MOV", required=False, )

    certification_amount = fields.Float(string="認證費用", required=False, )
    customs_rate = fields.Float(string="報關費率", required=False, )
    exchange_rate = fields.Float(string="匯率", required=False, )
    test_amount = fields.Float(string="測試費用", required=False, )
    certificate_amount = fields.Float(string="證書費用", required=False, )

    packing_inbox = fields.Integer(string='內盒', required=False)
    packing_outbox = fields.Integer(string='外箱', required=False)
    packing_net_weight = fields.Float(string='淨重', required=False)
    packing_gross_weight = fields.Float(string='毛重', required=False)
    packing_bulk = fields.Float(string='材積', required=False)
    quote_memo = fields.Text(string='報價說明', required=False)
    quote_image = fields.Binary(string="報價單圖片", related="product_id.product_image", readonly=True)

    quote_lines = fields.One2many(comodel_name="lancer.quote.line", inverse_name="quote_id", string="自製明細")
    subcontract_ids = fields.One2many(comodel_name="lancer.quote.subcontract", inverse_name="quote_id", string="外購明細")
    package_ids = fields.One2many(comodel_name="lancer.quote.package", inverse_name="quote_id", string="包裝明細")
    expense_ids = fields.One2many(comodel_name="lancer.quote.expense", inverse_name="quote_id", string="其餘費用明細")

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('lancer.quote') or _('New')

        result = super(LancerQuote, self).create(vals)
        return result

    @api.onchange('product_series_id')
    def onchange_product_series_id(self):
        if not self.product_series_id:
            return
        main_record = self.env['lancer.main'].search([('product_series_id', '=', self.product_series_id.id)])
        # if not self.product_category_id:
        #
        # else:
        # main_record = self.env['lancer.main'].search([('product_series_id', '=', self.product_series_id.id),
        #                                                   ('product_category_id', '=', self.product_category_id.id)])
        if main_record:
            self.write({'quote_lines': [(5, 0, 0)]})
            new_lines = []
            for line in main_record:
                vals = {
                    'main_id': line.id,
                }
                new_lines.append((0, 0, vals))
            self.quote_lines = new_lines


    @api.onchange('product_category_id')
    def onchange_product_category_id(self):
        if not self.product_category_id:
            return
        main_record = self.env['lancer.main'].search([('product_series_id', '=', self.product_series_id.id),
                                                          ('product_category_id', '=', self.product_category_id.id)])
        if main_record:
            self.write({'quote_lines': [(5, 0, 0)]})
            new_lines = []
            for line in main_record:
                vals = {
                    'main_id': line.id,
                }
                new_lines.append((0, 0, vals))
            self.quote_lines = new_lines

class LancerQuoteLine(models.Model):
    _name = 'lancer.quote.line'
    _order = "sequence, id"
    _description = '報價單-自製'

    quote_id = fields.Many2one(comodel_name="lancer.quote", string="報價單", required=True, ondelete='cascade')
    main_id = fields.Many2one(comodel_name='lancer.main', string='主件品名')
    routing_cutting_id = fields.Many2one(comodel_name='lancer.routing.cutting', string='刃口')
    routing_outer_id = fields.Many2one(comodel_name="lancer.routing.outer", string="外徑", required=False, )
    exposed_long_id = fields.Many2one('lancer.metal.exposed.long', string="長度", required=False, )

    main_category_id = fields.Many2one(comodel_name="lancer.main.category", string="主件分類", required=False, )
    sequence = fields.Integer(string='項次', required=True, default=10)
    material_amount = fields.Float(related='main_id.main_material_cost', string="料", required=False, )
    work_amount = fields.Float(related='main_id.main_process_cost', string="工", required=False, )
    factory_amount = fields.Float(related='main_id.main_manufacture_cost', string="費", required=False, )
    total_amount = fields.Float(string="台幣", required=False, )
    total_amount_usd = fields.Float(string="美金", required=False, )
    quote_attrs_ids = fields.Many2many('lancer.attr.records', string='主件特徵值')
    packing_inbox = fields.Integer(string='內盒', required=False)
    packing_outbox = fields.Integer(string='外箱', required=False)
    packing_net_weight = fields.Float(string='淨重', required=False)
    packing_gross_weight = fields.Float(string='毛重', required=False)
    packing_bulk = fields.Float(string='材積', required=False)

    # @api.onchange('main_id')
    # def set_attrs_data(self):
    #     if not self.main_id:
    #         return
    #     if self.main_id:
    #         self.quote_attrs_ids = self.main_id.main_attrs_ids



class LancerQuoteSubcontract(models.Model):
    _name = 'lancer.quote.subcontract'
    _rec_name = 'name'
    _order = "name"
    _description = '報價單-外購'

    quote_id = fields.Many2one(comodel_name="lancer.quote", string="報價單", required=True, ondelete='cascade')
    sequence = fields.Integer(string='項次', required=True, default=10)
    partner_id = fields.Many2one(comodel_name="res.partner", string="廠商", required=False, )
    subcontract_category_id = fields.Many2one(comodel_name="lancer.subcontract.category", string="品項大類",
                                              required=False, )
    name = fields.Char(string="品名規格", required=False, )
    partno = fields.Char(string="參考料號", required=False, )
    material_id = fields.Many2one(comodel_name="lancer.subcontract.material", string="材質", required=False, )
    treatment_id = fields.Many2one(comodel_name="lancer.subcontract.treatment", string="表面處理", required=False, )
    handle_amount = fields.Float(string="柄價", required=False, )
    subcontract_amount = fields.Float(string="單價", required=False, )
    build_amount = fields.Float(string="組工", required=False, )
    cost_amount = fields.Float(string="成本", required=False, )
    mould_amount = fields.Float(string="模具費用", required=False, )
    manage_rate = fields.Float(string="管銷百分比", required=False, )
    profit_rate = fields.Float(string="利潤百分比", required=False, )


class LancerQuotePackage(models.Model):
    _name = 'lancer.quote.package'
    _rec_name = 'name'
    _order = "name"
    _description = '報價單-包裝'

    quote_id = fields.Many2one(comodel_name="lancer.quote", string="報價單", required=True, ondelete='cascade')
    package_type_id = fields.Many2one(comodel_name="lancer.package.type", string="包裝分類", required=False, )
    package_setting_id = fields.Many2one(comodel_name="lancer.package.setting", string="包裝料件", required=True, )
    name = fields.Char(string='說明')
    quant = fields.Float(string="數量", required=False, )
    amount = fields.Float(string="價格", required=False, )
    mould_amount = fields.Float(string="模具/版費", required=False, )

    @api.onchange('package_type_id')
    def onchange_package_type_id(self):
        if not self.package_type_id:
            return
        package_setting = self.env['lancer.package.setting'].search([('package_type_id', '=', self.package_type_id.id)])
        list = []
        result = {}
        for line in package_setting:
            list.append(line.id)
        result['domain'] = {'package_setting_id': [('id', 'in', list)]}
        return result

class LancerQuotExpense(models.Model):
    _name = 'lancer.quote.expense'
    _rec_name = 'name'
    _order = "name"
    _description = '報價單-其餘費用'

    quote_id = fields.Many2one(comodel_name="lancer.quote", string="報價單", required=True, ondelete='cascade')
    package_expense_id = fields.Many2one(comodel_name="lancer.package.expense", string="其餘費用項目", required=True, )
    name = fields.Char(string='說明')
    quant = fields.Float(string="數量", required=False, )
    amount = fields.Float(string="價格", required=False, )
