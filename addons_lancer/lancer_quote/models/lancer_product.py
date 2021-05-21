# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import api, fields, models


class LancerProduct(models.Model):
    _name = 'lancer.product'
    _rec_name = 'name'
    _order = "product_code, id"
    _description = 'Lancer Product Item'

    name = fields.Char(string='產品名稱', translate=True)
    product_code = fields.Char(string='產品品號')
    product_image = fields.Binary(string="產品圖片", attachment=True)
    product_series_id = fields.Many2one(comodel_name="lancer.routing.series", string="產品系列", required=False, )
    product_category_id = fields.Many2one(comodel_name="lancer.product.category", string="產品分類", required=False, )
    active = fields.Boolean(default=True, string='是否啟用')
    product_desc = fields.Text(string='產品描述', translate=True)

    product_line = fields.One2many('lancer.product.line', 'product_id')

class LancerProductLine(models.Model):
    _name = 'lancer.product.line'
    _order = 'id'
    _description = '產品主件明細'

    product_id = fields.Many2one('lancer.product', string='產品參考', index=True, required=True, readonly=True,
                               ondelete="cascade", copy=False)
    sequence = fields.Integer(string='Sequence', default=10)
    main_id = fields.Many2one('lancer.main', string='主件', index=True, ondelete="cascade", )
    material_cost = fields.Float(string='料', related='main_id.main_material_cost', store=True)
    process_cost = fields.Float(string='工', related='main_id.main_process_cost', store=True)
    manufacture_cost = fields.Float(string='費', related='main_id.main_manufacture_cost', store=True)
    total_cost = fields.Float(string='總價', related='main_id.main_total_cost', store=True)