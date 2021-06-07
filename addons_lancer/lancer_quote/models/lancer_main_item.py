# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError



class LancerMainItem(models.Model):
    _name = 'lancer.main.item'
    _rec_name = 'name'
    _order = "name, id"
    _description = '品項'

    def _get_metal_work_labor(self):
        return self.env['ir.config_parameter'].sudo().get_param('lancer_metal_work_labor')

    def _get_metal_work_make(self):
        return self.env['ir.config_parameter'].sudo().get_param('lancer_metal_work_make')

    def _get_metal_work_efficiency(self):
        return self.env['ir.config_parameter'].sudo().get_param('lancer_metal_work_efficiency')

    def _get_metal_work_yield(self):
        return self.env['ir.config_parameter'].sudo().get_param('lancer_metal_work_yield')

    def _get_handle_work_mould(self):
        return self.env['ir.config_parameter'].sudo().get_param('lancer_handle_work_mould')

    def _get_handle_work_make(self):
        return self.env['ir.config_parameter'].sudo().get_param('lancer_handle_work_make')

    def _get_handle_work_efficiency(self):
        return self.env['ir.config_parameter'].sudo().get_param('lancer_handle_work_efficiency')

    def _get_handle_work_yield(self):
        return self.env['ir.config_parameter'].sudo().get_param('lancer_handle_work_yield')

    @api.depends('material_cost', 'process_cost', 'manufacture_cost')
    def _amount_all(self):
        price = self.material_cost + self.process_cost + self.manufacture_cost
        self.update({'item_total_cost': price})

    @api.depends('handle_moldcost1', 'handle_moldcost2', 'handle_moldcost3', 'handle_moldcost4', 'handle_moldcost5',
                 'handle_moldcost6', 'handle_mandrel', 'handle_elecmandrel')
    def _handle_mold_total(self):
        price = self.handle_moldcost1 + self.handle_moldcost2 + self.handle_moldcost3 + self.handle_moldcost4 + self.handle_moldcost5 + self.handle_moldcost6 + self.handle_mandrel + self.handle_elecmandrel
        self.update({'handle_mold_total': price})

    # 手柄射出-總成本計算
    @api.depends('handle_materialcost_ids', 'handle_mold_total')
    def _handle_work_sum(self):
        sum1 = sum([l.material_cost + l.process_price for l in self.handle_materialcost_ids])
        # sum2 = sum([l.process_price for l in self.handle_processcost_ids])
        sumcost = (
                          sum1 + self.handle_work_make + self.handle_work_mould) / self.handle_work_efficiency / self.handle_work_yield
        # Math.Round(((txt_Matall.Text + txt_Proall.Text + txt_Cost03.Text + txt_Cost05.Text) / txt_Cost02.Text / txt_Cost04.Text), 3, MidpointRounding.AwayFromZero).ToString();
        self.update({'handle_work_sum': sumcost})
        if sum1 > 0:
            self.update({'manufacture_cost': sumcost})

    # 將品項明細中的特徵值集合呈現
    # @api.depends('handle_materialcost_ids.main_item_id')
    # def _compute_attrs_record(self):
    #     # self.main_attrs_metal_ids = [(5,)]
    #     # self.main_attrs_handle_ids = [(5,)]
    #     if self.item_routing == 'handle':
    #         attrs_ids = []
    #         for rec in self.handle_materialcost_ids:
    #             if rec.material:
    #                 attrs_ids.append(rec.material.id)
    #         self.update({'handle_attrs_ids': [(6, 0, attrs_ids)]})
    #     else:
    #         self.update({'handle_attrs_ids': None})
    @api.depends('handle_materialcost_ids.main_item_id')
    def _compute_attrs_record(self):
        # self.main_attrs_metal_ids = [(5,)]
        # self.main_attrs_handle_ids = [(5,)]
        handle_attrs = self.env['lancer.handle.attrs.record']
        if self.item_routing == 'handle':
            attrs_record = []
            for rec in self.handle_materialcost_ids:
                if rec.material:
                    attrs_record.append(rec.material.name)
                    # attrs_name += '+'.join(rec.material.name)
            attrs_name = '+'.join(str(d) for d in attrs_record)
            handle_record = handle_attrs.search([('name', '=', attrs_name)],limit=1)
            if not handle_record:
                handle_record.create({
                    'name': attrs_name,
                })
            self.update({'handle_attrs_id': handle_record.id})
        else:
            self.update({'handle_attrs_id': None})

    active = fields.Boolean(default=True, string='是否啟用')
    name = fields.Char(string='品項品名規格')
    main_item_category_id = fields.Many2one(comodel_name="lancer.main.item.category", string="品項分類", required=True, )

    item_routing = fields.Selection(string="加工製程段",
                                    selection=[('metal', '金屬加工'), ('handle', '手柄射出'), ('assembly', '組裝')],
                                    required=True, )
    material_cost = fields.Float(string='料')
    process_cost = fields.Float(string='工')
    manufacture_cost = fields.Float(string='費')
    item_total_cost = fields.Float(string='總價', store=True, readonly=True, compute='_amount_all')

    metal_blade = fields.Boolean(string="加工鋼刃", default=True)
    metal_shape_id = fields.Many2one(comodel_name="lancer.routing.shape", string="形狀", required=False, )
    metal_coating_id = fields.Many2one(comodel_name="lancer.routing.coating", string="鍍層", required=False, )
    metal_cutting_id = fields.Many2one(comodel_name="lancer.routing.cutting", string="刃口", required=False, )
    metal_outer_id = fields.Many2one(comodel_name="lancer.routing.outer", string="外徑", required=False, )
    metal_version_id = fields.Many2one(comodel_name="lancer.version.metal", string="版本版次", required=False, )

    metal_spec_id = fields.Many2one('lancer.metal.spec', string="鋼材種類", required=False, )
    metal_type_id = fields.Many2one('lancer.metal.type', string="鋼材規格", required=False, )
    metal_long = fields.Float(string="物料長(mm)", required=False, )
    metal_cutting_long_id = fields.Many2one('lancer.metal.cutting.long', string="下料長度(mm)", required=False, )
    metal_exposed_long_id = fields.Many2one('lancer.metal.exposed.long', string="外露長度(mm)", required=False, )

    metal_cut = fields.Float(string="切料節數", required=False, )
    metal_weight = fields.Float(string="鋼刃單隻重量", required=False, )
    metal_material = fields.Float(string="材料(元/KG)", required=False, )
    metal_price = fields.Float(string="單隻價格", required=False, )
    metal_count = fields.Float(string="支數(支/KG)", required=False, )

    metal_is_std_hour = fields.Boolean(string="依標工計算", )
    metal_item_processcost_ids = fields.One2many(comodel_name="lancer.main.item.processcost",
                                                 inverse_name="main_item_id", string="內製/委外加工成本", required=False, )

    metal_work_labor = fields.Float(string="人工成本", required=False, default=_get_metal_work_labor)
    metal_work_make = fields.Float(string="製造費", required=False, default=_get_metal_work_make)
    metal_work_efficiency = fields.Float(string="效率", required=False, default=_get_metal_work_efficiency)
    metal_work_yield = fields.Float(string="良率", required=False, default=_get_metal_work_yield)
    metal_work_plating = fields.Float(string="+電鍍", required=False, )
    metal_work_dye_blackhead = fields.Float(string="+染黑頭", required=False, )
    metal_work_spray_blackhead = fields.Float(string="+噴砂頭", required=False, )
    metal_work_sum1 = fields.Float(string="合計1", required=False, )
    metal_work_sum2 = fields.Float(string="合計2", required=False, )
    metal_work_sum3 = fields.Float(string="合計3", required=False, )

    # 手柄射出
    handle_series_id = fields.Many2one(comodel_name="lancer.routing.series", string="系列別", required=False, )
    handle_handle_id = fields.Many2one(comodel_name="lancer.routing.handle", string="手柄尺吋", required=False, )
    # handle_version_id = fields.Many2one(comodel_name="lancer.routing.version", string="版本版次", required=False, )
    handle_version_id = fields.Many2one(comodel_name="lancer.version.handle", string="版本版次", required=False, )
    # handle_attrs_ids = fields.Many2many('lancer.handlematerial.material', string='手柄材質特徵集合',
    #                                     compute='_compute_attrs_record')
    handle_attrs_id = fields.Many2one('lancer.handle.attrs.record', string='材質集合', compute='_compute_attrs_record')

    handle_materialcost_ids = fields.One2many(comodel_name="lancer.main.item.handlematerial",
                                              inverse_name="main_item_id", string="用料成本", required=False, )
    # handle_processcost_ids = fields.One2many(comodel_name="lancer.main.item.handleprocesscost",
    #                                          inverse_name="main_item_id", string="內製/委外加工成本", required=False, )

    handle_moldcost1 = fields.Float(string="第一層射出", required=False, defalut="0")
    handle_moldcost2 = fields.Float(string="第二層射出", required=False, defalut="0")
    handle_moldcost3 = fields.Float(string="第三層射出", required=False, defalut="0")
    handle_moldcost4 = fields.Float(string="第四層射出", required=False, defalut="0")
    handle_moldcost5 = fields.Float(string="第五層射出", required=False, defalut="0")
    handle_moldcost6 = fields.Float(string="第六層射出", required=False, defalut="0")
    handle_mandrel = fields.Float(string="芯軸", required=False, defalut="0")
    handle_elecmandrel = fields.Float(string="電工芯軸", required=False, defalut="0")
    handle_mold_total = fields.Float(string='總模具費用', store=True, readonly=True, compute='_handle_mold_total')

    handle_work_make = fields.Float(string="製造費", required=False, default=_get_handle_work_make)
    handle_work_mould = fields.Float(string="模具分攤", required=False, default=_get_handle_work_mould)
    handle_work_efficiency = fields.Float(string="效率", required=False, default=_get_handle_work_efficiency)
    handle_work_yield = fields.Float(string="良率", required=False, default=_get_handle_work_yield)
    handle_work_sum = fields.Float(string="總成本", required=False, store=True, readonly=True, compute='_handle_work_sum')
    # 包裝
    assembly_wage_ids = fields.One2many(comodel_name="lancer.main.item.assemblywage", inverse_name="main_item_id",
                                        string="選擇工資項目", required=False, )
    assembly_material_ids = fields.One2many(comodel_name="lancer.main.item.assemblymaterial",
                                            inverse_name="main_item_id", string="選擇材料", required=False, )
    assembly_manage_rate = fields.Float(string="管銷百分比", required=False, )
    assembly_profit_rate = fields.Float(string="利潤百分比", required=False, )

