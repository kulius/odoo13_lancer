# -*- coding: utf-8 -*-
from odoo import models, fields, api
from lxml import etree
import logging
import json


_logger = logging.getLogger(__name__)


class View(models.Model):
    _inherit = 'ir.ui.view'

    type = fields.Selection(selection_add=[('approval_diagram', '审批流程')])


fields_view_get_origin = models.BaseModel.fields_view_get


@api.model
def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    result = fields_view_get_origin(self, view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
    view_get_approval_flow(self, view_id, view_type, toolbar, submenu, result)
    return result


models.BaseModel.fields_view_get = fields_view_get


def view_get_approval_flow(self, view_id, view_type, toolbar, submenu, result):
    if not self.env.registry.models.get('increase.type'):
        return

    if view_type != 'form':
        return

    model_id = self.env['ir.model'].sudo().search([('model', '=', self._name)]).id
    flows = self.env['approval.flow'].sudo().search([('model_id', '=', model_id)])
    if not flows:
        return

    # 是否存在<header>
    root = etree.fromstring(result['arch'])
    headers = root.xpath('header')
    if not headers:
        header = etree.Element('header')
        root.insert(0, header)
    else:
        header = headers[0]

    div = etree.Element('div')
    div.set('style', 'display:inline-block; margin-left:10px')

    # 提交审批
    button = etree.Element('button')
    button.set('invisible', '1')
    button.set('modifiers', json.dumps({'invisible': 'true'}))
    button.set('string', u'提交审批')
    button.set('class', 'oe_highlight btn-commit-approval')
    button.set('type', 'commit_approval')
    button.set('style', 'margin:0 2px')
    div.append(button)
    # 暂停审批
    button = etree.Element('button')
    button.set('invisible', '1')
    button.set('modifiers', json.dumps({'invisible': 'true'}))
    button.set('string', u'暂停审批')
    button.set('class', 'btn-default btn-pause-approval')
    button.set('type', 'pause_approval')
    button.set('style', 'margin:0 2px')
    div.append(button)
    # 恢复审批
    button = etree.Element('button')
    button.set('invisible', '1')
    button.set('modifiers', json.dumps({'invisible': 'true'}))
    button.set('string', u'恢复审批')
    button.set('class', 'oe_highlight btn-resume-approval')
    button.set('type', 'resume_approval')
    button.set('style', 'margin:0 2px')
    div.append(button)
    # 取消审批
    button = etree.Element('button')
    button.set('invisible', '1')
    button.set('modifiers', json.dumps({'invisible': 'true'}))
    button.set('string', u'取消审批')
    button.set('class', 'btn-default btn-cancel-approval')
    button.set('type', 'cancel_approval')
    button.set('style', 'margin:0 2px')
    div.append(button)
    # 审批
    button = etree.Element('button')
    button.set('invisible', '1')
    button.set('modifiers', json.dumps({'invisible': 'true'}))
    button.set('string', u'审批')
    button.set('class', 'oe_highlight btn-do-approval')
    button.set('type', 'approval')
    button.set('style', 'margin-left:10px')
    div.append(button)

    header.insert(len(header.xpath('button')), div)



    result['arch'] = etree.tostring(root)


