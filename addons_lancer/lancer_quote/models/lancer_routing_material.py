# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import api, fields, models


class LancerRoutingMaterial(models.Model):
    _name = 'lancer.routing.material'
    _rec_name = 'name'
    _description = '組裝-材料名稱'

    name = fields.Char(string='組裝-材料名稱', translate=True)
    price = fields.Char(string='單價')
    active = fields.Boolean(default=True, string='是否啟用')
    sequence = fields.Integer(required=True, default=10)
