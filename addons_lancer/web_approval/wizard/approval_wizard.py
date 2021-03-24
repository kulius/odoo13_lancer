# -*- coding: utf-8 -*-
from odoo.exceptions import ValidationError
from odoo import fields, models, api
from odoo.addons.web_approval.controllers.main import DiagramView


class ApprovalWizard(models.TransientModel):
    _name = 'approval.wizard'
    _description = u'审批向导'

    say = fields.Text('审批意见')
    action_type = fields.Selection([('accept', '同意'), ('refuse', '拒绝')], '动作类型', default='accept')


    @api.onchange('action_type')
    def onchange_action_type(self):
        action_type = self.action_type
        if not action_type:
            return

        res_id = self._context['res_id']  # 记录ID
        model = self._context['model']  # 记录model
        flow = self.env['approval.flow'].get_approval_flow(model, res_id)
        if action_type == 'accept':
            if flow.accept_template:
                self.say = flow.accept_template

        if action_type == 'refuse':
            if flow.refuse_template:
                self.say = flow.refuse_template


    def button_ok(self):
        def create_approval():
            """创建审批信息"""
            approval_obj.create({
                'instance_node_id': instance_node_id,
                'action_type': '同意' if action_type == 'accept' else '拒绝',
                'say': self.say,
                'user_id': self.env.user.id
            })

        def accept_next_action():
            """同意后的下一步处理"""
            # 当前实例节点的状态置为完成
            if instance_node.is_increase or instance_node.is_turn_to:
                all_approvaled = True
            else:
                node = instance_node.node_id # 实例节点的节点
                if node.is_all_approval: # 须全组审批
                    # 需审批的用户
                    if node.only_document_company: # 仅单据公司的用户审批
                        group_user_ids = [user.id for user in node.groups_id.users if user.company_id.id == document.company_id.id]
                    else:
                        group_user_ids = node.groups_id.users.ids

                    # 已审批的用户
                    users = [approval.user_id.id for approval in approval_obj.search([('instance_node_id', '=', instance_node.id)])]

                    if set(users).issuperset(set(group_user_ids)): # A.issuperset(B)表款A集合是否是B集合的父集
                        all_approvaled = True # 当前节点是否全部审批完成
                    else:
                        all_approvaled = False # 当前节点是否全部审批完成
                else:
                    all_approvaled = True # 当前节点是否全部审批完成

            if not all_approvaled: # 没有全部审批完成，不激活下一节点
                return

            instance_node.state = 'complete'

            # 当前顺序的所有节点是否审批完成
            seam_serial_num_node = instance_node_obj.search([('res_id', '=', res_id), ('model_name', '=', model), ('serial_num', '=', serial_num), ('instance_id', '=', instance_id), ('state', '!=', 'turn_to')])
            is_all_done = all([i_node.state == 'complete' for i_node in seam_serial_num_node])
            if not is_all_done:
                return

            next_node = instance_node_obj.search([('res_id', '=', res_id), ('model_name', '=', model), ('serial_num', '=', (serial_num + 1)), ('instance_id', '=', instance_id)])
            # 激活下一步
            if next_node:
                next_node.write({
                    'state': 'running'
                })
            # 节点实例状态置为complete, document的approval_state置为done
            else:
                instance.state = 'complete'
                res_state.approval_state = 'complete'

        def refuse_next_action():
            """拒绝后的下一步动作"""
            # 当前实例节点的状态置为完成
            instance_node.state = 'complete'
            # 当前节点的实例状态置为完成，当前拒绝动作的目标动作作为next_instance_node_id值
            node_action = node_action_obj.search([('action_type', '=', action_type), ('sorce_node_id', '=', instance_node.node_id.id), ('flow_id', '=', approval_flow.id)])
            instance.write({
                'state': 'complete',
                'next_instance_node_id': node_action.target_node_id.id
            })

            # 删除当前节点后的所有实例节点
            for inode in instance_node_obj.search([('instance_id', '=', instance_id), ('state', 'in', ['active', 'running'])]):
                inode.unlink()
            # 将当前记录的is_commit_approval(是否提交审批)置为False，等待提交审批
            res_state.write({
                'is_commit_approval': False,
            })

            if not node_action.target_node_id.is_start:
                DiagramView.commit_approval(model, res_id)


        self.ensure_one()

        instance_node_obj = self.env['approval.flow.instance.node']
        node_action_obj = self.env['approval.flow.node.action']
        approval_obj = self.env['approval']

        instance_node_id = self._context['instance_node_id']  # 实例节点ID
        res_id = self._context['res_id'] # 记录ID
        model = self._context['model'] # 记录model
        action_type = self.action_type # 动作类型

        res_state = self.env['record.approval.state'].search([('model', '=', model), ('res_id', '=', res_id)])
        if res_state.approval_state == 'pause':
            raise ValidationError('审批流程暂停!')

        # 实例节点信息
        instance_node = instance_node_obj.browse(instance_node_id)
        serial_num = instance_node.serial_num  # 当前节点的序号
        approval_flow = instance_node.flow_id  # 审批流程
        instance = instance_node.instance_id # 当前节点对应的实例
        instance_id = instance.id
        document = self.env[model].browse(res_id)  # 当前记录

        # 创建审批信息
        create_approval()

        # 审批后的下一步动作
        # show_commit_approval_btn = False
        # next_node_id = None
        if action_type == 'accept':
            accept_next_action()
        else:
            refuse_next_action()


        return {
            'state': 1
            # 'say': self.say or '',
            # 'action_type': '同意' if self._context['action_type'] == 'accept' else '拒绝',
            # 'approval_time': (datetime.strptime(self.create_date, '%Y-%m-%d %H:%M:%S') + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S'),
            # 'show_commit_approval_btn': show_commit_approval_btn, # 拒绝后是否显示提交审核按钮
            # 'next_node_id': next_node_id
        }
