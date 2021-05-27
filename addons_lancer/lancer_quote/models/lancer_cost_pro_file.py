# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import api, fields, models


class LancerCostProFile(models.Model):
    _name = 'lancer.cost.pro.file'
    _description = '金屬加工-人工成本'

    active = fields.Boolean(default=True, string='是否啟用')
    sequence = fields.Integer(required=True, default=10)
    routing_shape_id = fields.Many2one(comodel_name='lancer.routing.shape', string='形狀')
    routing_coating_id = fields.Many2one(comodel_name='lancer.routing.coating', string='鍍層')
    routing_cutting_id = fields.Many2one(comodel_name='lancer.routing.cutting', string='刃口')
    routing_outer_id = fields.Many2one(comodel_name='lancer.routing.outer', string='外徑')
    process = fields.Integer(string="工序", required=False, )
    process_num = fields.Char(string="工序編號", required=False, )
    process_name = fields.Char(string="工序名稱", required=False, )
    wage_rate = fields.Float(string='工資率')
    std_hour = fields.Float(string='標準工時')
    process_cost = fields.Float(string='加工成本')
    #unit_price = fields.Float(string='公斤/吋單價')
    out_price = fields.Float(string='委外單價')
    is_inout = fields.Boolean(string="內製否", )
    is_std = fields.Boolean(string="標工否", )



