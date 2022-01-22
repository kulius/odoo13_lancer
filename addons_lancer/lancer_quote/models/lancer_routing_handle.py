# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import api, fields, models


class LancerRoutingHandle(models.Model):
    _name = 'lancer.routing.handle'
    _rec_name = 'name'
    _description = '手柄射出-手柄尺吋'

    name = fields.Char(string='手柄尺吋名稱', translate=True)
    handle_code = fields.Char(string='手柄尺吋代號')
    active = fields.Boolean(default=True, string='是否啟用')
    sequence = fields.Integer(required=True, default=10)

    # def name_get(self):
    #     res = []
    #     for rec in self:
    #         name = rec.name
    #         if rec.handle_code:
    #             name = '[' + rec.handle_code + '] ' + name
    #         else:
    #             name = name
    #         res.append((rec.id, name))
    #     return res

    @api.model
    def create(self, values):
        # Add code here
        res = super(LancerRoutingHandle, self).create(values)
        vals = {
            'name': res.display_name,
            'code': res.handle_code,
            'type': 'b',
            'origin_id': res.id,
        }
        self.env['lancer.attr.records'].create(vals)
        return res

    def write(self, values):

        res = super(LancerRoutingHandle, self).write(values)
        attrs_records = self.env['lancer.attr.records']
        records = attrs_records.search([('name', '=', self.name), ('type', '=', 'b')])
        if records:
            records.write({'name': self.name, 'code': self.handle_code})
        else:
            vals = {
                'name': self.name,
                'code': self.handle_code,
                'type': 'b',
                'origin_id': self.id,
            }
            self.env['lancer.attr.records'].create(vals)
        return res


    def action_rewrite(self):
        for record in self.browse(self.env.context['active_ids']):
            record.write({'name': record.name})