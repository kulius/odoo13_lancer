# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import api, fields, models


class LancerAttrRecords(models.Model):
    _name = 'lancer.attr.records'
    _rec_name = 'name'
    _description = '用来收集特徵值的表'

    name = fields.Char(string='特徵值名')
    type = fields.Selection(string='類型',
                            selection=[('a', '手柄系列別'), ('b', '手柄尺寸'), ('c', '金屬形狀'), ('d', '金屬鍍層'), ('e', '金屬刃口'),
                                       ('f', '金屬外徑')], )

