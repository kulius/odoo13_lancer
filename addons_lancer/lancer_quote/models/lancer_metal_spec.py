# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import api, fields, models


class LanceMetalSpec(models.Model):
    _name = 'lancer.metal.spec'
    _rec_name = 'name'
    _description = 'Lancer Metal Spec for Main Item Use'

    name = fields.Char(string='鋼材種類名稱')
    active = fields.Boolean(default=True, string='是否啟用')
    sequence = fields.Integer(required=True, default=10)