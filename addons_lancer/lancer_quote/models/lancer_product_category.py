# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import api, fields, models


class LancerProductCategory(models.Model):
    _name = 'lancer.product.category'
    _rec_name = 'name'
    _order = "sequence,id"
    _description = 'Lancer Product 產品分類'

    name = fields.Char(string='產品分類', translate=True)
    active = fields.Boolean(default=True, string='是否啟用')
    sequence = fields.Integer(required=True, default=10)