class LancerMainItemProcesscost(models.Model):
    _name = 'lancer.main.item.processcost'
    _rec_name = 'process'
    _order = "process, id"
    _description = '品項-金屬加工-內製委外加工成本'

    main_item_id = fields.Many2one(comodel_name="lancer.main.item", string="品項", required=True, ondelete='cascade')
    metal_version_id = fields.Many2one('lancer.version.metal', string='版次')
    process = fields.Integer(string='工序')
    process_num = fields.Char(string='工序編號')
    process_name = fields.Char(string='工序名稱')
    wage_rate = fields.Float(string='工資率')
    std_hour = fields.Float(string='標準工時')
    process_cost = fields.Float(string='加工成本')
    unit_price = fields.Float(string='公斤/吋單價')
    out_price = fields.Float(string='委外單價')
    is_inout = fields.Boolean(string="內製否", )
    is_std = fields.Boolean(string="標工否", )
    calc_role = fields.Selection(string="計算方式", selection=[('1', '加工單價(PCS)＝加工單價(KG) / 支數'),
                                                           ('2', '加工單價(PCS)＝下料長 / 25.4 * 加工單價(寸)'),
                                                           ('3', ''),
                                                           ], required=False, )


# 手柄射出-用料成本 + 內製委外加工成本
class LancerMainItemHandleMaterial(models.Model):
    _name = 'lancer.main.item.handlematerial'
    _rec_name = 'process'
    _order = "process, id"
    _description = '品項-手柄射出-加工工序'

    def _get_handle_process_wage(self):
        return self.env['ir.config_parameter'].sudo().get_param('lancer_handle_process_wage')

    main_item_id = fields.Many2one(comodel_name="lancer.main.item", string="品項", required=True, ondelete='cascade')
    handle_version_id = fields.Many2one('lancer.version.handle', string='版次')
    process = fields.Many2one('lancer.handlematerial.process', string='加工工序')
    material = fields.Many2one('lancer.handlematerial.material', string='材質')
    cavity_num = fields.Float(string='模穴數')
    original_price = fields.Float(string='原枓單價')
    dyeing = fields.Float(string='染色(打粒)')
    net_weight = fields.Float(string='淨重(G)')
    gross_weight = fields.Float(string='毛重(G)')
    material_cost = fields.Float(string='材料成本')

    process_hour = fields.Float(string='加工時間')
    wage = fields.Float(string='工資', default=_get_handle_process_wage)
    process_price = fields.Float(string='加工單價')
    inout = fields.Selection(string="內外", selection=[('1', '內製'), ('2', '委外'), ], required=False, default="1")

    # master_handle_series_id = fields.Many2one(related='main_item_id.handle_series_id', store=True, string='系列別', readonly=True)
    # master_handle_handle_id = fields.Many2one(related='main_item_id.handle_handle_id', store=True, string='尺吋', readonly=True)

    # 材質改變
    @api.onchange('material')
    def onchange_material(self):
        self.cavity_num = 0
        self.original_price = 0
        self.net_weight = 0
        self.cavity_num = 0
        self.dyeing = 0
        self.gross_weight = 0
        master_handle_series_id = self.main_item_id.handle_series_id.id
        master_handle_handle_id = self.main_item_id.handle_handle_id.id
        cost_handle_file = self.env['lancer.cost.handle.file'].search(
            [('handle_series_id', '=', master_handle_series_id),
             ('handle_handle_id', '=', master_handle_handle_id),
             ('process', '=', self.process.id),
             ('material', '=', self.material.id),
             ], limit=1)
        if cost_handle_file:
            self.original_price = cost_handle_file.original_price
            self.net_weight = cost_handle_file.net_weight

    # 模穴數改變
    @api.onchange('cavity_num', 'dyeing')
    def onchange_cavity_num(self):
        if self.cavity_num != 0:
            # 毛重=淨重+(20/模穴數)
            self.gross_weight = self.net_weight + (20 / self.cavity_num)
            # 材料成本=(毛重 * (原料成本+染色))/1000
            self.material_cost = (self.gross_weight * (self.original_price + self.cavity_num)) / 1000

    # 加工時間
    @api.onchange('process_hour', 'wage')
    def onchange_process_hour(self):
        if self.process_hour != 0 and self.cavity_num != 0:
            # 加工單價 = 工資 / ((28800/加工時間) * 模穴數)* 1.2
            self.process_price = self.wage / ((28800 / self.process_hour) * self.cavity_num) * 1.2
    # txt_Pro31.Text = (txt_Pro21.Text / ((28800 / txt_Pro11.Text) * txt_Mat011.Text) *1.2)


