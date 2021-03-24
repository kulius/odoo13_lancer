# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import fields, models, api
from odoo.exceptions import ValidationError


class AddNodeActionWizard(models.TransientModel):
    _name = 'add.node.action.wizard'
    _description = u'添加动作向导'

    flow_id = fields.Many2one('approval.flow', '流程', ondelete='cascade')
    action_type = fields.Selection([('accept', '同意'), ('refuse', '拒绝')], '动作类型')
    condition = fields.Char('条件')
    sorce_node_id = fields.Many2one('approval.flow.node', '源节点')
    target_node_id = fields.Many2one('approval.flow.node', '目标节点')

    @api.onchange('sorce_node_id')
    def onchange_sorce_node_id(self):
        if self.sorce_node_id and self.sorce_node_id.is_start:
            self.action_type = 'accept'

    @api.onchange('target_node_id')
    def onchange_target_node_id(self):
        if self.target_node_id and self.target_node_id.is_start:
            self.action_type = 'refuse'

    @api.model
    def default_get(self, fields_list):
        res = super(AddNodeActionWizard, self.sudo()).default_get(fields_list)
        context = self._context
        if context.get('source_node_id'):
            res['sorce_node_id'] = context['source_node_id']

        if context.get('target_node_id'):
            res['target_node_id'] = context['target_node_id']

        if context.get('flow_id'):
            res['flow_id'] = context['flow_id']

        if context.get('source_serial_num') and context.get('target_serial_num'):
            source_serial_num = context['source_serial_num']
            target_serial_num = context['target_serial_num']

            if source_serial_num < target_serial_num:
                res['action_type'] = 'accept'

            if source_serial_num > target_serial_num:
                res['action_type'] = 'refuse'

        return res



    def button_ok(self):
        self.ensure_one()
        node_action_obj = self.env['approval.flow.node.action']
        # 作动存在
        node_action = node_action_obj.search([('flow_id', '=', self.flow_id.id), ('sorce_node_id', '=', self.sorce_node_id.id), ('target_node_id', '=', self.target_node_id.id), ('action_type', '=', self.action_type)])
        if node_action:
            raise ValidationError(u'动作已经存在')

        # 开始节点和结束节点之前不能建立动作
        if (self.sorce_node_id.is_start and self.target_node_id.is_end) or (self.target_node_id.is_start and self.sorce_node_id.is_end):
            raise ValidationError(u'源节点和目标节点之前不能建立连接！')

        # 源节点和目标结点不能相同
        if self.sorce_node_id.id == self.target_node_id.id:
            raise ValidationError(u'源节点和目标结点不能相同!')

        # 创建动作
        action = node_action_obj.create({
            'flow_id': self.flow_id.id,
            'sorce_node_id': self.sorce_node_id.id,
            'target_node_id': self.target_node_id.id,
            'action_type': self.action_type,
            'condition': self.condition,
        })
        return {
            'action': {
                'id': action.id,
                'action_type': action.action_type,
                'condition': action.condition,
                'source_node_id': action.sorce_node_id.id,
                'target_node_id': action.target_node_id.id
            },

        }
