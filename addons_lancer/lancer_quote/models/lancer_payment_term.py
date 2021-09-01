# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import api, fields, models


class LancerPaymentTerm(models.Model):
    _name = "lancer.payment.term"
    _description = "Payment Terms"
    _order = "sequence, id"
    _description = '報價單-付款條件'

    name = fields.Char(string='付款條件', required=True)
    active = fields.Boolean(default=True, string='是否啟用')
    note = fields.Text(string='報價單中文說明', required=True)
    note_en = fields.Text(string='報價單英文說明', required=True)
    sequence = fields.Integer(required=True, default=10)


