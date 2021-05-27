# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import api, fields, models


class PaymentTerm(models.Model):
    _name = "payment.term"
    _description = "Payment Terms"
    _order = "sequence, id"
    _description = '報價單-付款條件'

    name = fields.Char(string='付款條件', translate=True, required=True)
    active = fields.Boolean(default=True, string='是否啟用')
    note = fields.Text(string='報表上的說明', translate=True)
    company_id = fields.Many2one('res.company', string='公司')
    sequence = fields.Integer(required=True, default=10)


