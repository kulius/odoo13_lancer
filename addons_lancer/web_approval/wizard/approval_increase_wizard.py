# -*- coding: utf-8 -*-
import json
from odoo import fields, models, api


class ApprovalIncreaseWizard(models.TransientModel):
    _name = 'approval.increase.wizard'
    _description = u'加签向导'


    user_id = fields.Many2one('res.users', '加签审批人', domain="[('share','=',False)]")
    increase_type = fields.Many2one('increase.type', '加签类型')


    def onchange(self, values, field_name, field_onchange):
        instance_node_obj = self.env['approval.flow.instance.node']

        increase_type_domain = []

        instance_node = instance_node_obj.browse(self._context['instance_node_id'])
        node = instance_node.node_id

        exist_before_increase = instance_node_obj.search([('parent_id', '=', instance_node.id), ('increase_type', '=', 'before')]).exists()  # 存在前加签
        exist_after_increase = instance_node_obj.search([('parent_id', '=', instance_node.id), ('increase_type', '=', 'after')]).exists()  # 存在后加签

        before_increase_id = self.env.ref('web_approval.increase_type_before').id
        after_increase_id = self.env.ref('web_approval.increase_type_after').id

        if node.allow_before_increase:
            if not exist_before_increase:
                increase_type_domain.append(before_increase_id)

        if node.allow_after_increase:
            if not exist_after_increase:
                increase_type_domain.append(after_increase_id)

        result = {
            'domain': {
                'user_id': [('share','=',False), ('id', '!=', self.env.user.id)],
                'increase_type': [('id', 'in', increase_type_domain)]
            },
        }
        if len(increase_type_domain) == 1:
            result.update({
                'value': {
                    'increase_type': increase_type_domain[0]
                }
            })
        return result


    def button_ok(self):
        def update_instance_str_node_ids():
            """修改审批实例的str_node_ids字段"""
            str_node_ids = json.loads(instance.str_node_ids)
            # 前加签
            if action_type == 'before':
                for node in str_node_ids:
                    if node['serial_num'] >= instance_node_serial_num:
                        node['serial_num'] += 1

                str_node_ids.append({
                    'node_id': False,
                    'serial_num': instance_node_serial_num,
                    'is_increase': True,
                    'user_id': self.user_id.id,
                    'allow_increase_user_id': self.env.user.id,
                    'parent_id': instance_node.id,
                    'increase_type': action_type,
                })
            # 后加签
            else:
                for node in str_node_ids:
                    if node['serial_num'] > instance_node_serial_num:
                        node['serial_num'] += 1

                str_node_ids.append({
                    'node_id': False,
                    'serial_num': instance_node_serial_num + 1,
                    'is_increase': True,
                    'user_id': self.user_id.id,
                    'allow_increase_user_id': self.env.user.id,
                    'parent_id': instance_node.id,
                    'increase_type': action_type,
                })
            str_node_ids.sort(key=lambda x: x['serial_num'])
            instance.str_node_ids = json.dumps(str_node_ids)

        def add_instance_node():
            """添加实例节点"""

            if action_type == 'before':
                for node in instance_node_obj.search([('instance_id', '=', instance.id)]):
                    if node.serial_num >= instance_node_serial_num:
                        node.serial_num += 1
                        # if node.state == 'running':
                        #     node.state = 'active'
                state = 'active'
                if instance_node.state == 'running':
                    instance_node.state = 'active'
                    state = 'running'

                node = instance_node_obj.create({
                    'flow_id': instance_node.flow_id.id,
                    'node_id': False,
                    'instance_id': instance.id,
                    'state': state,
                    'serial_num': instance_node_serial_num,
                    'is_increase': True,
                    'user_id': self.user_id.id,
                    'allow_increase_user_id': self.env.user.id,
                    'parent_id': instance_node.id,
                    'increase_type': action_type,

                })


            else:
                for node in instance_node_obj.search([('instance_id', '=', instance.id)]):
                    if node.serial_num > instance_node_serial_num:
                        node.serial_num += 1

                node = instance_node_obj.create({
                    'flow_id': instance_node.flow_id.id,
                    'node_id': False,
                    'instance_id': instance.id,
                    'state': 'active',
                    'serial_num': instance_node_serial_num + 1,
                    'is_increase': True,
                    'user_id': self.user_id.id,
                    'allow_increase_user_id': self.env.user.id,
                    'parent_id': instance_node.id,
                    'increase_type': action_type,
                })

            return node

        def add_wait_approval():
            """添加待审批"""
            # if action_type == 'before':
            #     self.env['wait.approval'].search([('instance_node_id', '=', instance_node_id), ('state', '=', 'running')]).write({
            #         'state': 'active'
            #     })

            self.env['wait.approval'].create({
                'instance_node_id': increase_instance_node.id,
                # 'state': 'running' if action_type == 'before' else 'active',
                'apply_id': self.env.user.id,
                'user_id': self.user_id.id
            })


        self.ensure_one()

        instance_node_obj = self.env['approval.flow.instance.node']

        context = self._context
        action_type = self.increase_type.code # 值：before、after，前加签还是后加签
        instance_node_id = context['instance_node_id'] # 加签的节点

        # 当前实例节点
        instance_node = instance_node_obj.browse(instance_node_id)
        instance_node_serial_num = instance_node.serial_num
        # 当前实例
        instance = instance_node.instance_id

        update_instance_str_node_ids()
        increase_instance_node = add_instance_node() # 加签的实例节点
        add_wait_approval()


        return {
            'state': True
            # 'name': instance_node.name + u'-加(%s)' % self.user_id.name,
            # 'action_type': action_type,
        }



