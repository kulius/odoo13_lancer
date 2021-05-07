# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import api, fields, models


class LanceMetalSpec(models.Model):
    _name = 'lancer.metal.spec'
    _rec_name = 'name'
    _description = 'Lancer Metal Spec for Main Item Use'

    name = fields.Char(string='鋼材種類名稱', translate=True)
    metal_spec_code = fields.Char(string='鋼材種類代碼')
    active = fields.Boolean(default=True, string='是否啟用')
    sequence = fields.Integer(required=True, default=10)

    # def name_get(self):
    #     res = []
    #     for rec in self:
    #         name = rec.name
    #         if rec.metal_spec_code:
    #             name = '[' + rec.metal_spec_code + '] ' + name
    #         else:
    #             name = name
    #         res.append((rec.id, name))
    #     return res
