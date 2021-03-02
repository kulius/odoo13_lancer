# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import api, fields, models
import json
from lxml import etree


class LancerMainItem(models.Model):
    _name = 'lancer.main.item'
    _rec_name = 'name'
    _order = "name, id"
    _description = 'Lancer main Item'

    @api.depends('material_cost', 'process_cost', 'manufacture_cost')
    def _amount_all(self):
        """
            Compute the amounts by the Material_Cost、Process_Cost、Manufacture_Cost.
        """
        price = self.material_cost + self.process_cost + self.manufacture_cost
        self.update({'item_total_cost': price})

    active = fields.Boolean(default=True, string='是否啟用')
    name = fields.Char(string='品項品名規格')
    main_id = fields.Many2one(comodel_name="lancer.main", string="所屬主件", required=True, )
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

    metal_type = fields.Many2one('lancer.metal.type', string="鋼材規格", required=False, )
    metal_spec = fields.Many2one('lancer.metal.spec', string="鋼材種類", required=False, )
    metal_long = fields.Char(string="物料長(mm)", required=False, )
    metal_cutting_long = fields.Many2one('lancer.metal.cutting.long', string="下料長度(mm)", required=False, )
    metal_cut = fields.Char(string="切料節數", required=False, )
    metal_weight = fields.Char(string="鋼刃單隻重量", required=False, )
    metal_material = fields.Char(string="材料(元/KG)", required=False, )
    metal_price = fields.Char(string="單隻價格", required=False, )

    metal_is_std_hour = fields.Boolean(string="依標工計算", )
    metal_item_processcost_ids = fields.One2many(comodel_name="lancer.main.item.processcost",
                                                 inverse_name="main_item_id", string="內製/委外加工成本", required=False, )

    metal_work_labor = fields.Float(string="人工成本", required=False, )
    metal_work_make = fields.Float(string="製造費", required=False, )
    metal_work_efficiency = fields.Float(string="效率", required=False, )
    metal_work_yield = fields.Float(string="良率", required=False, )
    metal_work_plating = fields.Float(string="+電鍍", required=False, )
    metal_work_dye_blackhead = fields.Float(string="+染黑頭", required=False, )
    metal_work_spray_blackhead = fields.Float(string="+噴黑頭", required=False, )
    metal_work_sum1 = fields.Float(string="合計1", required=False, )
    metal_work_sum2 = fields.Float(string="合計2", required=False, )
    metal_work_sum3 = fields.Float(string="合計3", required=False, )

    # 手柄射出
    handle_series_id = fields.Many2one(comodel_name="lancer.routing.series", string="系列別", required=False, )
    handle_handle_id = fields.Many2one(comodel_name="lancer.routing.handle", string="手柄尺吋", required=False, )
    handle_version_id = fields.Many2one(comodel_name="lancer.routing.version", string="版本版次", required=False, )

    handle_materialcost_ids = fields.One2many(comodel_name="lancer.main.item.handlematerial",
                                              inverse_name="main_item_id", string="用料成本", required=False, )
    handle_processcost_ids = fields.One2many(comodel_name="lancer.main.item.handleprocesscost",
                                             inverse_name="main_item_id", string="內製/委外加工成本", required=False, )

    handle_moldcost1 = fields.Float(string="第一層射出", required=False, )
    handle_moldcost2 = fields.Float(string="第二層射出", required=False, )
    handle_moldcost3 = fields.Float(string="第三層射出", required=False, )
    handle_moldcost4 = fields.Float(string="第四層射出", required=False, )
    handle_moldcost5 = fields.Float(string="第五層射出", required=False, )
    handle_moldcost6 = fields.Float(string="第六層射出", required=False, )
    handle_mandrel = fields.Float(string="芯軸", required=False, )
    handle_elecmandrel = fields.Float(string="電工芯軸", required=False, )

    handle_work_make = fields.Float(string="製造費", required=False, )
    handle_work_mould = fields.Float(string="模具分攤", required=False, )
    handle_work_efficiency = fields.Float(string="效率", required=False, )
    handle_work_yield = fields.Float(string="良率", required=False, )
    handle_work_sum = fields.Float(string="總成本", required=False, )
    # 包裝
    assembly_wage_ids = fields.One2many(comodel_name="lancer.main.item.assemblywage", inverse_name="main_item_id",
                                        string="選擇工資項目", required=False, )
    assembly_material_ids = fields.One2many(comodel_name="lancer.main.item.assemblymaterial",
                                            inverse_name="main_item_id", string="選擇材料", required=False, )
    assembly_manage_rate = fields.Float(string="管銷百分比", required=False, )
    assembly_profit_rate = fields.Float(string="利潤百分比", required=False, )


