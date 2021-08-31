# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)
from odoo import api, fields, models


class LancerProduct(models.Model):
    _name = 'lancer.product'
    _rec_name = 'name'
    _order = "product_code, id"
    _description = '產品'

    name = fields.Char(string='產品名稱', translate=True)
    product_code = fields.Char(string='產品品號')
    product_image = fields.Binary(string="產品圖片", attachment=True)
    product_series_id = fields.Many2one(comodel_name="lancer.routing.series", string="產品系列", required=False, )
    product_category_id = fields.Many2one(comodel_name="lancer.product.category", string="產品分類", required=False, )
    active = fields.Boolean(default=True, string='是否啟用')
    product_desc = fields.Text(string='產品描述', translate=True)

    product_line = fields.One2many('lancer.product.line', 'product_id')

    # 0613 调整產品模式，按需填入 後續帶入報價單
    # product_series_id = fields.Many2one(comodel_name="lancer.routing.series", string="產品系列", required=False, )
    # product_category_id = fields.Many2one(comodel_name="lancer.product.category", string="產品分類", required=False, )
    # product_id = fields.Many2one(comodel_name="lancer.product", string="產品名稱")
    handle_material_id = fields.Many2one(comodel_name="lancer.handle.attrs.record", string="手柄材質", required=False, )
    metal_spec_id = fields.Many2one(comodel_name="lancer.metal.spec", string="鋼刃材質", required=False, )
    routing_shape_id = fields.Many2one(comodel_name="lancer.routing.shape", string="鋼刃形狀", required=False, )
    routing_coating_id = fields.Many2one(comodel_name="lancer.routing.coating", string="鋼刃鍍層", required=False, )
    product_package_1 = fields.Many2one(string="包裝", comodel_name="lancer.product.package", required=False, )

    product_quote_lines = fields.One2many(comodel_name="lancer.product.quote.line", inverse_name="product_quote_id",
                                          string="自製明細")
    product_package_lines = fields.One2many(comodel_name="lancer.product.quote.package",
                                            inverse_name="product_quote_id",
                                            string="包裝明細")

    packing_inbox = fields.Integer(string='內盒', required=False)
    packing_outbox = fields.Integer(string='外箱', required=False)
    packing_net_weight = fields.Float(string='淨重', required=False)
    packing_gross_weight = fields.Float(string='毛重', required=False)
    packing_bulk = fields.Float(string='材積', required=False)

    @api.onchange('product_series_id')
    def onchange_product_series_id(self):
        if not self.product_series_id:
            return
        main_record = self.env['lancer.main'].search([('product_series_id', '=', self.product_series_id.id)])
        self.write({'product_quote_lines': [(5, 0, 0)]})
        if main_record:
            new_lines = []
            for line in main_record:
                vals = {
                    'main_id': line.id,
                }
                new_lines.append((0, 0, vals))
            self.product_quote_lines = new_lines

    @api.onchange('product_category_id')
    def onchange_product_category_id(self):
        if not self.product_category_id:
            return
        main_record = self.env['lancer.main'].search([('product_series_id', '=', self.product_series_id.id),
                                                      ('product_category_id', '=', self.product_category_id.id)])
        self.write({'product_quote_lines': [(5, 0, 0)]})
        if main_record:
            new_lines = []
            for line in main_record:
                vals = {
                    'main_id': line.id,
                }
                new_lines.append((0, 0, vals))
            self.product_quote_lines = new_lines

        # 依報價明細，決定手柄下拉內容
        list = []
        result = {}
        for line in self.product_quote_lines:
            for main_item in line.main_id.order_line:
                list.append(main_item.handle_attrs_record.id)
        result['domain'] = {'handle_material_id': [('id', 'in', list)]}
        return result

    @api.onchange('handle_material_id')
    def onchange_handle_material_id(self):
        if not self.handle_material_id:
            return

        #self.write({'product_quote_lines': [(2, line.id, 0) for line in self.mapped('product_quote_lines')]})

        for line in self.product_quote_lines :
            delete_id = True
            for main_item in line.main_id.order_line:
                if main_item.handle_attrs_record.id == self.handle_material_id.id:
                    delete_id = False
            if delete_id == True :
                self.write({'product_quote_lines': [(2, line.id, 0)]})


        # 尋找手抦成本
        for line in self.product_quote_lines:
            line.subcontract_cost = 0
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
            line.total_cost = line.assembly_cost+line.metal_cost+line.handle_cost+line.subcontract_cost

        # 依報價明細，決定	鋼刃材質下拉內容
        list1 = []
        list2 = []
        list3 = []
        result = {}
        for line in self.product_quote_lines:
            for main_item in line.main_id.order_line:
                list1.append(main_item.main_item_id.metal_spec_id.id)
                list2.append(main_item.main_item_id.metal_shape_id.id)
                list3.append(main_item.main_item_id.metal_coating_id.id)
        result['domain'] = {'metal_spec_id': [('id', 'in', list1)], 'routing_shape_id': [('id', 'in', list2)],
                            'routing_coating_id': [('id', 'in', list3)]}
        return result

    @api.onchange('product_quote_lines')
    def onchange_product_quote_lines(self):
        total_packing_inbox = 0
        total_packing_outbox = 0
        total_packing_net_weight = 0
        total_packing_gross_weight = 0
        total_packing_bulk = 0
        for line in self.product_quote_lines:
            line.total_cost = line.assembly_cost + line.metal_cost + line.handle_cost + line.subcontract_cost
            total_packing_inbox += line.packing_inbox
            total_packing_outbox += line.packing_outbox
            total_packing_net_weight += line.packing_net_weight
            total_packing_gross_weight += line.packing_gross_weight
            total_packing_bulk += line.packing_bulk

        self.packing_inbox = total_packing_inbox
        self.packing_outbox = total_packing_outbox
        self.packing_net_weight = total_packing_net_weight
        self.packing_gross_weight = total_packing_gross_weight
        self.packing_bulk = total_packing_bulk