# 手柄射出-內製委外加工成本
class LancerMainItemHandleProcessCost(models.Model):
    _name = 'lancer.main.item.handleprocesscost'
    _rec_name = 'id'
    _order = "id"
    _description = '品項-手柄射出-內製委外加工成本'

    main_item_id = fields.Many2one(comodel_name="lancer.main.item", string="品項", required=True, ondelete='cascade')

    process_hour = fields.Float(string='加工時間')
    wage = fields.Float(string='工資')
    process_price = fields.Float(string='加工單價')
    inout = fields.Selection(string="內外", selection=[('1', '內製'), ('2', '委外'), ], required=False, default="1")


# 組裝-選擇工資項目
class LancerMainItemAssemblyWage(models.Model):
    _name = 'lancer.main.item.assemblywage'
    _rec_name = 'id'
    _order = "id"
    _description = '品項-組裝工資'

    main_item_id = fields.Many2one(comodel_name="lancer.main.item", string="品項", required=True, ondelete='cascade')

    routing_wages_id = fields.Many2one(comodel_name="lancer.routing.wages", string="工資項目", required=False,
                                       ondelete='cascade')
    num = fields.Float(string='次數/面數')
    price = fields.Float(string='價格')


# 組裝-選擇材料
class LancerMainItemAssemblyMaterial(models.Model):
    _name = 'lancer.main.item.assemblymaterial'
    _rec_name = 'id'
    _order = "id"
    _description = '品項-組裝材料'

    main_item_id = fields.Many2one(comodel_name="lancer.main.item", string="品項", required=True, ondelete='cascade')

    routing_material_id = fields.Many2one(comodel_name="lancer.routing.material", string="材料", required=False, )
    price = fields.Float(string='價格')


class LancerHandleAttrsRecord(models.Model):
    _name = 'lancer.handle.attrs.record'
    _rec_name = 'name'
    _description = '材質特徵質集合'

    name = fields.Char()
    # handle_material_id = fields.Many2one('lancer.main.item')
