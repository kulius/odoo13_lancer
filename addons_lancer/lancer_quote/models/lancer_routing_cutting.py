# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import api, fields, models


class LancerRoutingCutting(models.Model):
    _name = 'lancer.routing.cutting'
    _rec_name = 'name'
    _description = 'Lancer Routing Cutting Item'

    name = fields.Char(string='刃口名稱')
    cutting_code = fields.Char(string='刃口代碼')
    active = fields.Boolean(default=True, string='是否啟用')
    sequence = fields.Integer(required=True, default=10)

    def name_get(self):
        res = []
        for rec in self:
            name = rec.name
            if rec.cutting_code:
                name = '[' + rec.cutting_code + '] ' + name
            else:
                name = name
            res.append((rec.id, name))
        return res
