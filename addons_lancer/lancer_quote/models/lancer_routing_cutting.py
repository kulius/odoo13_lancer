# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import api, fields, models


class LancerRoutingCutting(models.Model):
    _name = 'lancer.routing.cutting'
    _rec_name = 'name'
    _description = 'Lancer Routing Cutting Item'

    name = fields.Char(string='刃口名稱', translate=True)
    ename = fields.Char(string='Tip Style')
    cutting_code = fields.Char(string='刃口代碼')
    active = fields.Boolean(default=True, string='是否啟用')
    sequence = fields.Integer(required=True, default=10)

    # def name_get(self):
    #     res = []
    #     for rec in self:
    #         name = rec.name
    #         if rec.cutting_code:
    #             name = '[' + rec.cutting_code + '] ' + name
    #         else:
    #             name = name
    #         res.append((rec.id, name))
    #     return res

    @api.model
    def create(self, values):
        # Add code here
        res = super(LancerRoutingCutting, self).create(values)
        vals = {
            'name': res.display_name,
            'code': res.cutting_code,
            'type': 'e',
        }
        self.env['lancer.attr.records'].create(vals)
        return res

    def write(self, values):
        # Add code here
        res = super(LancerRoutingCutting, self).write(values)
        attrs_records = self.env['lancer.attr.records']
        records = attrs_records.search([('name', '=', self.name), ('type', '=', 'e')])
        if records:
            records.write({'name': self.name, 'code': self.cutting_code})
        else:
            vals = {
                'name': self.name,
                'code': self.cutting_code,
                'type': 'e',
            }
            self.env['lancer.attr.records'].create(vals)
        return res
        # else:
        #     return super(LancerRoutingCutting, self).write(values)

    def action_rewrite(self):
        for record in self.browse(self.env.context['active_ids']):
            record.write({'name': record.name})