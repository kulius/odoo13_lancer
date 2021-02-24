# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import api, fields, models


class LancerRoutingSeries(models.Model):
    _name = 'lancer.routing.series'
    _rec_name = 'name'
    _description = 'Lancer Routing Series Item'

    name = fields.Char(string='系列別名稱')
    active = fields.Boolean(default=True, string='是否啟用')
    sequence = fields.Integer(required=True, default=10)
