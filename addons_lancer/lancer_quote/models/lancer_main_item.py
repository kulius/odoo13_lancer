# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError
import json
from lxml import etree


class LancerMainItem(models.Model):
    _name = 'lancer.main.item'
    _rec_name = 'name'
    _order = "name, id"
    _description = 'Lancer main Item'

    def _get_metal_work_labor(self):
        return self.env['ir.config_parameter'].sudo().get_param('lancer_metal_work_labor')
    def _get_metal_work_make(self):
        return self.env['ir.config_parameter'].sudo().get_param('lancer_metal_work_make')
    def _get_metal_work_efficiency(self):
        return self.env['ir.config_parameter'].sudo().get_param('lancer_metal_work_efficiency')
    def _get_metal_work_yield(self):
        return self.env['ir.config_parameter'].sudo().get_param('lancer_metal_work_yield')

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

    metal_spec_id = fields.Many2one('lancer.metal.spec', string="鋼材種類", required=False, )
    metal_type_id = fields.Many2one('lancer.metal.type', string="鋼材規格", required=False, )
    metal_long = fields.Float(string="物料長(mm)", required=False, )
    metal_cutting_long_id = fields.Many2one('lancer.metal.cutting.long', string="下料長度(mm)", required=False, )
    metal_cut = fields.Float(string="切料節數", required=False, )
    metal_weight = fields.Float(string="鋼刃單隻重量", required=False, )
    metal_material = fields.Float(string="材料(元/KG)", required=False, )
    metal_price = fields.Float(string="單隻價格", required=False, )
    metal_count = fields.Float(string="支數(支/KG)", required=False, )

    metal_is_std_hour = fields.Boolean(string="依標工計算", )
    metal_item_processcost_ids = fields.One2many(comodel_name="lancer.main.item.processcost",
                                                 inverse_name="main_item_id", string="內製/委外加工成本", required=False, )

    metal_work_labor = fields.Float(string="人工成本", required=False, default = _get_metal_work_labor)
    metal_work_make = fields.Float(string="製造費", required=False, default = _get_metal_work_make )
    metal_work_efficiency = fields.Float(string="效率", required=False, default = _get_metal_work_efficiency )
    metal_work_yield = fields.Float(string="良率", required=False, default = _get_metal_work_yield )
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

    #形狀 影響 鍍層
    @api.onchange('metal_shape_id')
    def onchange_metal_shape(self):
        cost_map_file = self.env['lancer.cost.map.file'].search([('routing_shape_id', '=', self.metal_shape_id.id)])
        list = []
        result = {}
        for line in cost_map_file:
            list.append(line.routing_coating_id.id)
        result['domain'] = {'metal_coating_id': [('id', 'in', list)]}
        return result

    # 形狀、鍍層 連動 刃口
    @api.onchange('metal_shape_id','metal_coating_id')
    def onchange_metal_coating(self):
        cost_map_file = self.env['lancer.cost.map.file'].search([('routing_shape_id', '=', self.metal_shape_id.id)
                                                                    , ('routing_coating_id', '=', self.metal_coating_id.id)])
        list = []
        result = {}
        for line in cost_map_file:
            list.append(line.routing_cutting_id.id)
        result['domain'] = {'metal_cutting_id': [('id', 'in', list)]}
        return result

    # 形狀、鍍層、刃口 連動 外徑
    @api.onchange('metal_shape_id', 'metal_coating_id', 'metal_cutting_id')
    def onchange_metal_cutting(self):
        cost_map_file = self.env['lancer.cost.map.file'].search([('routing_shape_id', '=', self.metal_shape_id.id)
                                                                    ,('routing_coating_id', '=', self.metal_coating_id.id)
                                                                    ,('routing_cutting_id', '=', self.metal_cutting_id.id)
                                                                 ])
        list = []
        result = {}
        for line in cost_map_file:
            list.append(line.routing_cutting_id.id)

        result['domain'] = {'metal_type_id': [('id', 'in', list)]}
        return result

    # 形狀、外徑 連動 鋼材種類
    @api.onchange('metal_shape_id', 'metal_outer_id')
    def onchange_metal_shape_outer(self):
        cost_wire_file = self.env['lancer.cost.wire.file'].search([('routing_shape_id', '=', self.metal_shape_id.id)
                                                                    , ('routing_outer_id', '=',self.metal_outer_id.id)
                                                                 ])
        list = []
        result = {}
        for line in cost_wire_file:
            list.append(line.metal_spec_id.id)
        result['domain'] = {'metal_spec_id': [('id', 'in', list)]}
        return result

    # 外徑 連動 長度
    @api.onchange('metal_outer_id')
    def onchange_metal_outer(self):
        metal_cutting_long = self.env['lancer.metal.cutting.long'].search(
            [('metal_outer_id', '=', self.metal_outer_id.id)])

        list= []
        result = {}
        for line in metal_cutting_long:
            list.append(line.id)

        result['domain'] = {'metal_cutting_long_id': [('id', 'in', list)]}
        return result

    # 形狀、外徑、鋼材種類 連動 鋼材規格
    @api.onchange('metal_shape_id', 'metal_outer_id','metal_spec_id')
    def onchange_metal_spec(self):
        cost_wire_file = self.env['lancer.cost.wire.file'].search([('routing_shape_id', '=', self.metal_shape_id.id),
                                                                   ('routing_outer_id', '=', self.metal_outer_id.id),
                                                                   ('metal_spec_id', '=', self.metal_spec_id.id)
                                                                   ])
        list = []
        result = {}
        for line in cost_wire_file:
            list.append(line.metal_type_id.id)
        result['domain'] = {'metal_type_id': [('id', 'in', list)]}
        return result

    # 形狀、外徑、鋼材種類、鋼材規格 計算成本
    @api.onchange('metal_shape_id', 'metal_outer_id', 'metal_spec_id', 'metal_type_id')
    def onchange_metal_type(self):
        if not (self.metal_shape_id and self.metal_outer_id and self.metal_spec_id and self.metal_type_id and self.metal_cutting_long_id):
            return False
        cost_wire_file = self.env['lancer.cost.wire.file'].search([('routing_shape_id', '=', self.metal_shape_id.id),
                                                                   ('routing_outer_id', '=', self.metal_outer_id.id),
                                                                   ('metal_spec_id', '=', self.metal_spec_id.id),
                                                                   ('metal_type_id', '=', self.metal_type_id.id),
                                                                   ], limit=1)
        if cost_wire_file:
            self.metal_material = cost_wire_file.wire_cost + cost_wire_file.iron_cost
        else:
            self.metal_material = 0

        cost_cal_file = self.env['lancer.cost.cal.file'].search([('routing_shape_id', '=', self.metal_shape_id.id),
                                                                   ('routing_coating_id', '=', self.metal_coating_id.id),
                                                                   ('routing_cutting_id', '=', self.metal_cutting_id.id),
                                                                   ('routing_outer_id', '=', self.metal_outer_id.id),
                                                                   ], limit=1)
        if not cost_cal_file:
            raise ValidationError(_("找不到 單重長度表."))
        cal_change = cost_cal_file.cal_change #單重換算
        self.metal_long = cost_cal_file.calc_long #物料長
        self.metal_cut = self.metal_long / self.metal_cutting_long_id.name #切料節數= 物料長/下料長度
        self.metal_weight = (self.metal_long * cal_change / self.metal_cut) * 0.001 #單支重量=(物料長(mm) * 單重換算 / 切料節數) * 0.001
        self.metal_price = self.metal_material * self.metal_weight #單支價格=單價 * 單支重量
        self.metal_count = 1000/(cal_change * self.metal_cutting_long_id.name)  # 支數 = 1000 / (單重換算 * 下料長 )

        cost_pro_file = self.env['lancer.cost.pro.file'].search([('routing_shape_id', '=', self.metal_shape_id.id),
                                                                   ('routing_coating_id', '=', self.metal_coating_id.id),
                                                                   ('routing_cutting_id', '=', self.metal_cutting_id.id),
                                                                   ('routing_outer_id', '=', self.metal_outer_id.id),
                                                                   ])
        if not cost_pro_file:
            raise ValidationError(_("找不到 內製/委外 加工成本."))
        self.metal_item_processcost_ids = [(5,)]
        for cost_pro in cost_pro_file:
            calc_process_cost = 0
            calc_out_price = 0
            calc_role = 3
            if (cost_pro.process_num == 'Y025') or (cost_pro.process_num == 'Y029') or (cost_pro.process_num == 'Y011') \
                    or (cost_pro.process_num == 'Y027') or (cost_pro.process_num == 'Y028'):
                # 加工單價(PCS)＝加工單價(KG) / 支數
                calc_unit_price = cost_pro.process_cost / self.metal_count
                calc_out_price = cost_pro.process_cost
                calc_role = '1'
            elif cost_pro.process_num == 'Y026':
                #加工單價(PCS)＝下料長 / 25.4 * 加工單價(寸)
                calc_unit_price = self.metal_cutting_long_id.name /25.4 * cost_pro.process_cost
                calc_out_price = cost_pro.process_cost
                calc_role = '2'
            else:
                calc_unit_price = cost_pro.process_cost #加工成本
                calc_out_price = 0
                calc_role = '3'
            vals = {
                'main_item_id': self.id,
                'process': cost_pro.process,
                'process_num': cost_pro.process_num,
                'process_name': cost_pro.process_name,
                'std_hour': cost_pro.std_hour,
                'process_cost': cost_pro.process_cost,
                'unit_price': calc_unit_price,
                'out_price': calc_out_price,
                'is_inout': cost_pro.is_inout,
                'is_std': cost_pro.is_std,
                'calc_role': calc_role,
            }
            self.metal_item_processcost_ids = [(0, 0, vals)]

            #染黑頭
            outer_size = self.metal_outer_id.outer_size # 外徑長度
            # 下料長度*換算率+0.5
            cos_cost4 = self.metal_outer_id.outer_rate * self.metal_cutting_long_id.name + self.metal_outer_id.outer_dye_blackhead_price
            #鍍層單價
            cost_plat_file = self.env['lancer.cost.plat.file'].search([('routing_coating_id', '=', self.metal_coating_id.id),
                                                                       ('plat_begin', '<=',outer_size),
                                                                       ('plat_end', '>=', outer_size),
                                                                       ('plat_long_being', '<=', self.metal_cutting_long_id.name),
                                                                       ('plat_long_end', '>=', self.metal_cutting_long_id.name),
                                                                       ], limit=1)
            if cost_plat_file:
                self.metal_work_plating = cost_plat_file.plat_cost
                self.metal_work_dye_blackhead = cost_plat_file.plat_cost + cos_cost4
            self.metal_work_spray_blackhead = cost_plat_file.plat_cost + 0.3

            #電鍍成本=((單支價格+人工成本+製造費)/效率/良率)+電鍍單價
            sum_process_cost = sum([l.process_cost for l in self.metal_item_processcost_ids])
            sum_out_price = sum([l.out_price for l in self.metal_item_processcost_ids])

            self.metal_work_sum1 = ((self.metal_price + sum_process_cost + self.metal_work_make) / self.metal_work_efficiency /self.metal_work_yield) + self.metal_work_plating
            self.metal_work_sum2 = ((self.metal_price + sum_process_cost + self.metal_work_make) / self.metal_work_efficiency /self.metal_work_yield) + self.metal_work_dye_blackhead
            self.metal_work_sum3 = ((self.metal_price + sum_process_cost + self.metal_work_make) / self.metal_work_efficiency /self.metal_work_yield) + self.metal_work_spray_blackhead










        # 金屬加工-內製委外加工成本
class LancerMainItemProcesscost(models.Model):
    _name = 'lancer.main.item.processcost'
    _rec_name = 'process'
    _order = "process, id"
    _description = 'Lancer main Item process cost'

    main_item_id = fields.Many2one(comodel_name="lancer.main.item", string="品項", required=True, )

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
