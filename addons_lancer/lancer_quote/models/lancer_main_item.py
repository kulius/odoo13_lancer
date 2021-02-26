# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import api, fields, models


class LancerMainItem(models.Model):
    _name = 'lancer.main.item'
    _rec_name = 'name'
    _order = "name, id"
    _description = 'Lancer main Item'

    active = fields.Boolean(default=True, string='是否啟用')
    name = fields.Char(string='品項品名規格')
    main_id = fields.Many2one(comodel_name="lancer.main", string="所屬主件", required=True, )
    main_item_category_id = fields.Many2one(comodel_name="lancer.main.item.category", string="品項分類", required=True, )

    item_routing = fields.Selection(string="加工製程段", selection=[('metal', '金屬加工'), ('handle', '手柄射出'), ('assembly', '組裝')], required=True, )
    steel_blade = fields.Boolean(string="加工鋼刃",  )
    routing_shape_id = fields.Many2one(comodel_name="lancer.routing.shape", string="形狀", required=True, )
    routing_coating_id = fields.Many2one(comodel_name="lancer.routing.coating", string="鍍層", required=True, )
    routing_cutting_id = fields.Many2one(comodel_name="lancer.routing.cutting", string="刃口", required=True, )
    routing_outer_id = fields.Many2one(comodel_name="lancer.routing.outer", string="外徑", required=True, )

    steel_type = fields.Char(string="鋼材規格", required=False, )
    steel_spec = fields.Char(string="鋼材種類", required=False, )
    steel_long = fields.Char(string="物料長(mm)", required=False, )
    steel_cutting_long = fields.Char(string="下料長度(mm)", required=False, )
    steel_cut = fields.Char(string="切料節數", required=False, )
    steel_weight = fields.Char(string="鋼刃單隻重量", required=False, )
    steel_material = fields.Char(string="材料(元/KG)", required=False, )
    steel_price = fields.Char(string="單隻價格", required=False, )


