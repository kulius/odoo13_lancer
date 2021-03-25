# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import api, fields, models


class LancerCostWireFile(models.Model):
    _name = 'lancer.cost.wire.file'
    _description = 'Lancer Cost Wire File'

    active = fields.Boolean(default=True, string='是否啟用')
    sequence = fields.Integer(required=True, default=10)
    metal_spec_id = fields.Many2one(comodel_name='lancer.metal.spec', string='鋼材種類')
    routing_shape_id = fields.Many2one(comodel_name='lancer.routing.shape', string='形狀')
    routing_outer_id = fields.Many2one(comodel_name='lancer.routing.outer', string='外徑')
    metal_type_id = fields.Many2one(comodel_name='lancer.metal.type', string='鋼材規格')
    wire_cost = fields.Float(string='單價')
    iron_spec = fields.Float(string='盤元規格')
    iron_cost = fields.Float(string='盤元單價')
