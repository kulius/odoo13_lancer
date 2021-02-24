# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import api, fields, models


class LancerRoutingOuter(models.Model):
    _name = 'lancer.routing.outer'
    _rec_name = 'name'
    _description = 'Lancer Routing Outer Item'

    name = fields.Char(string='外徑名稱')
    active = fields.Boolean(default=True, string='是否啟用')
    sequence = fields.Integer(required=True, default=10)
