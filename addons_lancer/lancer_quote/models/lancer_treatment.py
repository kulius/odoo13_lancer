# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import api, fields, models


class LancerSubcontractTreatment(models.Model):
    _name = 'lancer.subcontract.treatment'
    _rec_name = 'name'
    _order = "sequence, id"
    _description = '外購-表面處理'

    name = fields.Char(string='表面處理名稱')
    active = fields.Boolean(default=True, string='是否啟用')
    sequence = fields.Integer(required=True, default=10)
