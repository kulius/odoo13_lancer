# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import api, fields, models


class LancerRoutingCoating(models.Model):
    _name = 'lancer.routing.coating'
    _rec_name = 'name'
    _description = 'Lancer Routing Coating Item'

    name = fields.Char(string='鍍層名稱')
    active = fields.Boolean(default=True, string='是否啟用')
    sequence = fields.Integer(required=True, default=10)
