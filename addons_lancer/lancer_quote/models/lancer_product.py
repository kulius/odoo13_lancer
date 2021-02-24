# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import api, fields, models


class LancerProduct(models.Model):
    _name = 'lancer.product'
    _rec_name = 'name'
    _order = "product_code, id"
    _description = 'Lancer Product Item'

    name = fields.Char(string='產品名稱')
    product_code = fields.Char(string='產品品號')
    active = fields.Boolean(default=True, string='是否啟用')
    product_desc = fields.Text(string='產品描述')
