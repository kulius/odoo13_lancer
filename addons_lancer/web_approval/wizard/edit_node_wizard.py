# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import fields, models, api
from odoo.exceptions import ValidationError


class EditNodeWizard(models.TransientModel):
    _name = 'edit.node.wizard'
    _description = u'编辑动作向导'

    name = fields.Char('名称')
    groups_id = fields.Many2one('res.groups', '节点执行组')
    is_all_approval = fields.Boolean('需全组审批', default=False)
    only_document_company = fields.Boolean('仅单据公司', default=True)

    duration = fields.Integer('审批时效', default=0)
    allow_before_increase = fields.Boolean('允许前加签', default=False)
    allow_after_increase = fields.Boolean('允许后加签', default=False)
    allow_turn_to = fields.Boolean('允许转签', default=False)


    @api.model
    def default_get(self, fields_list):
        res = super(EditNodeWizard, self.sudo()).default_get(fields_list)

        if self._context.get('node_id'):
            node = self.env['approval.flow.node'].browse(self._context['node_id'])
            res.update({
                'name': node.name,
                'groups_id': node.groups_id.id,
                'is_all_approval': node.is_all_approval,
                'only_document_company': node.only_document_company,
            })

        return res




    def button_ok(self):
        self.ensure_one()

        if self._context.get('type') == 'edit':
            self.env['approval.flow.node'].browse(self._context['node_id']).write({
                'name': self.name,
                'groups_id': self.groups_id.id,
                'is_all_approval': self.is_all_approval,
                'only_document_company': self.only_document_company,
            })
            node_id = self._context['node_id']
        else:
            node = self.env['approval.flow.node'].create({
                'name': self.name,
                'groups_id': self.groups_id.id,
                'is_all_approval': self.is_all_approval,
                'only_document_company': self.only_document_company,
                'flow_id': self._context['flow_id']
            })
            node_id = node.id

        return {
            'action': {
                'id': node_id,
                'name': self.name,
            },
        }
