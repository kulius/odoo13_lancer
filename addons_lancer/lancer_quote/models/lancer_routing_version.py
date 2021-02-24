# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import api, fields, models


class LancerRoutingVersion(models.Model):
    _name = 'lancer.routing.version'
    _rec_name = 'name'
    _description = 'Lancer Routing Version Item'

    name = fields.Char(string='版本版次名稱')
    active = fields.Boolean(default=True, string='是否啟用')
    sequence = fields.Integer(required=True, default=10)
