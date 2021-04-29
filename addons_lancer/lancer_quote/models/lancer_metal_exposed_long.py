# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import api, fields, models


class LancerMetalExposedLong(models.Model):
    _name = 'lancer.metal.exposed.long'
    _rec_name = 'name'
    _description = '外露長度'

    name = fields.Integer(string='外露長度長度(mm)')
    depth = fields.Integer(string='組立深度(mm)')
    active = fields.Boolean(default=True, string='是否啟用')
    sequence = fields.Integer(required=True, default=10)
