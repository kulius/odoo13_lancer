# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import api, fields, models


class LancerMain(models.Model):
    _name = 'lancer.main'
    _rec_name = 'name'
    _order = "name, id"
    _description = '主件'

    @api.depends('main_material_cost', 'main_process_cost', 'main_manufacture_cost')
    def _main_amount_all(self):
        price = self.main_material_cost + self.main_process_cost + self.main_manufacture_cost
        self.update({'main_total_cost': price})

    @api.depends('order_line.material_cost')
    def _amount_all(self):
        for order in self:
            main_material_cost = main_process_cost = main_manufacture_cost = 0.0
            for line in order.order_line:
                main_material_cost += line.material_cost
                main_process_cost += line.process_cost
                main_manufacture_cost += line.manufacture_cost
            order.update({
                'main_material_cost': main_material_cost,
                'main_process_cost': main_process_cost,
                'main_manufacture_cost': main_manufacture_cost,
            })

    #將品項明細中的特徵值集合呈現
    @api.depends('order_line')
    def _compute_attrs_record(self):
        self.update({'main_attrs_ids': None})
        if self.order_line:
            attrs_ids = []
            for rec in self.order_line:
                for x in rec.item_attrs_ids:
                    attrs_ids.append(x.id)
            self.update({'main_attrs_ids': [(6, 0, attrs_ids)]})

    name = fields.Char(string='主件品名規格')
    main_category_id = fields.Many2one(comodel_name="lancer.main.category", string="主件分類")
    product_series_id = fields.Many2one(comodel_name="lancer.routing.series", string="產品系列", required=False, )
    product_category_id = fields.Many2one(comodel_name="lancer.product.category", string="產品分類", required=False, )
    active = fields.Boolean(default=True, string='是否啟用')
    main_material_cost = fields.Float(string='料', store=True, readonly=True, compute='_amount_all')
    main_process_cost = fields.Float(string='工', store=True, readonly=True, compute='_amount_all')
    main_manufacture_cost = fields.Float(string='費', store=True, readonly=True, compute='_amount_all')
    main_total_cost = fields.Float(string='總價', store=True, readonly=True, compute='_main_amount_all')
    # main_item_ids = fields.One2many(comodel_name='lancer.main.item', inverse_name='main_id', string='品項')
    order_line = fields.One2many('lancer.main.order.line', 'order_id')
    main_attrs_ids = fields.Many2many('lancer.attr.records', string='特徵值集合', compute='_compute_attrs_record')
    packing_inbox = fields.Integer(string='內盒', required=False)
    packing_outbox = fields.Integer(string='外箱', required=False)
    packing_net_weight = fields.Float(string='淨重', required=False)
    packing_gross_weight = fields.Float(string='毛重', required=False)
    packing_bulk = fields.Float(string='材積', required=False)



class LancerMainOrderLine(models.Model):
    _name = 'lancer.main.order.line'
    _order = 'id'
    _description = '主件-品項明細'

    order_id = fields.Many2one('lancer.main', string='主件參考', index=True, required=True, readonly=True,
                               ondelete="cascade", copy=False)
    sequence = fields.Integer(string='Sequence', default=10)
    main_item_id = fields.Many2one('lancer.main.item', string='品項品名規格', index=True, ondelete="cascade", )
    material_cost = fields.Float(string='料', related='main_item_id.material_cost', store=True)
    process_cost = fields.Float(string='工', related='main_item_id.process_cost', store=True)
    manufacture_cost = fields.Float(string='費', related='main_item_id.manufacture_cost', store=True)
    item_total_cost = fields.Float(string='總價', related='main_item_id.item_total_cost', store=True)
    item_attrs_ids = fields.Many2many('lancer.attr.records', string='特徵值集合')
    handle_attrs_record = fields.Many2one('lancer.handle.attrs.record', string='手抦材質')


    @api.onchange('main_item_id')
    def set_attrs_data(self):
        if not self.main_item_id:
            return
        if self.main_item_id.item_routing == 'metal':
            attr_ids = []
            for rec in self:
                shape_name = self.env['lancer.attr.records'].search(
                    [('name', '=', rec.main_item_id.metal_shape_id.name), ('type', '=', 'c')])
                if shape_name:
                    attr_ids.append(shape_name.id)
                coating_name = self.env['lancer.attr.records'].search(
                    [('name', '=', rec.main_item_id.metal_coating_id.name), ('type', '=', 'd')])
                if coating_name:
                    attr_ids.append(coating_name.id)
                cutting_name = self.env['lancer.attr.records'].search(
                    [('name', '=', rec.main_item_id.metal_cutting_id.name), ('type', '=', 'e')])
                if cutting_name:
                    attr_ids.append(cutting_name.id)
                outer_name = self.env['lancer.attr.records'].search(
                    [('name', '=', rec.main_item_id.metal_outer_id.name), ('type', '=', 'f')])
                if outer_name:
                    attr_ids.append(outer_name.id)
            self.item_attrs_ids = [(6, False, attr_ids)]
            self.handle_attrs_record = self.main_item_id.handle_attrs_id.id
            return {'domain':{'item_attrs_ids':[('type','in', ['c', 'd', 'e', 'f'])]}}
        else:
            attr_ids = []
            for rec in self:
                series_name = self.env['lancer.attr.records'].search(
                    [('name', '=', rec.main_item_id.handle_series_id.name), ('type', '=', 'a')])
                if series_name:
                    attr_ids.append(series_name.id)
                handle_name = self.env['lancer.attr.records'].search(
                    [('name', '=', rec.main_item_id.handle_handle_id.name), ('type', '=', 'b')])
                if handle_name:
                    attr_ids.append(handle_name.id)
            self.item_attrs_ids = [(6, False, attr_ids)]
            self.handle_attrs_record = self.main_item_id.handle_attrs_id.id
            return {'domain': {'item_attrs_ids': [('type', 'in', ['a', 'b',])]}}
