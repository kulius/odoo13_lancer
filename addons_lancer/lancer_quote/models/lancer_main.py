# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import api, fields, models


class LancerMain(models.Model):
    _name = 'lancer.main'
    _rec_name = 'name'
    _order = "name, id"
    _description = 'Lancer main'

    name = fields.Char(string='主件品名規格')
    main_category_id = fields.Many2one(comodel_name="lancer.main.category", string="主件分類" )
    active = fields.Boolean(default=True, string='是否啟用')
