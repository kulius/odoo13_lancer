# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import api, fields, models


class LancerPackageSetting(models.Model):
    _name = 'lancer.package.setting'
    _rec_name = 'name'
    _order = "sequence, id"
    _description = '報價單-包裝材料'

    code = fields.Char(string='代號', translate=True)
    name = fields.Char(string='包裝材料名稱', translate=True)
    package_type_id = fields.Many2one(comodel_name="lancer.package.type", string="包裝大分類", required=False, )
    active = fields.Boolean(default=True, string='是否啟用')
    sequence = fields.Integer(required=True, default=10)

    def name_get(self):
        res = []
        for rec in self:
            name = rec.name
            if rec.code:
                name = '[' + rec.code + '] ' + name
            else:
                name = name
            res.append((rec.id, name))
        return res


class LancerProductPackage(models.Model):
    _name = 'lancer.product.package'
    _rec_name = 'name'
    _order = "sequence, id"
    _description = '報價單-包装'

    name = fields.Char(string='包裝材料名稱', translate=True)
    active = fields.Boolean(default=True, string='是否啟用')
    sequence = fields.Integer(required=True, default=10)
