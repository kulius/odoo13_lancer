# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)
from odoo import api, fields, models


class LancerMetalType(models.Model):
    _name = 'lancer.metal.type'
    _rec_name = 'name'
    _description = '金屬加工-鋼材規格'

    name = fields.Char(string='鋼材規格說明', translate=True)
    metal_type_code = fields.Char(string='鋼材規格代號')
    active = fields.Boolean(default=True, string='是否啟用')
    sequence = fields.Integer(required=True, default=10)

    # def name_get(self):
    #     res = []
    #     for rec in self:
    #         name = rec.name
    #         if rec.metal_type_code:
    #             name = '[' + rec.metal_type_code + '] ' + name
    #         else:
    #             name = name
    #         res.append((rec.id, name))
    #     return res
