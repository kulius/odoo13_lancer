# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import api, fields, models


class LancerRoutingHandle(models.Model):
    _name = 'lancer.routing.handle'
    _rec_name = 'name'
    _description = 'Lancer Routing Handle Item'

    name = fields.Char(string='手柄尺吋名稱')
    handle_code = fields.Char(string='手柄尺吋代號')
    active = fields.Boolean(default=True, string='是否啟用')
    sequence = fields.Integer(required=True, default=10)

    def name_get(self):
        res = []
        for rec in self:
            name = rec.name
            if rec.handle_code:
                name = '[' + rec.handle_code + '] ' + name
            else:
                name = name
            res.append((rec.id, name))
        return res
