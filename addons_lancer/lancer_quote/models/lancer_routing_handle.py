# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import api, fields, models


class LancerRoutingHandle(models.Model):
    _name = 'lancer.routing.handle'
    _rec_name = 'name'
    _description = 'Lancer Routing Handle Item'

    name = fields.Char(string='手柄尺吋名稱')
    handle_code = fields.Char(string='手柄尺吋代號')
    active = fields.Boolean(default=True, string='是否啟用')
    sequence = fields.Integer(required=True, default=10)

    def name_get(self):
        res = []
        for rec in self:
            name = rec.name
            if rec.handle_code:
                name = '[' + rec.handle_code + '] ' + name
            else:
                name = name
            res.append((rec.id, name))
        return res

    @api.model
    def create(self, values):
        # Add code here
        res = super(LancerRoutingHandle, self).create(values)
        vals = {
            'name': res.display_name,
            'type': 'b',
        }
        self.env['lancer.attr.records'].create(vals)
        return res

    def write(self, values):
        # Add code here
        origin_name = self.name
        origin_dis_name = self.display_name
        if values.get('name') != origin_name:
            res = super(LancerRoutingHandle, self).write(values)
            attrs_records = self.env['lancer.attr.records']
            records = attrs_records.search([('name', '=', origin_dis_name), ('type', '=', 'b')])
            if records:
                records.write({'name': self.display_name})
            else:
                vals = {
                    'name': self.display_name,
                    'type': 'b',
                }
                self.env['lancer.attr.records'].create(vals)
            return res
        else:

            return super(LancerRoutingHandle, self).write(values)
