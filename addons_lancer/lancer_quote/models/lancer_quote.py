# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import api, fields, models, _
import datetime
from dateutil.relativedelta import relativedelta


class LancerQuote(models.Model):
    _name = 'lancer.quote'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = "name"
    _description = '報價單'

    def _get_quote_exchange_rate(self):
        return self.env['ir.config_parameter'].sudo().get_param('lancer_quote_exchange_rate')

    def _get_quote_manage_rate(self):
        return self.env['ir.config_parameter'].sudo().get_param('lancer_quote_manage_rate')

    def _get_quote_profit_rate(self):
        return self.env['ir.config_parameter'].sudo().get_param('lancer_quote_profit_rate')

    def _get_quote_charge_rate(self):
        return self.env['ir.config_parameter'].sudo().get_param('lancer_quote_charge_rate')

    @api.depends('quote_lines.total_cost')
    def _amount_all(self):
        for order in self:
            routing_amount = 0.0
            for line in order.quote_lines:
                routing_amount += line.total_cost
            order.update({
                'routing_amount': routing_amount,
            })

    @api.depends('subcontract_ids.quote_subcontract_amount')
    def _subcontract_amount_all(self):
        for order in self:
            quote_subcontract_amount = 0.0
            for line in order.subcontract_ids:
                quote_subcontract_amount += line.quote_subcontract_amount
            order.update({
                'subcontract_amount': quote_subcontract_amount,
            })

    @api.depends('package_ids.amount')
    def _package_amount_all(self):
        for order in self:
            package_amount = 0.0
            for line in order.package_ids:
                package_amount += line.mould_amount
            order.update({
                'package_amount': package_amount,
            })

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
    partner_id = fields.Many2one(comodel_name="res.partner", string="客戶")
    contact_id = fields.Many2one('res.partner', '客戶業務', domain="[('parent_id','=',partner_id)]")
    product_series_id = fields.Many2one(comodel_name="lancer.routing.series", string="產品系列", required=False, )
    product_category_id = fields.Many2one(comodel_name="lancer.product.category", string="產品分類", required=False, )
    product_id = fields.Many2one(comodel_name="lancer.product", string="產品名稱")
    quote_currency = fields.Selection([
        ('NT$', 'NT$'),
        ('US$', 'US$')
    ], string='報價單幣別', copy=False, default='NT$', tracking=True)

    # handle_material_id = fields.Many2one(comodel_name="lancer.handlematerial.material", string="手柄材質", required=False, )
    handle_material_id = fields.Many2one(comodel_name="lancer.handle.attrs.record", string="手柄材質", required=False, )
    metal_spec_id = fields.Many2one(comodel_name="lancer.metal.spec", string="鋼刃材質", required=False, )
    routing_shape_id = fields.Many2one(comodel_name="lancer.routing.shape", string="鋼刃形狀", required=False, )
    routing_coating_id = fields.Many2one(comodel_name="lancer.routing.coating", string="鋼刃鍍層", required=False, )
    # product_package = fields.Selection(string="包裝", selection=[('BULK', 'BULK'), ('加吊牌', '加吊牌'), ], required=False, )
    product_package = fields.Many2one(string="包裝", comodel_name="lancer.product.package", required=False, )

    quote_date = fields.Date(string="報價日期", required=True, default=fields.Date.context_today)


    main_count = fields.Integer(string="自製組件數", required=False, )
    subcontract_count = fields.Integer(string="外購品項數", required=False, )
    routing_amount = fields.Float(string="自製金額", store=True, readonly=True, compute='_amount_all', )
    subcontract_amount = fields.Float(string="外購金額", store=True, readonly=True, compute='_subcontract_amount_all', )
    package_amount = fields.Float(string="包裝金額", store=True, readonly=True, compute='_package_amount_all', )

    payment_term_id = fields.Many2one(comodel_name="lancer.payment.term", string="付款條件", required=False, )
    moq = fields.Integer(string="MOQ", required=False, )
    shipping_term_id = fields.Many2one(comodel_name="lancer.incoterms", string="貿易條件", required=False, )
    delivery_id = fields.Many2one(comodel_name="lancer.delivery", string="交貨條件", required=False, )
    quote_validdate = fields.Date(string="報價有效期", required=False, default= datetime.datetime.now() + relativedelta(months=+3))
    mov = fields.Integer(string="MOV", required=False, )
    mov_add = fields.Integer(string="MOV附加費用", required=False, )
    delivery_before = fields.Integer(string="交貨前置時間", required=False, )

    certification_amount = fields.Float(string="認證費用", required=False, )
    customs_rate = fields.Float(string="報關費率", required=False, )
    exchange_rate = fields.Float(string="匯率", required=False, default=_get_quote_exchange_rate)
    test_amount = fields.Float(string="測試費用", required=False, )
    certificate_amount = fields.Float(string="證書費用", required=False, )
    manage_rate = fields.Float(string="管銷百分比", required=False, default=_get_quote_manage_rate)
    profit_rate = fields.Float(string="利潤百分比", required=False, default=_get_quote_profit_rate)
    charge_rate = fields.Float(string="手續百分比", required=False, default=_get_quote_charge_rate)

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

    @api.onchange('contact_id')
    def onchange_contact_id(self):
        if self.contact_id:
            self.contact_id.partner_id = self.partner_id.id

    @api.onchange('product_id')
    def onchange_product_id(self):
        if not self.product_id:
            return
        product_record = self.env['lancer.product'].search([('id', '=', self.product_id.id)])
        if product_record:
            new_lines = []
            self.product_series_id = product_record.product_series_id.id
            self.product_category_id = product_record.product_category_id.id
            self.handle_material_id = product_record.handle_material_id.id
            self.metal_spec_id = product_record.metal_spec_id.id
            self.routing_shape_id = product_record.routing_shape_id.id
            self.routing_coating_id = product_record.routing_coating_id.id
            self.product_package_1 = product_record.product_package_1.id
            self.packing_inbox = product_record.packing_inbox
            self.packing_outbox = product_record.packing_outbox
            self.packing_net_weight = product_record.packing_net_weight
            self.packing_gross_weight = product_record.packing_gross_weight
            self.packing_bulk = product_record.packing_bulk
            self.write({'quote_lines': [(5, 0, 0)]})
            if product_record.product_quote_lines:
                for line in product_record.product_quote_lines:
                    vals = {
                        'main_id': line.main_id.id,
                        'routing_cutting_id': line.routing_cutting_id.id,
                        'routing_outer_id': line.routing_outer_id.id,
                        'exposed_long_id': line.exposed_long_id.id,
                        'main_category_id': line.main_category_id.id,
                        'metal_cost': line.metal_cost,
                        'handle_cost': line.handle_cost,
                        'assembly_cost': line.assembly_cost,
                        'subcontract_cost': line.subcontract_cost,
                        'total_cost': line.total_cost,
                        'packing_inbox': line.packing_inbox,
                        'packing_outbox': line.packing_outbox,
                        'packing_net_weight': line.packing_net_weight,
                        'packing_gross_weight': line.packing_gross_weight,
                        'packing_bulk': line.packing_bulk,
                    }
                    new_lines.append((0, 0, vals))
            self.quote_lines = new_lines
            new_lines = []
            self.write({'package_ids': [(5, 0, 0)]})
            if product_record.product_package_lines:
                for line in product_record.product_package_lines:
                    vals = {
                        'package_type_id': line.package_type_id.id,
                        'package_setting_id': line.package_setting_id.id,
                        'name': line.name,
                        'quant': line.quant,
                        'amount': line.amount,
                        'mould_amount': line.mould_amount,
                    }
                    new_lines.append((0, 0, vals))
            self.package_ids = new_lines

    #產品系列下拉
    @api.onchange('product_series_id')
    def onchange_product_series_id(self):
        if not self.product_series_id:
            return
        main_record = self.env['lancer.main'].search([('product_series_id', '=', self.product_series_id.id)])
        self.write({'quote_lines': [(5, 0, 0)]})
        if main_record:
            new_lines = []
            for line in main_record:
                vals = {
                    'main_id': line.id,
                }
                new_lines.append((0, 0, vals))
            self.quote_lines = new_lines
    # 產品分類下拉
    @api.onchange('product_category_id')
    def onchange_product_category_id(self):
        if not self.product_category_id:
            return
        main_record = self.env['lancer.main'].search([('product_series_id', '=', self.product_series_id.id),
                                                      ('product_category_id', '=', self.product_category_id.id)])
        self.write({'quote_lines': [(5, 0, 0)]})
        if main_record:
            new_lines = []
            for line in main_record:
                vals = {
                    'main_id': line.id,
                }
                new_lines.append((0, 0, vals))
            self.quote_lines = new_lines

        product_record = self.env['lancer.product'].search([('product_series_id', '=', self.product_series_id.id),
                                                      ('product_category_id', '=', self.product_category_id.id)])
        productlist = []
        for line in product_record:
            productlist.append(line.id)


        # 依報價明細，決定手柄下拉內容
        list = []
        result = {}
        for line in self.quote_lines:
            for main_item in line.main_id.order_line:
                list.append(main_item.handle_attrs_record.id)
        result['domain'] = {'handle_material_id': [('id', 'in', list)], 'product_id': [('id', 'in', productlist)]}
        return result

    @api.onchange('handle_material_id')
    def onchange_handle_material_id(self):
        if not self.handle_material_id:
            return
        # 尋找手抦成本
        for line in self.quote_lines:
            line.subcontract_cost=0
            for main_item in line.main_id.order_line:
                if main_item.main_item_id.item_routing == 'assembly':
                    line.assembly_cost = main_item.item_total_cost
                if main_item.main_item_id.item_routing == 'metal':
                    line.routing_cutting_id = main_item.main_item_id.metal_cutting_id.id
                    line.routing_outer_id = main_item.main_item_id.metal_outer_id.id
                    line.exposed_long_id = main_item.main_item_id.metal_exposed_long_id.id
                    line.metal_cost = main_item.item_total_cost
                    line.packing_inbox = main_item.order_id.packing_inbox
                    line.packing_outbox = main_item.order_id.packing_outbox
                    line.packing_net_weight = main_item.order_id.packing_net_weight
                    line.packing_gross_weight = main_item.order_id.packing_gross_weight
                    line.packing_bulk = main_item.order_id.packing_bulk
                if main_item.handle_attrs_record.id == self.handle_material_id.id:
                    line.handle_cost = main_item.item_total_cost
                if main_item.main_item_id.item_routing == 'subcontract':
                    line.subcontract_cost += main_item.item_total_cost

        # 依報價明細，決定	鋼刃材質下拉內容
        list1 = []
        list2 = []
        list3 = []
        result = {}
        for line in self.quote_lines:
            for main_item in line.main_id.order_line:
                list1.append(main_item.main_item_id.metal_spec_id.id)
                list2.append(main_item.main_item_id.metal_shape_id.id)
                list3.append(main_item.main_item_id.metal_coating_id.id)
        result['domain'] = {'metal_spec_id': [('id', 'in', list1)], 'routing_shape_id': [('id', 'in', list2)],
                            'routing_coating_id': [('id', 'in', list3)]}
        return result


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

    metal_cost = fields.Float(string="鋼刃成本", required=False, )
    handle_cost = fields.Float(string="手柄成本", required=False, )
    assembly_cost = fields.Float(string="組立成本", required=False, )
    subcontract_cost = fields.Float(string="外購成本", required=False, )
    total_cost = fields.Float(string="總成本", required=False, compute='_compute_total_cost', store=True)

    total_amount = fields.Float(string="台幣", required=False, size=16, digits=(11, 3))
    total_amount_usd = fields.Float(string="美金", required=False, size=16, digits=(11, 3))
    total_gross = fields.Float(string="毛利率", required=False, size=16, digits=(11, 3), compute='_compute_total_gross', store=True)
    quote_attrs_ids = fields.Many2many('lancer.attr.records', string='主件特徵值')
    packing_inbox = fields.Integer(string='內盒', required=False)
    packing_outbox = fields.Integer(string='外箱', required=False)
    packing_net_weight = fields.Float(string='淨重', required=False)
    packing_gross_weight = fields.Float(string='毛重', required=False)
    packing_bulk = fields.Float(string='材積', required=False)
    cutting_ids = fields.Many2many('lancer.routing.cutting', string='刃口', compute='_compute_attrs_ids', store=True)
    outer_ids = fields.Many2many("lancer.routing.outer", string="外徑", compute='_compute_attrs_ids', store=True)
    exposed_long_ids = fields.Many2many('lancer.metal.exposed.long', string="長度", compute='_compute_attrs_ids',
                                        store=True)

    # 依主件，決定下拉值內容
    @api.depends('main_id')
    def _compute_attrs_ids(self):
        attrs_ids1 = []
        attrs_ids2 = []
        attrs_ids3 = []
        for line in self.main_id.order_line:
            if line.main_item_id.metal_cutting_id.id:
                attrs_ids1.append(line.main_item_id.metal_cutting_id.id)
            if line.main_item_id.metal_outer_id.id:
                attrs_ids2.append(line.main_item_id.metal_outer_id.id)
            if line.main_item_id.metal_exposed_long_id.id:
                attrs_ids3.append(line.main_item_id.metal_exposed_long_id.id)
        self.update({'cutting_ids': [(6, 0, attrs_ids1)]})
        self.update({'outer_ids': [(6, 0, attrs_ids2)]})
        self.update({'exposed_long_ids': [(6, 0, attrs_ids3)]})

    @api.depends('metal_cost', 'handle_cost', 'assembly_cost', )
    def _compute_total_cost(self):
        for record in self:
            # 總成本=手柄成本+金屬成本+組立成本
            record.total_cost = record.metal_cost + record.handle_cost + record.assembly_cost + record.subcontract_cost
            if record.total_cost > 0:
                # 台幣報價=總成本/1-管銷/1-利潤
                record.total_amount = record.total_cost / (1 - record.quote_id.manage_rate) / (
                        1 - record.quote_id.profit_rate)
                # 美金報價=台幣報價/手續費/匯率
                record.total_amount_usd = record.total_amount / record.quote_id.charge_rate / record.quote_id.exchange_rate

    @api.depends('total_amount', 'total_cost', 'total_amount', )
    def _compute_total_gross(self):
        for record in self:
            if record.total_amount != 0:
                record.total_gross = (record.total_amount - record.total_cost) / record.total_amount
            else:
                record.total_gross = 0

    @api.onchange('routing_cutting_id', 'routing_outer_id', 'exposed_long_id')
    def get_item_total_cost(self):
        for line in self.main_id.order_line:
            if line.main_item_id.metal_cutting_id.id == self.routing_cutting_id.id and line.main_item_id.metal_outer_id.id == self.routing_outer_id.id and line.main_item_id.metal_exposed_long_id.id == self.exposed_long_id.id:
                self.metal_cost = line.item_total_cost

    # @api.onchange('main_id', 'handle_cost')
    # def set_attrs_data(self):
    #     list1 = []
    #     list2 = []
    #     list3 = []
    #     result = {}
    #     for line in self.main_id.order_line:
    #         list1.append(line.main_item_id.metal_cutting_id.id)
    #         list2.append(line.main_item_id.metal_outer_id.id)
    #         list3.append(line.main_item_id.metal_exposed_long_id.id)
    #     result['domain'] = {'routing_cutting_id': [('id', 'in', list1)], 'routing_outer_id': [('id', 'in', list2)], 'exposed_long_id': [('id', 'in', list3)]}
    #     return result