# 金屬加工-內製委外加工成本
class LancerMainItemProcesscost(models.Model):
    _name = 'lancer.main.item.processcost'
    _rec_name = 'process'
    _order = "process, id"
    _description = 'Lancer main Item process cost'

    main_item_id = fields.Many2one(comodel_name="lancer.main.item", string="品項", required=True, )

    process = fields.Char(string='工序')
    process_num = fields.Char(string='工序編號')
    std_hour = fields.Char(string='標準工時')
    process_cost = fields.Char(string='加工成本')
    unit_price = fields.Char(string='公斤/吋單價')
    out_price = fields.Char(string='委外單價')
    inout = fields.Selection(string='內製/委外', selection=[('internal', '內製'), ('external', '外製')])


# 手柄射出-用料成本
class LancerMainItemHandleMaterial(models.Model):
    _name = 'lancer.main.item.handlematerial'
    _rec_name = 'process'
    _order = "process, id"
    _description = 'Lancer main Item handlematerial'

    main_item_id = fields.Many2one(comodel_name="lancer.main.item", string="品項", required=True, )

    process = fields.Many2one('lancer.handlematerial.process', string='加工工序')
    material = fields.Many2one('lancer.handlematerial.material', string='材質')
    cavity_num = fields.Float(string='模穴數')
    original_price = fields.Float(string='原枓單價')
    dyeing = fields.Char(string='染色(打粒)')
    net_weight = fields.Float(string='淨重(G)')
    gross_weight = fields.Float(string='毛重(G)')
    material_cost = fields.Float(string='材料成本')


# 手柄射出-內製委外加工成本
class LancerMainItemHandleProcessCost(models.Model):
    _name = 'lancer.main.item.handleprocesscost'
    _rec_name = 'id'
    _order = "id"
    _description = 'Lancer main Item handleprocesscost'

    main_item_id = fields.Many2one(comodel_name="lancer.main.item", string="品項", required=True, )

    process_hour = fields.Float(string='加工時間')
    wage = fields.Float(string='工資')
    process_price = fields.Float(string='加工單價')
    inout = fields.Char(string='內外')


# 組裝-選擇工資項目
class LancerMainItemAssemblyWage(models.Model):
    _name = 'lancer.main.item.assemblywage'
    _rec_name = 'id'
    _order = "id"
    _description = 'Lancer main Item assemblywage'

    main_item_id = fields.Many2one(comodel_name="lancer.main.item", string="品項", required=True, )

    routing_wages_id = fields.Many2one(comodel_name="lancer.routing.wages", string="工資項目", required=False, )
    num = fields.Float(string='次數/面數')
    price = fields.Float(string='價格')


# 組裝-選擇材料
class LancerMainItemAssemblyMaterial(models.Model):
    _name = 'lancer.main.item.assemblymaterial'
    _rec_name = 'id'
    _order = "id"
    _description = 'Lancer main Item assemblymaterial'

    main_item_id = fields.Many2one(comodel_name="lancer.main.item", string="品項", required=True, )

    routing_material_id = fields.Many2one(comodel_name="lancer.routing.material", string="材料", required=False, )
    price = fields.Float(string='價格')
