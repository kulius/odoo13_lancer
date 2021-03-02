# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import api, fields, models


class LancerMetalCuttingLong(models.Model):
    _name = 'lancer.metal.cutting.long'
    _rec_name = 'name'
    _description = 'Lancer Metal Cutting Long For Main Item Use'

    name = fields.Char(string='下料長度(mm)說明')
    active = fields.Boolean(default=True, string='是否啟用')
    sequence = fields.Integer(required=True, default=10)
