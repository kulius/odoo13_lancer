# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import api, fields, models


class LancerRoutingOuter(models.Model):
    _name = 'lancer.routing.outer'
    _rec_name = 'name'
    _description = 'Lancer Routing Outer Item'

    name = fields.Char(string='鋼刄外徑名稱', translate=True)
    outer_code = fields.Char(string='鋼刄外徑代碼')

    outer_size = fields.Float(string='鋼刄外徑')
    outer_rate = fields.Float(string='換算率', digits=(1, 5))
    outer_dye_blackhead_price = fields.Float(string='染黑頭單價')

    active = fields.Boolean(default=True, string='是否啟用')
    sequence = fields.Integer(required=True, default=10)

    def name_get(self):
        res = []
        for rec in self:
            name = rec.name
            if rec.outer_code:
                name = '[' + rec.outer_code + '] ' + name
            else:
                name = name
            res.append((rec.id, name))
        return res

    @api.model
    def create(self, values):
        # Add code here
        res = super(LancerRoutingOuter, self).create(values)
        vals = {
            'name': res.name,
            'code': res.outer_code,
            'type': 'f',
        }
        self.env['lancer.attr.records'].create(vals)
        return res

    def write(self, values):
        res = super(LancerRoutingOuter, self).write(values)
        attrs_records = self.env['lancer.attr.records']
        records = attrs_records.search([('name', '=', self.name), ('type', '=', 'f')])
        if records:
            records.write({'name': self.name, 'code': self.outer_code})
        else:
            vals = {
                'name': self.name,
                'code': self.outer_code,
                'type': 'f',
            }
            self.env['lancer.attr.records'].create(vals)
        return res

    def action_rewrite(self):
        for record in self.browse(self.env.context['active_ids']):
            record.write({'name': record.name})