# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import api, fields, models


class LancerCostMapFile(models.Model):
    _name = 'lancer.cost.map.file'
    _description = 'Lancer Cost Map File 特徵值關係表'

    active = fields.Boolean(default=True, string='是否啟用')
    sequence = fields.Integer(required=True, default=10)
    routing_coating_id = fields.Many2one(comodel_name='lancer.routing.coating', string='鍍層')
    routing_cutting_id = fields.Many2one(comodel_name='lancer.routing.cutting', string='刃口')
    routing_outer_id = fields.Many2one(comodel_name='lancer.routing.outer', string='外徑')
    routing_shape_id = fields.Many2one(comodel_name='lancer.routing.shape', string='形狀')
