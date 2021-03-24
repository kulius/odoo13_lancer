# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import api, fields, models


class LancerRoutingOuter(models.Model):
    _name = 'lancer.routing.outer'
    _rec_name = 'name'
    _description = 'Lancer Routing Outer Item'

    name = fields.Char(string='鋼刄外徑名稱')
    outer_code = fields.Char(string='鋼刄外徑代碼')
    active = fields.Boolean(default=True, string='是否啟用')
    sequence = fields.Integer(required=True, default=10)

    def name_get(self):
        res = []
        for rec in self:
            name = rec.name
            if rec.outer_code:
                name = '[' + rec.outer_code + '] ' + name
            else:
                name = name
            res.append((rec.id, name))
        return res
