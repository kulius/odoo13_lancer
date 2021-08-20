# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import api, fields, models


class LancerSubcontractCategory(models.Model):
    _name = 'lancer.subcontract.category'
    _rec_name = 'name'
    _order = "sequence, id"
    _description = '外購-外購品名維護'

    name = fields.Char(string='類別名稱')
    active = fields.Boolean(default=True, string='是否啟用')
    sequence = fields.Integer(required=True, default=10)

    partner_id = fields.Many2one(comodel_name="res.partner", string="廠商", required=False)
    name = fields.Char(string="品名", required=False, )
    spec = fields.Char(string="規格", required=False, )
    partno = fields.Char(string="參考料號", required=False, )
    material_id = fields.Many2one(comodel_name="lancer.subcontract.material", string="材質", required=False, )
    treatment_id = fields.Many2one(comodel_name="lancer.subcontract.treatment", string="表面處理", required=False, )
    handle_amount = fields.Float(string="柄價", required=False, )
    subcontract_amount = fields.Float(string="單價", required=False, )
    build_amount = fields.Float(string="組工", required=False, )
    cost_amount = fields.Float(string="成本", required=False, compute='_compute_cost_amount', store=True )
    mould_amount = fields.Float(string="模具費用", required=False, )

    @api.depends('handle_amount', 'subcontract_amount', 'build_amount')
    def _compute_cost_amount(self):
        for data in self:
            data.cost_amount = data.handle_amount + data.subcontract_amount + data.build_amount