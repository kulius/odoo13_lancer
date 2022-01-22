# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import api, fields, models


class LancerAttrRecords(models.Model):
    _name = 'lancer.attr.records'
    _rec_name = 'name'
    _description = '用来收集特徵值的表'

    name = fields.Char(string='特徵值名')
    ename = fields.Char(string='英文名稱')
    code = fields.Char(string='代碼')
    origin_id = fields.Char(string='來源id')
    type = fields.Selection(string='類型',
                            selection=[('a', '手柄系列別'), ('b', '手柄尺寸'), ('c', '金屬形狀'), ('d', '金屬鍍層'), ('e', '金屬刃口'),
                                       ('f', '金屬外徑')], )


    def action_rewrite(self):
        attr = self.env['lancer.attr.records'].search([])
        attr.unlink()

        #金屬加工-形狀
        recs = self.env['lancer.routing.shape'].search([])
        for rec in recs:
            vals = {
                'name': rec.name,
                'code': rec.shape_code,
                'type': 'c',
                'origin_id': rec.id,
            }
            self.env['lancer.attr.records'].create(vals)

        # 金屬加工-刃口
        recs = self.env['lancer.routing.cutting'].search([])
        for rec in recs:
            vals = {
                'name': rec.name,
                'code': rec.cutting_code,
                'type': 'e',
                'origin_id': rec.id,
            }
            self.env['lancer.attr.records'].create(vals)

        # 手柄射出-手柄尺吋
        recs = self.env['lancer.routing.handle'].search([])
        for rec in recs:
            vals = {
                'name': rec.name,
                'code': rec.handle_code,
                'type': 'b',
                'origin_id': rec.id,
            }
            self.env['lancer.attr.records'].create(vals)

        # 金屬加工-鋼刄外徑
        recs = self.env['lancer.routing.outer'].search([])
        for rec in recs:
            vals = {
                'name': rec.name,
                'code': rec.outer_code,
                'type': 'f',
                'origin_id': rec.id,
            }
            self.env['lancer.attr.records'].create(vals)

        # 主件-系列別
        recs = self.env['lancer.routing.series'].search([])
        for rec in recs:
            vals = {
                'name': rec.name,
                'code': rec.series_code,
                'type': 'a',
                'origin_id': rec.id,
            }
            self.env['lancer.attr.records'].create(vals)

        # 金屬加工-鍍層
        recs = self.env['lancer.routing.coating'].search([])
        for rec in recs:
            vals = {
                'name': rec.name,
                'code': rec.coating_code,
                'type': 'd',
                'origin_id': rec.id,
            }
            self.env['lancer.attr.records'].create(vals)


