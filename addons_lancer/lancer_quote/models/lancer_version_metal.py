# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import api, fields, models, _


class LancerVersionMetal(models.Model):
    _name = 'lancer.version.metal'
    _rec_name = 'name'
    _description = '金屬加工版次-主檔'

    def _get_metal_work_labor(self):
        return self.env['ir.config_parameter'].sudo().get_param('lancer_metal_work_labor')
    def _get_metal_work_make(self):
        return self.env['ir.config_parameter'].sudo().get_param('lancer_metal_work_make')
    def _get_metal_work_efficiency(self):
        return self.env['ir.config_parameter'].sudo().get_param('lancer_metal_work_efficiency')
    def _get_metal_work_yield(self):
        return self.env['ir.config_parameter'].sudo().get_param('lancer_metal_work_yield')

    name = fields.Char(string='版次編號', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))

    metal_blade = fields.Boolean(string="加工鋼刃", default=True)
    metal_shape_id = fields.Many2one(comodel_name="lancer.routing.shape", string="形狀", required=False, )
    metal_coating_id = fields.Many2one(comodel_name="lancer.routing.coating", string="鍍層", required=False, )
    metal_cutting_id = fields.Many2one(comodel_name="lancer.routing.cutting", string="刃口", required=False, )
    metal_outer_id = fields.Many2one(comodel_name="lancer.routing.outer", string="外徑", required=False, )

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
    metal_item_processcost_ids = fields.One2many(comodel_name="lancer.version.processcost",
                                                 inverse_name="metal_version_id", string="內製/委外加工成本", required=False, )

    metal_work_labor = fields.Float(string="人工成本", required=False, default=_get_metal_work_labor)
    metal_work_make = fields.Float(string="製造費", required=False, default=_get_metal_work_make)
    metal_work_efficiency = fields.Float(string="效率", required=False, default=_get_metal_work_efficiency)
    metal_work_yield = fields.Float(string="良率", required=False, default=_get_metal_work_yield)
    metal_work_plating = fields.Float(string="+電鍍", required=False, )
    metal_work_dye_blackhead = fields.Float(string="+染黑頭", required=False, )
    metal_work_spray_blackhead = fields.Float(string="+噴黑頭", required=False, )
    metal_work_sum1 = fields.Float(string="合計1", required=False, )
    metal_work_sum2 = fields.Float(string="合計2", required=False, )
    metal_work_sum3 = fields.Float(string="合計3", required=False, )

    active = fields.Boolean(default=True, string='是否啟用')
    sequence = fields.Integer(required=True, default=10)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('lancer.version.metal') or _('New')

        result = super(LancerVersionMetal, self).create(vals)
        return result

class LancerVersionProcesscost(models.Model):
    _name = 'lancer.version.processcost'
    _rec_name = 'process'
    _order = "process, id"
    _description = '金屬加工版次-主檔 工序'

    metal_version_id = fields.Many2one('lancer.version.metal', string='版次', ondelete='cascade')
    main_item_id = fields.Many2one(comodel_name="lancer.main.item", string="品項", ondelete='cascade')
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