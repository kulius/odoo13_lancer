# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import api, fields, models


class LancerRoutingCutting(models.Model):
    _name = 'lancer.routing.cutting'
    _rec_name = 'name'
    _description = 'Lancer Routing Cutting Item'

    name = fields.Char(string='刃口名稱')
    cutting_code = fields.Char(string='刃口代碼')
    active = fields.Boolean(default=True, string='是否啟用')
    sequence = fields.Integer(required=True, default=10)

    def name_get(self):
        res = []
        for rec in self:
            name = rec.name
            if rec.cutting_code:
                name = '[' + rec.cutting_code + '] ' + name
            else:
                name = name
            res.append((rec.id, name))
        return res

    @api.model
    def create(self, values):
        # Add code here
        res = super(LancerRoutingCutting, self).create(values)
        vals = {
            'name': res.display_name,
            'type': 'e',
        }
        self.env['lancer.attr.records'].create(vals)
        return res

    def write(self, values):
        # Add code here
        origin_name = self.name
        origin_dis_name = self.display_name
        if values.get('name') != origin_name:
            res = super(LancerRoutingCutting, self).write(values)
            attrs_records = self.env['lancer.attr.records']
            records = attrs_records.search([('name', '=', origin_dis_name), ('type', '=', 'e')])
            if records:
                records.write({'name': self.display_name})
            else:
                vals = {
                    'name': self.display_name,
                    'type': 'e',
                }
                self.env['lancer.attr.records'].create(vals)
            return res
        else:
            return super(LancerRoutingCutting, self).write(values)
