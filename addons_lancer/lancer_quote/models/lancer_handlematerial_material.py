# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import api, fields, models


class LancerHandleMaterialMaterial(models.Model):
    _name = 'lancer.handlematerial.material'
    _rec_name = 'name'
    _description = 'Lancer Main Item Handle Material use Material'

    name = fields.Char(string='材質名稱')
    active = fields.Boolean(default=True, string='是否啟用')
    sequence = fields.Integer(required=True, default=10)
