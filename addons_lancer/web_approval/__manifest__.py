# -*- coding: utf-8 -*-
{
    'name': 'Web Approval',
    'category': 'Hidden',
    'author': '675938238@qq.com',
    'version': '1.0',
    'summary': '审批流程',
    'description': '要实现审批流程的model所在的模块不用依赖此模块，实现条件审批、会签，未实现代签',
    'depends': ['web', 'mail'],
    'auto_install': False,
    'data': [
        'security/ir.model.access.csv',

        'data/increase_type.xml',

        'views/menu.xml',
        'views/approval_flow_view.xml',
        'views/wait_approval_summary_view.xml',
        'views/web_template.xml',
        #
        'wizard/approval_wizard_view.xml',
        'wizard/add_node_action_wizard_view.xml',
        'wizard/edit_node_action_wizard_view.xml',
        'wizard/edit_node_wizard_view.xml',
        'wizard/approval_increase_wizard_view.xml',
        'wizard/approval_turn_to_wizard_view.xml',
        'wizard/approval_edit_turn_to_wizard_view.xml',
        'wizard/edit_approval_wizard_view.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],
    'auto_install': False,
    'application': False
}
