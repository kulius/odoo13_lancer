# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import api, fields, models


class LancerRoutingCoating(models.Model):
    _name = 'lancer.routing.coating'
    _rec_name = 'name'
    _description = 'Lancer Routing Coating Item'

    name = fields.Char(string='鍍層名稱')
    coating_code = fields.Char(string='鍍層代碼')
    active = fields.Boolean(default=True, string='是否啟用')
    sequence = fields.Integer(required=True, default=10)

    def name_get(self):
        res = []
        for rec in self:
            name = rec.name
            if rec.coating_code:
                name = '[' + rec.coating_code + '] ' + name
            else:
                name = name
            res.append((rec.id, name))
        return res
