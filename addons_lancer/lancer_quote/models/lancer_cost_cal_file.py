# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import api, fields, models


class LancerCostCalFile(models.Model):
    _name = 'lancer.cost.cal.file'
    _description = '金屬加工-單重長度表'

    active = fields.Boolean(default=True, string='是否啟用')
    sequence = fields.Integer(required=True, default=10)
    routing_shape_id = fields.Many2one(comodel_name='lancer.routing.shape', string='形狀')
    routing_coating_id = fields.Many2one(comodel_name='lancer.routing.coating', string='鍍層')
    routing_cutting_id = fields.Many2one(comodel_name='lancer.routing.cutting', string='刃口')
    routing_outer_id = fields.Many2one(comodel_name='lancer.routing.outer', string='外徑')
    cal_change = fields.Float(string='單重換算', digits=(12, 6))
    calc_long = fields.Float(string='物料長', digits=(12, 6))

