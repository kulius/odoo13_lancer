# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import api, fields, models


class LancerMetalCuttingLong(models.Model):
    _name = 'lancer.metal.cutting.long'
    _rec_name = 'name'
    _description = '金屬加工-鋼刄外徑'

    metal_outer_id = fields.Many2one(comodel_name="lancer.routing.outer", string="鋼刄外徑")
    name = fields.Integer(string='下料長度(mm)')
    active = fields.Boolean(default=True, string='是否啟用')
    sequence = fields.Integer(required=True, default=10)
