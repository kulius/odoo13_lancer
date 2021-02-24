# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import api, fields, models


class LancerMainItemCategory(models.Model):
    _name = 'lancer.main.item.category'
    _rec_name = 'name'
    _description = 'Lancer Main Item Category'

    name = fields.Char(string='品項分類名稱')
    active = fields.Boolean(default=True, string='是否啟用')
    sequence = fields.Integer(required=True, default=10)
