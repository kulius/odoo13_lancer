# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import api, fields, models


class LancerRoutingCutting(models.Model):
    _name = 'lancer.routing.cutting'
    _rec_name = 'name'
    _description = 'Lancer Routing Cutting Item'

    name = fields.Char(string='刃口名稱')
    active = fields.Boolean(default=True, string='是否啟用')
    sequence = fields.Integer(required=True, default=10)
