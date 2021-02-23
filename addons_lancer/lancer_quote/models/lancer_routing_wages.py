# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import api, fields, models


class LancerRoutingWages(models.Model):
    _name = 'lancer.routing.wages'
    _rec_name = 'name'
    _description = 'Lancer Routing Wages Item'

    name = fields.Char(string='組裝-工資項目名稱')
    active = fields.Boolean(default=True, string='是否啟用')
    sequence = fields.Integer(required=True, default=10)
