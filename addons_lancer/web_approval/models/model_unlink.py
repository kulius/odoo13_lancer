# -*- coding: utf-8 -*-
from odoo import models, api
from odoo.exceptions import ValidationError


unlink_origin = models.BaseModel.unlink



def unlink(self):
    result = unlink_origin(self)

    approval_cannot_unlink(self)

    return result


def approval_cannot_unlink(self):
    """审批后不能执行删除动作"""
    # 安装本模块时不执行
    if not self.env.registry.models.get('increase.type'):
        return

    flow_obj = self.env['approval.flow']
    res_state_obj = self.env['record.approval.state']
    instance_obj = self.env['approval.flow.instance']

    for res in self:

        approval_flow = flow_obj.get_approval_flow(self._name, res.id)
        # 没有对应的流程
        if not approval_flow:
            continue

        approval_cannot_run = approval_flow.approval_cannot_run or ''
        approval_cannot_run = map(lambda x: x.strip(), approval_cannot_run.split(','))

        if 'unlink' in approval_cannot_run:
            res_state = res_state_obj.search([('model', '=', self._name), ('res_id', '=', res.id)])  # 记录审批状态
            if res_state and res_state.approval_state == 'complete':
                raise ValidationError('审批完成，不能删除记录！')


        # 删除审批状态
        res_state = res_state_obj.search([('model', '=', self._name), ('res_id', '=', res.id)])
        if res_state:
            res_state.unlink()

        # 删除审批流程实例
        instances = instance_obj.search([('res_id', '=', res.id), ('model_name', '=', self._name)])
        if instances:
            for instance in instances:
                instance.unlink()

    # unlink_approval_flow(self)



# def unlink_approval_flow(self):
#     """删除审批流程实例和特点"""
#     res_state_obj = self.env['record.approval.state']
#     instance_obj = self.env['approval.flow.instance']
#     flow_obj = self.env['approval.flow']
#
#     for res in self:
#         approval_flow = flow_obj.get_approval_flow(self._name, res.id)
#         # 没有对应的流程
#         if not approval_flow:
#             continue
#
#         # 删除审批状态
#         res_state = res_state_obj.search([('model', '=', self._name), ('res_id', '=', res.id)])
#         if res_state:
#             res_state.unlink()
#
#         # 删除审批流程实例
#         instances = instance_obj.search([('res_id', '=', res.id), ('model_name', '=', self._name)])
#         if instances:
#             for instance in instances:
#                 instance.unlink()


models.BaseModel.unlink = unlink

