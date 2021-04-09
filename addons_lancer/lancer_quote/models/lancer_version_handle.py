# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)

from odoo import api, fields, models, _


class LancerVersionHandle(models.Model):
    _name = 'lancer.version.handle'
    _rec_name = 'name'
    _description = '手柄射出 版次'

    def _get_handle_work_mould(self):
        return self.env['ir.config_parameter'].sudo().get_param('lancer_handle_work_mould')
    def _get_handle_work_make(self):
        return self.env['ir.config_parameter'].sudo().get_param('lancer_handle_work_make')
    def _get_handle_work_efficiency(self):
        return self.env['ir.config_parameter'].sudo().get_param('lancer_handle_work_efficiency')
    def _get_handle_work_yield(self):
        return self.env['ir.config_parameter'].sudo().get_param('lancer_handle_work_yield')

    @api.depends('handle_moldcost1', 'handle_moldcost2', 'handle_moldcost3', 'handle_moldcost4', 'handle_moldcost5', 'handle_moldcost6', 'handle_mandrel', 'handle_elecmandrel')
    def _handle_mold_total(self):
        price = self.handle_moldcost1 + self.handle_moldcost2 + self.handle_moldcost3 + self.handle_moldcost4 + self.handle_moldcost5 + self.handle_moldcost6 + self.handle_mandrel + self.handle_elecmandrel
        self.update({'handle_mold_total': price})

    #手柄射出-總成本計算
    @api.depends('handle_materialcost_ids', 'handle_mold_total')
    def _handle_work_sum(self):
        sum1 = sum([l.material_cost+l.process_price for l in self.handle_materialcost_ids])
        # sum2 = sum([l.process_price for l in self.handle_processcost_ids])
        sumcost = (sum1 + self.handle_work_make + self.handle_work_mould) / self.handle_work_efficiency / self.handle_work_yield
        # Math.Round(((txt_Matall.Text + txt_Proall.Text + txt_Cost03.Text + txt_Cost05.Text) / txt_Cost02.Text / txt_Cost04.Text), 3, MidpointRounding.AwayFromZero).ToString();
        self.update({'handle_work_sum': sumcost})

    name = fields.Char(string='版次編號', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    handle_series_id = fields.Many2one(comodel_name="lancer.routing.series", string="系列別", required=False, )
    handle_handle_id = fields.Many2one(comodel_name="lancer.routing.handle", string="手柄尺吋", required=False, )

    handle_materialcost_ids = fields.One2many(comodel_name="lancer.main.item.handlematerial",
                                              inverse_name="main_item_id", string="用料成本", required=False, )

    handle_moldcost1 = fields.Float(string="第一層射出", required=False, defalut="0")
    handle_moldcost2 = fields.Float(string="第二層射出", required=False, defalut="0")
    handle_moldcost3 = fields.Float(string="第三層射出", required=False, defalut="0")
    handle_moldcost4 = fields.Float(string="第四層射出", required=False, defalut="0")
    handle_moldcost5 = fields.Float(string="第五層射出", required=False, defalut="0")
    handle_moldcost6 = fields.Float(string="第六層射出", required=False, defalut="0")
    handle_mandrel = fields.Float(string="芯軸", required=False, defalut="0")
    handle_elecmandrel = fields.Float(string="電工芯軸", required=False, defalut="0")
    handle_mold_total = fields.Float(string='總模具費用', store=True, readonly=True, compute='_handle_mold_total')

    handle_work_make = fields.Float(string="製造費", required=False, default=_get_handle_work_make )
    handle_work_mould = fields.Float(string="模具分攤", required=False, default=_get_handle_work_mould)
    handle_work_efficiency = fields.Float(string="效率", required=False, default=_get_handle_work_efficiency)
    handle_work_yield = fields.Float(string="良率", required=False, default=_get_handle_work_yield)
    handle_work_sum = fields.Float(string="總成本", required=False, store=True, readonly=True, compute='_handle_work_sum')

    active = fields.Boolean(default=True, string='是否啟用')
    sequence = fields.Integer(required=True, default=10)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('lancer.version.handle') or _('New')

        result = super(LancerVersionHandle, self).create(vals)
        return result
