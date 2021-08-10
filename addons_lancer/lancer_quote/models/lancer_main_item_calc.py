# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


# 品項 計算金屬加工
class LancerMainItemCalcMetal(models.Model):
    _inherit = 'lancer.main.item'
    _description = '品項 計算金屬加工'

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

    # 形狀、外徑、鋼材種類、鋼材規格、下料長度 計算成本
    @api.onchange('metal_shape_id', 'metal_outer_id', 'metal_spec_id', 'metal_type_id', 'metal_cutting_long_id', 'metal_long')
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
        a=(self.metal_long * cal_change / self.metal_cut) * 0.001
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

    # 電鍍計算
    @api.onchange('plating_select', 'metal_work_plating', 'metal_work_dye_blackhead', 'metal_work_spray_blackhead')
    def onchange_plating_select(self):
        #電鍍成本=((單支價格+人工成本+製造費)/效率/良率)+電鍍單價
        sum_process_cost = sum([l.process_cost for l in self.metal_item_processcost_ids])
        sum_out_price = sum([l.out_price for l in self.metal_item_processcost_ids])

        self.metal_work_sum1 = ((self.metal_price + sum_process_cost + self.metal_work_make) / self.metal_work_efficiency /self.metal_work_yield) + self.metal_work_plating
        self.metal_work_sum2 = ((self.metal_price + sum_process_cost + self.metal_work_make) / self.metal_work_efficiency /self.metal_work_yield) + self.metal_work_dye_blackhead
        self.metal_work_sum3 = ((self.metal_price + sum_process_cost + self.metal_work_make) / self.metal_work_efficiency /self.metal_work_yield) + self.metal_work_spray_blackhead

        #料工費 計算及取得
        self.material_cost = self.metal_price
        self.process_cost = sum_process_cost
        self.manufacture_cost = self.metal_work_make


