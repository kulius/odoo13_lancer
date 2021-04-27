# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import api, fields, models


class LancerPackageSetting(models.Model):
    _name = 'lancer.package.setting'
    _rec_name = 'name'
    _order = "sequence, id"
    _description = 'Lancer Package Setting Item'

    name = fields.Char(string='包裝材料名稱', translate=True)
    active = fields.Boolean(default=True, string='是否啟用')
    sequence = fields.Integer(required=True, default=10)
