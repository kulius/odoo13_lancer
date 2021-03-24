# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import fields, models, api
from odoo.exceptions import ValidationError


class EditNodeActionWizard(models.TransientModel):
    _name = 'edit.node.action.wizard'
    _description = u'编辑动作向导'

    condition = fields.Char('条件')


    @api.model
    def default_get(self, fields_list):
        res = super(EditNodeActionWizard, self.sudo()).default_get(fields_list)

        if self._context.get('node_action_id'):
            node_action = self.env['approval.flow.node.action'].browse(self._context['node_action_id'])
            res['condition'] = node_action.condition

        return res




    def button_ok(self):
        self.ensure_one()
        self.env['approval.flow.node.action'].browse(self._context['node_action_id']).condition = self.condition

        return {
            'action': {
                'id': self._context['node_action_id'],
                'condition': self.condition or '',
            },

        }
