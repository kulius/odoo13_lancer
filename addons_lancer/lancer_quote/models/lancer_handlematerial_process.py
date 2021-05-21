# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import api, fields, models


class LancerHandleMaterialProcess(models.Model):
    _name = 'lancer.handlematerial.process'
    _rec_name = 'name'
    _description = 'Lancer Main Item Handle Material use process'

    name = fields.Char(string='手柄工序說明')
    process_code = fields.Char(string='手柄工序代號')
    active = fields.Boolean(default=True, string='是否啟用')
    sequence = fields.Integer(required=True, default=10)

    # def name_get(self):
    #     res = []
    #     for rec in self:
    #         name = rec.name
    #         if rec.process_code:
    #             name = '[' + rec.process_code + '] ' + name
    #         else:
    #             name = name
    #         res.append((rec.id, name))
    #     return res
