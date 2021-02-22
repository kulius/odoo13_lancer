# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import api, fields, models


class LancerSubcontractCategory(models.Model):
    _name = 'lancer.subcontract.category'
    _rec_name = 'name'
    _order = "sequence, id"
    _description = 'Lancer Subcontract Product Category'

    name = fields.Char(string='類別名稱')
    active = fields.Boolean(default=True, string='是否啟用')
    sequence = fields.Integer(required=True, default=10)
