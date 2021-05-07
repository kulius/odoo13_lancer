# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import api, fields, models


class LancerHandleMaterialMaterial(models.Model):
    _name = 'lancer.handlematerial.material'
    _rec_name = 'name'
    _description = 'Lancer Main Item Handle Material use Material'

    name = fields.Char(string='手柄材質說明')
    material_code = fields.Char(string='手柄材質代號')
    active = fields.Boolean(default=True, string='是否啟用')
    sequence = fields.Integer(required=True, default=10)

    # def name_get(self):
    #     res = []
    #     for rec in self:
    #         name = rec.name
    #         if rec.material_code:
    #             name = '[' + rec.material_code + '] ' + name
    #         else:
    #             name = name
    #         res.append((rec.id, name))
    #     return res
