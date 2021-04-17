# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import api, fields, models


class LancerRoutingShape(models.Model):
    _name = 'lancer.routing.shape'
    _rec_name = 'name'
    _description = 'Lancer Routing Shape Item'

    name = fields.Char(string='形狀名稱')
    shape_code = fields.Char(string='形狀代碼')
    active = fields.Boolean(default=True, string='是否啟用')
    sequence = fields.Integer(required=True, default=10)

    def name_get(self):
        res = []
        for rec in self:
            name = rec.name
            if rec.shape_code:
                name = '[' + rec.shape_code + '] ' + name
            else:
                name = name
            res.append((rec.id, name))
        return res

    @api.model
    def create(self, values):
        # Add code here
        res = super(LancerRoutingShape, self).create(values)
        vals = {
            'name': res.display_name,
            'type': 'c',
        }
        self.env['lancer.attr.records'].create(vals)
        return res

    def write(self, values):
        # Add code here
        origin_name = self.name
        origin_dis_name = self.display_name
        if values.get('name') != origin_name:
            res = super(LancerRoutingShape, self).write(values)
            attrs_records = self.env['lancer.attr.records']
            records = attrs_records.search([('name', '=', origin_dis_name), ('type', '=', 'c')])
            if records:
                records.write({'name': self.display_name})
            else:
                vals = {
                    'name': self.display_name,
                    'type': 'c',
                }
                self.env['lancer.attr.records'].create(vals)
            return res
        else:

            return super(LancerRoutingShape, self).write(values)
