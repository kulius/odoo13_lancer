# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import fields, models


class LancerIncoterms(models.Model):
    _name = 'lancer.incoterms'
    _description = '報價單設定-貿易條件'

    name = fields.Char(string='貿易條件', required=True)
    note = fields.Text(string='報價單中文說明', required=True)
    note_en = fields.Text(string='報價單英文說明', required=True)
    code = fields.Char(string='條件簡碼', size=3, required=False)
    active = fields.Boolean(string='是否啟用', default=True)
