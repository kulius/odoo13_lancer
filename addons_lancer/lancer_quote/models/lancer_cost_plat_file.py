# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import api, fields, models


class LancerCostPlatFile(models.Model):
    _name = 'lancer.cost.plat.file'
    _description = '金屬加工-電鍍單價表'

    active = fields.Boolean(default=True, string='是否啟用')
    sequence = fields.Integer(required=True, default=10)
    routing_coating_id = fields.Many2one(comodel_name='lancer.routing.coating', string='鍍層')
    plat_begin = fields.Float(string='外徑起', digits=(3, 3))
    plat_end = fields.Float(string='外徑迄', digits=(3, 3))
    plat_long_being = fields.Float(string='下料長度起', digits=(12,6))
    plat_long_end = fields.Float(string='下料長度迄', digits=(12, 6))
    plat_cost = fields.Float(string='單價')

