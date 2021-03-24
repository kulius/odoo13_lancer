# -*- coding: utf-8 -*-
from odoo import models, api
from odoo.exceptions import ValidationError


write_origin = models.BaseModel.write



def write(self, vals):
    result = write_origin(self, vals)

    approval_cannot_write(self)
    return result


def approval_cannot_write(self):
    """审批后不能执行修改动作"""
    # 安装本模块时不执行
    if not self.env.registry.models.get('increase.type'):
        return

    for res in self:
        approval_flow = self.env['approval.flow'].get_approval_flow(self._name, res.id)
        # 没有对应的流程
        if not approval_flow:
            continue

        approval_cannot_run = approval_flow.approval_cannot_run or ''
        approval_cannot_run = map(lambda x: x.strip(), approval_cannot_run.split(','))
        if 'write' in approval_cannot_run:
            res_state = self.env['record.approval.state'].search([('model', '=', self._name), ('res_id', '=', res.id)]) # 记录审批状态
            if res_state and res_state.approval_state == 'complete':
                raise ValidationError('审批完成，不能修改记录！')


models.BaseModel.write = write