class LancerQuoteSubcontract(models.Model):
    _name = 'lancer.quote.subcontract'
    _rec_name = 'name'
    _order = "name"
    _description = '報價單-外購'

    def _get_quote_manage_rate(self):
        return self.env['ir.config_parameter'].sudo().get_param('lancer_quote_manage_rate')

    def _get_quote_profit_rate(self):
        return self.env['ir.config_parameter'].sudo().get_param('lancer_quote_profit_rate')

    quote_id = fields.Many2one(comodel_name="lancer.quote", string="報價單", required=True, ondelete='cascade')
    sequence = fields.Integer(string='項次', required=True, default=10)
    partner_id = fields.Many2one(comodel_name="res.partner", string="廠商", required=False, )
    subcontract_category_id = fields.Many2one(comodel_name="lancer.subcontract.category", string="品名",
                                              required=False, )
    name = fields.Char(string="規格", required=False, )
    partno = fields.Char(string="參考料號", required=False, )
    material_id = fields.Many2one(comodel_name="lancer.subcontract.material", string="材質", required=False, )
    treatment_id = fields.Many2one(comodel_name="lancer.subcontract.treatment", string="表面處理", required=False, )
    handle_amount = fields.Float(string="柄價", required=False, )
    subcontract_amount = fields.Float(string="單價", required=False, )
    build_amount = fields.Float(string="組工", required=False, )
    cost_amount = fields.Float(string="成本", required=False, compute='_compute_cost_amount', store=True )
    mould_amount = fields.Float(string="模具費用", required=False, )
    manage_rate = fields.Float(string="管銷%", required=False, default=_get_quote_manage_rate)
    profit_rate = fields.Float(string="利潤%", required=False, default=_get_quote_profit_rate )
    quantity = fields.Float(string="數量", required=False, default= 1)
    quote_subcontract_amount = fields.Float(string="外購報價", required=False, compute='_compute_cost_amount', store=True )

    @api.onchange('subcontract_category_id')
    def get_subcontract(self):
        self.partner_id = self.subcontract_category_id.partner_id.id
        self.name = self.subcontract_category_id.spec
        self.partno = self.subcontract_category_id.partno
        self.material_id = self.subcontract_category_id.material_id.id
        self.treatment_id = self.subcontract_category_id.treatment_id.id
        self.handle_amount = self.subcontract_category_id.handle_amount
        self.subcontract_amount = self.subcontract_category_id.subcontract_amount
        self.build_amount = self.subcontract_category_id.build_amount
        self.cost_amount = self.subcontract_category_id.cost_amount
        self.mould_amount = self.subcontract_category_id.mould_amount
        self._compute_cost_amount()

    @api.depends('handle_amount', 'build_amount', 'quantity', 'manage_rate', 'profit_rate')
    def _compute_cost_amount(self):
        #柄價＋單價+組工＝成本 成本*數量/(100%-管銷)/(100%-利潤)＝報價
        for data in self:
            data.cost_amount = data.handle_amount + data.subcontract_amount + data.build_amount
            data.quote_subcontract_amount = (data.cost_amount * data.quantity) / (1 - data.manage_rate) / (
                        1 - data.profit_rate)





class LancerQuotePackage(models.Model):
    _name = 'lancer.quote.package'
    _rec_name = 'name'
    _order = "name"
    _description = '報價單-包裝'

    quote_id = fields.Many2one(comodel_name="lancer.quote", string="報價單", required=True, ondelete='cascade')
    package_type_id = fields.Many2one(comodel_name="lancer.package.type", string="包裝分類", required=False, )
    package_setting_id = fields.Many2one(comodel_name="lancer.package.setting", string="包裝料件", required=False, )
    name = fields.Char(string='說明')
    quant = fields.Float(string="數量", required=False, )
    amount = fields.Float(string="價格", required=False, )
    mould_amount = fields.Float(string="模具/版費", required=False, compute='_compute_amount', store=True )

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

    @api.onchange('package_setting_id')
    def onchange_package_setting_id(self):
        if self.package_setting_id:
            self.amount = self.package_setting_id.price

    @api.depends('quant', 'amount')
    def _compute_amount(self):
        for record in self :
            record.mould_amount = record.quant * record.amount

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