#------------------------------------------------------------------------------------
    #取得 手柄版本 並覆蓋 目前所有資料
    @api.onchange('handle_version_id')
    def set_handle_version(self):
        if not self.handle_version_id:
            return
        version_record = self.env['lancer.version.handle'].search([('id', '=', self.handle_version_id.id)])
        if version_record:
            self.handle_series_id = version_record.handle_series_id.id
            self.handle_handle_id = version_record.handle_handle_id.id
            new_lines = []
            for line in version_record.handle_materialcost_ids:
                vals = line.read()[0]
                vals.update({
                    'main_item_id': self.id,
                })
                # vals.pop('bom_id', False)
                new_lines.append((0, 0, vals))
            self.handle_materialcost_ids.unlink()
            self.handle_materialcost_ids = new_lines
            self.handle_moldcost1 = version_record.handle_moldcost1
            self.handle_moldcost2 = version_record.handle_moldcost2
            self.handle_moldcost3 = version_record.handle_moldcost3
            self.handle_moldcost4 = version_record.handle_moldcost4
            self.handle_moldcost5 = version_record.handle_moldcost5
            self.handle_moldcost6 = version_record.handle_moldcost6
            self.handle_mandrel = version_record.handle_mandrel
            self.handle_elecmandrel = version_record.handle_elecmandrel
            self.handle_mold_total = version_record.handle_mold_total

            # self.handle_materialcost_ids = version_record.handle_materialcost_ids.ids
    # 新增手柄版次
    def handle_cost_calc_safe(self):
        if self.handle_version_id:
            raise ValidationError(_("請先清除 版本版次內容 才能新增版次"))
            return
        version = self.env['lancer.version.handle']
        new_lines = []

        # version.handle_materialcost_ids = new_lines
        values = {
            'handle_series_id': self.handle_series_id.id,
            'handle_handle_id': self.handle_handle_id.id,
            'handle_moldcost1': self.handle_moldcost1,
            'handle_moldcost2': self.handle_moldcost2,
            'handle_moldcost3': self.handle_moldcost3,
            'handle_moldcost4': self.handle_moldcost4,
            'handle_moldcost5': self.handle_moldcost5,
            'handle_moldcost6': self.handle_moldcost6,
            'handle_mandrel': self.handle_mandrel,
            'handle_elecmandrel': self.handle_elecmandrel,
            'handle_mold_total': self.handle_mold_total,
            # 'handle_materialcost_ids': new_lines,
        }
        version_id = version.create(values)
        # values = (vals.get('partsorder_ids', [])) + [(0, 0, {'sourceorder_id': created_id,
        #                                                      completedby_id': uid})]
        for line in self.handle_materialcost_ids:
            vals = line.read()[0]
            vals.update({
                'handle_version_id': version_id.id,
                'material': vals.get('material')[0],
                'process': vals.get('process')[0],
            })
            vals.pop('main_item_id', False)
            new_lines.append((0, 0, vals))
        version_id.handle_materialcost_ids = new_lines
        self.handle_version_id = version_id.id
        return version_id
        # version.handle_series_id = self.handle_series_id.id,

    # 新增金屬版次
    def metal_cost_calc_safe(self):
        if self.metal_version_id:
            raise ValidationError(_("請先清除 版本版次內容 才能新增版次"))
            return
        version = self.env['lancer.version.metal']
        new_lines = []
        values = {
            'metal_blade': self.metal_blade,
            'metal_shape_id': self.metal_shape_id.id,
            'metal_coating_id': self.metal_coating_id.id,
            'metal_cutting_id': self.metal_cutting_id.id,
            'metal_spec_id': self.metal_spec_id.id,
            'metal_type_id': self.metal_type_id.id,
            'metal_long': self.metal_long,
            'metal_cutting_long_id': self.metal_cutting_long_id.id,
            'metal_exposed_long_id': self.metal_exposed_long_id.id,
            'metal_outer_id': self.metal_outer_id.id,

            'metal_cut': self.metal_cut,
            'metal_weight': self.metal_weight,
            'metal_material': self.metal_material,
            'metal_price': self.metal_price,
            'metal_count': self.metal_count,
            'metal_is_std_hour': self.metal_is_std_hour,

            'metal_work_labor': self.metal_work_labor,
            'metal_work_make': self.metal_work_make,
            'metal_work_efficiency': self.metal_work_efficiency,
            'metal_work_yield': self.metal_work_yield,
            'metal_work_plating': self.metal_work_plating,
            'metal_work_dye_blackhead': self.metal_work_dye_blackhead,
            'metal_work_spray_blackhead': self.metal_work_spray_blackhead,
            'metal_work_sum1': self.metal_work_sum1,
            'metal_work_sum2': self.metal_work_sum2,
            'metal_work_sum3': self.metal_work_sum3,

        }
        version_id = version.create(values)
        for line in self.metal_item_processcost_ids:
            vals = line.read()[0]
            vals.update({
                'metal_version_id': version_id.id,
            })
            vals.pop('main_item_id', False)
            new_lines.append((0, 0, vals))
        version_id.metal_item_processcost_ids = new_lines
        self.metal_version_id = version_id.id
        return version_id

    #取得 金屬版本 並覆蓋 目前所有資料
    @api.onchange('metal_version_id')
    def set_metal_version(self):
        if not self.metal_version_id:
            return
        version = self.env['lancer.version.metal'].search([('id', '=', self.metal_version_id.id)])
        if not version:
            return
        self.metal_blade = version.metal_blade
        self.metal_shape_id = version.metal_shape_id.id
        self.metal_coating_id = version.metal_coating_id.id
        self.metal_cutting_id = version.metal_cutting_id.id
        self.metal_spec_id = version.metal_spec_id.id
        self.metal_type_id = version.metal_type_id.id
        self.metal_long = version.metal_long
        self.metal_cutting_long_id = version.metal_cutting_long_id.id
        self.metal_exposed_long_id = version.metal_exposed_long_id.id
        self.metal_outer_id = version.metal_outer_id.id

        self.metal_cut = version.metal_cut
        self.metal_weight = version.metal_weight
        self.metal_material = version.metal_material
        self.metal_price = version.metal_price
        self.metal_count = version.metal_count
        self.metal_is_std_hour = version.metal_is_std_hour

        self.metal_work_labor = version.metal_work_labor
        self.metal_work_make = version.metal_work_make
        self.metal_work_efficiency = version.metal_work_efficiency
        self.metal_work_yield = version.metal_work_yield
        self.metal_work_plating = version.metal_work_plating
        self.metal_work_dye_blackhead = version.metal_work_dye_blackhead
        self.metal_work_spray_blackhead = version.metal_work_spray_blackhead
        self.metal_work_sum1 = version.metal_work_sum1
        self.metal_work_sum2 = version.metal_work_sum2
        self.metal_work_sum3 = version.metal_work_sum3

        new_lines = []
        for line in version.metal_item_processcost_ids:
            vals = line.read()[0]
            vals.update({
                'main_item_id': self.id,
            })
            new_lines.append((0, 0, vals))
        self.metal_item_processcost_ids.unlink()
        self.metal_item_processcost_ids = new_lines



    #取得組立料工費
    @api.onchange('assembly_wage_ids', 'assembly_material_ids', 'assembly_manage_rate', 'assembly_profit_rate')
    def onchange_assembly_wage_ids(self):
        self.process_cost =  sum(self.assembly_wage_ids.mapped('amount'))
        self.material_cost = sum(self.assembly_material_ids.mapped('price'))
        self.manufacture_cost = (self.material_cost+self.process_cost)*(self.assembly_manage_rate+self.assembly_profit_rate)

