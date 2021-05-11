# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import api, fields, models


class LancerMainCategory(models.Model):
    _name = 'lancer.main.category'
    _rec_name = 'name'
    _description = 'Lancer Main Parts Category Item'

    name = fields.Char(string='主件分類名稱', translate=True)
    main_categ_code = fields.Char(string='主件分類代碼')
    active = fields.Boolean(default=True, string='是否啟用')
    sequence = fields.Integer(required=True, default=10)

    # def name_get(self):
    #     res = []
    #     for rec in self:
    #         name = rec.name
    #         if rec.main_categ_code:
    #             name = '[' + rec.main_categ_code + '] ' + name
    #         else:
    #             name = name
    #         res.append((rec.id, name))
    #     return res
