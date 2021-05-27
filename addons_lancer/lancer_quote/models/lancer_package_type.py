# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import api, fields, models


class LancerPackageType(models.Model):
    _name = 'lancer.package.type'
    _rec_name = 'name'
    _order = "sequence,code, id"
    _description = '報價單-包裝大分類'

    code = fields.Char(string='代號')
    name = fields.Char(string='包裝大分類名稱', translate=True)
    active = fields.Boolean(default=True, string='是否啟用')
    sequence = fields.Integer(required=True, default=10)

    def name_get(self):
        res = []
        for rec in self:
            name = rec.name
            if rec.code:
                name = '[' + rec.code + '] ' + name
            else:
                name = name
            res.append((rec.id, name))
        return res
