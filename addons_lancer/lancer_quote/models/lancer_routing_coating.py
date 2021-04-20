# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import api, fields, models


class LancerRoutingCoating(models.Model):
    _name = 'lancer.routing.coating'
    _rec_name = 'name'
    _description = 'Lancer Routing Coating Item'

    name = fields.Char(string='鍍層名稱')
    coating_code = fields.Char(string='鍍層代碼')
    active = fields.Boolean(default=True, string='是否啟用')
    sequence = fields.Integer(required=True, default=10)

    def name_get(self):
        res = []
        for rec in self:
            name = rec.name
            if rec.coating_code:
                name = '[' + rec.coating_code + '] ' + name
            else:
                name = name
            res.append((rec.id, name))
        return res

    @api.model
    def create(self, values):
        # Add code here
        res = super(LancerRoutingCoating, self).create(values)
        vals = {
            'name': res.display_name,
            'type': 'd',
        }
        self.env['lancer.attr.records'].create(vals)
        return res

    def write(self, values):
        # Add code here
        origin_name = self.name
        origin_dis_name = self.display_name
        # if values.get('name') != origin_name:
        res = super(LancerRoutingCoating, self).write(values)
        attrs_records = self.env['lancer.attr.records']
        records = attrs_records.search([('name', '=', origin_dis_name), ('type', '=', 'd')])
        if records:
            records.write({'name': self.display_name})
        else:
            vals = {
                'name': self.display_name,
                'type': 'd',
            }
            self.env['lancer.attr.records'].create(vals)
        return res
        # else:
        #
        #     return super(LancerRoutingCoating, self).write(values)

    def action_rewrite(self):
        for record in self.browse(self.env.context['active_ids']):
            record.write({'name': record.name})