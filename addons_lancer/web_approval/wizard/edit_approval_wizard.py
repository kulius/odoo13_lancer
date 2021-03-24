# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.addons.web_approval.controllers.main import DiagramView


class EditApprovalWizard(models.TransientModel):
    _name = 'edit.approval.wizard'
    _description = u'编辑审批向导'

    say = fields.Text('审批意见')
    action_type = fields.Selection([('accept', '同意'), ('refuse', '拒绝')], '动作类型')

    @api.model
    def default_get(self, fields_list):
        res = super(EditApprovalWizard, self.sudo()).default_get(fields_list)

        if self._context.get('approval_id'):
            approval = self.env['approval'].browse(self._context['approval_id'])
            res.update({
                'say': approval.say,
                'action_type': {u'同意': 'accept', u'拒绝': 'refuse'}[approval.action_type]
            })
        return res


    def button_ok(self):
        def refuse_next_action():
            """拒绝后的下一步动作"""
            # 当前实例节点的状态置为完成
            instance_node = approval.instance_node_id
            instance = approval.instance_node_id.instance_id

            instance_node.state = 'complete'
            # 当前节点的实例状态置为完成，当前拒绝动作的目标动作作为next_instance_node_id值
            node_action = node_action_obj.search([('action_type', '=', action_type), ('sorce_node_id', '=', instance_node.node_id.id), ('flow_id', '=', instance.flow_id.id)])
            instance.write({
                'state': 'complete',
                'next_instance_node_id': node_action.target_node_id.id
            })

            # 删除当前节点后的所有实例节点
            for inode in instance_node_obj.search([('instance_id', '=', instance.id), ('state', 'in', ['active', 'running'])]):
                inode.unlink()
            # 将当前记录的is_commit_approval(是否提交审批)置为False，等待提交审批
            res_state = self.env['record.approval.state'].search([('model', '=', model), ('res_id', '=', res_id)])
            res_state.write({
                'is_commit_approval': False,
            })

            if not node_action.target_node_id.is_start:
                DiagramView.commit_approval(model, res_id)


        self.ensure_one()

        instance_node_obj = self.env['approval.flow.instance.node']
        node_action_obj = self.env['approval.flow.node.action']
        approval_obj = self.env['approval']

        approval_id = self._context['approval_id']  # 审批ID
        res_id = self._context['res_id'] # 记录ID
        model = self._context['model'] # 记录model
        action_type = self.action_type # 动作类型

        approval = approval_obj.browse(approval_id)

        if action_type == 'accept':
            approval.say = self.say
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
