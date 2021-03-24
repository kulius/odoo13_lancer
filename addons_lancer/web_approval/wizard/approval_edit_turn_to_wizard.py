# -*- coding: utf-8 -*-
from odoo import fields, models, api


class ApprovalEditTurnToWizard(models.TransientModel):
    _name = 'approval.edit.turn.to.wizard'
    _description = u'转签向导'


    user_id = fields.Many2one('res.users', '转签审批人', domain="[('share','=',False)]")



    def onchange(self, values, field_name, field_onchange):

        return {
            'domain': {
                'user_id': [('share','=',False), ('id', '!=', self.env.user.id)],
            },
            'value': {
                'user_id': self.env['approval.flow.instance.node'].browse(self._context['instance_node_id']).user_id.id
            }
        }


    def button_ok(self):
        self.ensure_one()

        instance_node_obj = self.env['approval.flow.instance.node']

        instance_node_id = self._context['instance_node_id'] # 加签的节点
        instance_node = instance_node_obj.browse(instance_node_id)

        if instance_node.user_id.id == self.user_id.id:
            return {'state': True}

        instance_node.user_id = self.user_id.id

        self.env['wait.approval'].search([('instance_node_id', '=', instance_node_id)]).user_id = self.user_id.id

        return {
            'state': True
        }





