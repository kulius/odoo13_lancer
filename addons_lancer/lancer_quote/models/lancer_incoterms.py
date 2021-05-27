# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import fields, models


class LancerIncoterms(models.Model):
    _name = 'lancer.incoterms'
    _description = '報價單設定-貿易條件'

    name = fields.Char(string='貿易條件', required=True, translate=True)
    code = fields.Char(string='條件簡碼', size=3, required=True)
    active = fields.Boolean(string='是否啟用', default=True)
