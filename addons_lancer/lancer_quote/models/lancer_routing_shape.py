# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import api, fields, models


class LancerRoutingShape(models.Model):
    _name = 'lancer.routing.shape'
    _rec_name = 'name'
    _description = 'Lancer Routing Shape Item'

    name = fields.Char(string='形狀名稱')
    shape_code = fields.Char(string='形狀代碼')
    active = fields.Boolean(default=True, string='是否啟用')
    sequence = fields.Integer(required=True, default=10)

    def name_get(self):
        res = []
        for rec in self:
            name = rec.name
            if rec.shape_code:
                name = '[' + rec.shape_code + '] ' + name
            else:
                name = name
            res.append((rec.id, name))
        return res
