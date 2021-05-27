# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import api, fields, models


class LancerRoutingCoating(models.Model):
    _name = 'lancer.routing.coating'
    _rec_name = 'name'
    _description = '金屬加工-鍍層'

    name = fields.Char(string='鍍層名稱', translate=True)
    ename = fields.Char(string='COATING')
    coating_code = fields.Char(string='鍍層代碼')
    active = fields.Boolean(default=True, string='是否啟用')
    sequence = fields.Integer(required=True, default=10)

    # def name_get(self):
    #     res = []
    #     for rec in self:
    #         name = rec.name
    #         if rec.coating_code:
    #             name = '[' + rec.coating_code + '] ' + name
    #         else:
    #             name = name
    #         res.append((rec.id, name))
    #     return res

    @api.model
    def create(self, values):
        # Add code here
        res = super(LancerRoutingCoating, self).create(values)
        vals = {
            'name': res.name,
            'code': res.coating_code,
            'type': 'd',
        }
        self.env['lancer.attr.records'].create(vals)
        return res

    def write(self, values):
        res = super(LancerRoutingCoating, self).write(values)
        attrs_records = self.env['lancer.attr.records']
        records = attrs_records.search([('name', '=', self.name), ('type', '=', 'd')])
        if records:
            records.write({'name': self.name, 'code': self.coating_code})
        else:
            vals = {
                'name': self.name,
                'code': self.coating_code,
                'type': 'd',
            }
            self.env['lancer.attr.records'].create(vals)
        return res


    def action_rewrite(self):
        for record in self.browse(self.env.context['active_ids']):
            record.write({'name': record.name})