# -*- coding: utf-8 -*-
from odoo import fields, models, api


class ApprovalTurnToWizard(models.TransientModel):
    _name = 'approval.turn.to.wizard'
    _description = u'转签向导'


    user_id = fields.Many2one('res.users', '转签审批人', domain="[('share','=',False)]")


    def onchange(self, values, field_name, field_onchange):

        return {
            'domain': {
                'user_id': [('share','=',False), ('id', '!=', self.env.user.id)],
            },
        }


    def button_ok(self):
        self.ensure_one()

        instance_node_obj = self.env['approval.flow.instance.node']

        instance_node_id = self._context['instance_node_id'] # 加签的节点
        instance_node = instance_node_obj.browse(instance_node_id)

        # 创建新的实例节点
        turn_instance_node = instance_node_obj.create({
            'flow_id': instance_node.flow_id.id,
            'node_id': False,
            'instance_id': instance_node.instance_id.id,
            'state': instance_node.state,
            'serial_num': instance_node.serial_num,
            'is_increase': False,
            'is_turn_to': True,
            'user_id': self.user_id.id,
            'allow_increase_user_id': self.env.user.id,
            'parent_id': instance_node.id,
        })

        # 创建待审批
        self.env['wait.approval'].create({
            'instance_node_id': turn_instance_node.id,
            # 'state': 'running' if action_type == 'before' else 'active',
            'apply_id': self.env.user.id,
            'user_id': self.user_id.id
        })

        # 当前实例节点状态改为转签
        instance_node.state = 'turn_to'




        return {
            'state': True
        }





