# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import api, fields, models


class LancerCostHandleFile(models.Model):
    _name = 'lancer.cost.handle.file'
    _description = '手柄射出-加工工序 手柄用料'

    active = fields.Boolean(default=True, string='是否啟用')
    sequence = fields.Integer(required=True, default=10)
    process = fields.Many2one('lancer.handlematerial.process', string='加工工序')
    material = fields.Many2one('lancer.handlematerial.material', string='材質')

    handle_series_id = fields.Many2one(comodel_name="lancer.routing.series", string="系列別", required=False, )
    handle_handle_id = fields.Many2one(comodel_name="lancer.routing.handle", string="手柄尺吋", required=False, )

    cavity_num = fields.Float(string='模穴數')
    original_price = fields.Float(string='原枓單價')
    dyeing = fields.Float (string='染色(打粒)')
    net_weight = fields.Float(string='淨重(G)')
    gross_weight = fields.Float(string='毛重(G)', size=10, digits=(6, 4))
    material_cost = fields.Float(string='材料成本', size=10, digits=(6, 4))

