# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import api, fields, models


class LancerHandleMaterialProcess(models.Model):
    _name = 'lancer.handlematerial.process'
    _rec_name = 'name'
    _description = 'Lancer Main Item Handle Material use process'

    name = fields.Char(string='加工工序名稱')
    active = fields.Boolean(default=True, string='是否啟用')
    sequence = fields.Integer(required=True, default=10)
