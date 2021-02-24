# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import api, fields, models


class LancerMainCategory(models.Model):
    _name = 'lancer.main.category'
    _rec_name = 'name'
    _description = 'Lancer Main Parts Category Item'

    name = fields.Char(string='主件分類名稱')
    active = fields.Boolean(default=True, string='是否啟用')
    sequence = fields.Integer(required=True, default=10)
