# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)
from odoo import api, fields, models


class LancerMetalType(models.Model):
    _name = 'lancer.metal.type'
    _rec_name = 'name'
    _description = 'Lance Metal Type By Main Item Use'

    name = fields.Char(string='鋼材規格名稱')
    active = fields.Boolean(default=True, string='是否啟用')
    sequence = fields.Integer(required=True, default=10)
