# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import api, fields, models


class LancerMain(models.Model):
    _name = 'lancer.main'
    _rec_name = 'name'
    _order = "name, id"
    _description = 'Lancer main'

    @api.depends('main_material_cost', 'main_process_cost', 'main_manufacture_cost')
    def _main_amount_all(self):
        """
            Compute the amounts by the Material_Cost、Process_Cost、Manufacture_Cost.
        """
        price = self.main_material_cost + self.main_process_cost + self.main_manufacture_cost
        self.update({'main_total_cost': price})

    @api.depends('main_item_ids.material_cost')
    def _amount_all(self):
        """
        Compute the total material amounts.
        """

        for order in self:
            main_material_cost = main_process_cost = main_manufacture_cost = 0.0
            for line in order.main_item_ids:
                main_material_cost += line.material_cost
                main_process_cost += line.process_cost
                main_manufacture_cost += line.manufacture_cost
            order.update({
                'main_material_cost': main_material_cost,
                'main_process_cost': main_process_cost,
                'main_manufacture_cost': main_manufacture_cost,
            })

    name = fields.Char(string='主件品名規格')
    main_category_id = fields.Many2one(comodel_name="lancer.main.category", string="主件分類")
    active = fields.Boolean(default=True, string='是否啟用')
    main_material_cost = fields.Float(string='料', store=True, readonly=True, compute='_amount_all')
    main_process_cost = fields.Float(string='工', store=True, readonly=True, compute='_amount_all')
    main_manufacture_cost = fields.Float(string='費', store=True, readonly=True, compute='_amount_all')
    main_total_cost = fields.Float(string='總價', store=True, readonly=True, compute='_main_amount_all')
    main_item_ids = fields.One2many(comodel_name='lancer.main.item', inverse_name='main_id', string='品項')


