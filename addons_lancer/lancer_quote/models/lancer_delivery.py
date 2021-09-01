# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import fields, models


class LancerDelivery(models.Model):
    _name = 'lancer.delivery'
    _description = '報價單設定-交貨條件'

    name = fields.Char(string='交貨條件', required=True)
    note = fields.Text(string='報價單中文說明', required=True)
    note_en = fields.Text(string='報價單英文說明', required=True)
    active = fields.Boolean(string='是否啟用', default=True)
