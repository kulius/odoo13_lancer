# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import api, fields, models


class LancerRoutingSeries(models.Model):
    _name = 'lancer.routing.series'
    _rec_name = 'name'
    _description = 'Lancer Routing Series Item'

    name = fields.Char(string='系列別名稱')
    series_code = fields.Char(string='系列別代號')
    active = fields.Boolean(default=True, string='是否啟用')
    sequence = fields.Integer(required=True, default=10)

    def name_get(self):
        res = []
        for rec in self:
            name = rec.name
            if rec.series_code:
                name = '[' + rec.series_code + '] ' + name
            else:
                name = name
            res.append((rec.id, name))
        return res