class LancerProductLine(models.Model):
    _name = 'lancer.product.line'
    _order = 'id'
    _description = '產品主件明細'

    product_id = fields.Many2one('lancer.product', string='產品參考', index=True, required=True, readonly=True,
                                 ondelete="cascade", copy=False)
    sequence = fields.Integer(string='Sequence', default=10)
    main_id = fields.Many2one('lancer.main', string='主件', index=True, ondelete="cascade", )
    material_cost = fields.Float(string='料', related='main_id.main_material_cost', store=True)
    process_cost = fields.Float(string='工', related='main_id.main_process_cost', store=True)
    manufacture_cost = fields.Float(string='費', related='main_id.main_manufacture_cost', store=True)
    total_cost = fields.Float(string='總價', related='main_id.main_total_cost', store=True)


class LancerProductQuoteLine(models.Model):
    _name = 'lancer.product.quote.line'
    _order = "sequence, id"
    _description = '產品預設報價使用-自製'

    product_quote_id = fields.Many2one(comodel_name="lancer.product", string="產品", required=True, ondelete='cascade')
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
    # total_cost = fields.Float(string="總成本", required=False, compute='_compute_total_cost', store=True)
    total_cost = fields.Float(string="總成本", required=False, store=True)
    # total_amount = fields.Float(string="台幣", required=False)
    # total_amount_usd = fields.Float(string="美金", required=False)
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


class LancerProductQuotePackage(models.Model):
    _name = 'lancer.product.quote.package'
    _rec_name = 'name'
    _order = "name"
    _description = '產品預設報價使用-包裝'

    product_quote_id = fields.Many2one(comodel_name="lancer.product", string="產品", required=True, ondelete='cascade')
    package_type_id = fields.Many2one(comodel_name="lancer.package.type", string="包裝分類", required=False, )
    package_setting_id = fields.Many2one(comodel_name="lancer.package.setting", string="包裝料件", required=False, )
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
