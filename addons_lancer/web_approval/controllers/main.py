# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import logging
import json
import networkx as nx

from odoo import http
from odoo.http import request
from odoo.exceptions import ValidationError
from odoo.addons.web.controllers.main import DataSet, Action

_logger = logging.getLogger(__name__)


class DiagramView(http.Controller):

    @http.route('/web/dataset/get_approval_flow', type='json', auth="user")
    def get_approval_info(self, model, res_id):
        """是否显示提交审批按钮和审批流程信息"""
        def can_approval_current_node():
            """是否可以审批当前节点"""
            if res_state.approval_state == 'pause' or res_state.approval_state == 'cancel':
                return False

            # 状态不是正在审批的不能审批
            if instance_node.state != 'running':
                return False

            # 当前用户审批过当前节点的不能再审批
            if filter(lambda x: x['user_id'] == user_id, approval_info):
                return False

            # 是加签节点，但当前用户不是节点的审批用户，不能审批当前节点
            if is_increase or is_turn_to:
                if instance_node.user_id.id == user_id:
                    return True

                return False

            # 当前用户不在当前节点对应的组中
            if user_id not in node.groups_id.sudo().users.ids:
                return False

            # 当前实例节点对应的节点仅能单据所在公司的用户审批
            if node.only_document_company:
                # 当前用户所属公司不等于单据所属公司，不能审批当前节点
                if document.company_id.id != user.company_id.id:
                    return False

                # 当前实例节点对应的节点需全组人审批，当前用户可以审批
                if node.is_all_approval:
                    return True

                # 当前节点没有人审批
                if len(approval_info) == 0:
                    return True

                return False # 当前节点有人审批了

            # 当前实例节点对应的节点需全组人审批，当前用户可以审批
            if node.is_all_approval:
                return True

            # 当前节点没有人审批
            if len(approval_info) == 0:
                return True

            return False # 当前节点有人审批了

        def compute_node_name():
            """计算节点名称"""
            if can_approval:
                if is_increase:
                    node_name = u'(加)(我)%s' % (instance_node.parent_id.node_id.name,)
                else:
                    if is_turn_to:
                        node_name = u'(转)(我)%s' % (instance_node.parent_id.node_id.name,)
                    else:
                        node_name = u'(我)%s' % (node.name,)
            else:
                if is_increase:
                    node_name = u'(加)(%s)%s' % (instance_node.user_id.name, instance_node.parent_id.node_id.name, )
                else:
                    if is_turn_to:
                        node_name = u'(转)(%s)%s' % (instance_node.user_id.name, instance_node.parent_id.node_id.name, )
                    else:
                        node_name = node.name

            return node_name

        def compute_allow_increase():
            """计算当前节点是否允许加签"""
            if res_state.approval_state == 'pause' or res_state.approval_state == 'cancel':
                return False

            # 完成的节点或是加签的节点，不允许加签
            if instance_node.state == 'complete' or is_increase:
                return False

            # 当前节点不允许前加签和后加签，不允许加签
            if not node.allow_before_increase and not node.allow_after_increase:
                return False

            # 当前节点允许前加签且前加签存在，允许后加签且后加签存在，不允许加签
            exist_before_increase = instance_node_obj.search([('parent_id', '=', instance_node.id), ('increase_type', '=', 'before')]).exists() # 存在前加签
            exist_after_increase = instance_node_obj.search([('parent_id', '=', instance_node.id), ('increase_type', '=', 'after')]).exists() # 存在后加签

            if node.allow_before_increase and not node.allow_after_increase:
                if exist_before_increase:
                    return False

            if not node.allow_before_increase and node.allow_after_increase:
                if exist_after_increase:
                    return False

            if node.allow_before_increase and node.allow_after_increase:
                if exist_before_increase and exist_after_increase:
                    return False


            # 当前用户不在当前节点对应的组中
            if user_id not in node.groups_id.sudo().users.ids:
                return False

            # 当前实例节点对应的节点仅能单据所在公司的用户审批
            if node.only_document_company:
                # 当前用户所属公司不等于单据所属公司，不能审批当前节点
                if document.company_id.id != user.company_id.id:
                    return False

            return True

        def compute_can_delete():
            """对于加签的节点，当前用户是否可以删除"""
            if res_state.approval_state == 'pause' or res_state.approval_state == 'cancel':
                return False

            # 不是加签的节点，不能删除
            if not is_increase:
                return False

            # 加签节点已审批完成， 不能删除
            if instance_node.state == 'complete':
                return False

            # 不是当前用户提出的加签，不能删除
            if instance_node.allow_increase_user_id.id != user_id:
                return False

            return True

        def compute_allow_turn_to():
            """计算是否允许转签"""
            if res_state.approval_state == 'pause' or res_state.approval_state == 'cancel':
                return False

            # 已审批完成， 不能转签
            if instance_node.state == 'complete':
                return False

            # 当前节点不允许转签，不能转签
            if not node.allow_turn_to:
                return False

            # 当前用户不在当前节点对应的组中， 不能转签
            if user_id not in node.groups_id.sudo().users.ids:
                return False

            # 当前实例节点对应的节点仅能单据所在公司的用户审批
            if node.only_document_company:
                # 当前用户所属公司不等于单据所属公司，不能审批当前节点
                if document.company_id.id != user.company_id.id:
                    return False


            return True

        def compute_can_delete_turn_to():
            """计算是否可删除转签"""
            if res_state.approval_state == 'pause' or res_state.approval_state == 'cancel':
                return False
            # 不是加签的节点，不能删除
            if not is_turn_to:
                return False

            # 加签节点已审批完成， 不能删除
            if instance_node.state == 'complete':
                return False

            # 不是当前用户提出的加签，不能删除
            if instance_node.allow_increase_user_id.id != user_id:
                return False

            return True

        def compute_btn_state():
            # 当前用户是否属于记录公司
            if request.env.user.company_id.id != document.company_id.id:
                show_commit_btn = False
            else:
                # 未提交审批
                if not res_state.is_commit_approval:
                    # 没有指定提交审批的组
                    if not approval_flow.commit_approval_group_id:
                        show_commit_btn = True
                    # 指定了提交审批的组
                    else:
                        # 当前用户在指定组中
                        if request.env.user.id in approval_flow.commit_approval_group_id.sudo().users.ids:
                            show_commit_btn = True
                        else:
                            show_commit_btn = False
                # 已提交审批
                else:
                    show_commit_btn = False

            return show_commit_btn

        def compute_show_buttons():
            # 当前用户是否属于记录公司
            if request.env.user.company_id.id != document.company_id.id:
                show_buttons = False
            else:
                # 没有指定提交审批的组
                if not approval_flow.commit_approval_group_id:
                    show_buttons = True
                # 指定了提交审批的组
                else:
                    # 当前用户在指定组中
                    if request.env.user.id in approval_flow.commit_approval_group_id.sudo().users.ids:
                        show_buttons = True
                    else:
                        show_buttons = False

            return show_buttons

        def compute_approval_info():
            """审批信息可编辑"""
            if res_state.approval_state != 'active':
                return False

            if approval.user_id.id != user_id:
                return False

            next_nodes = instance_node_obj.search([('instance_id', '=', instance.id), ('serial_num', '=', instance_node.serial_num + 1), ('state', '!=', 'turn_to')])
            if not next_nodes:
                return False

            for next_node in next_nodes:
                if request.env['approval'].search([('instance_node_id', '=', next_node.id)]):
                    return False

            return True





        res = {
            'show_commit_btn': False,
            'instance_nodes': [],
            'approval_state': '',
            'show_buttons': False
        }

        approval_flow = request.env['approval.flow'].get_approval_flow(model, res_id)
        if not approval_flow:
            return res

        if not [a for a in approval_flow.action_ids if a.action_type == 'accept']:
            return res

        res_state = request.env['record.approval.state'].search([('model', '=', model), ('res_id', '=', res_id)])
        if not res_state:
            return res

        document = request.env[model].browse(res_id)  # 当前单据

        instance_node_obj = request.env['approval.flow.instance.node']

        # 计算审批信息
        instance_nodes = []
        # 当前用户ID
        user = request.env.user
        user_id = user.id

        for instance in request.env['approval.flow.instance'].search([('model_name', '=', model), ('res_id', '=', res_id)], order='id desc'):
            for instance_node in instance_node_obj.search([('instance_id', '=', instance.id)], order='serial_num desc'):
                # 转签不处理
                if instance_node.state == 'turn_to':
                    continue

                # 当前节点
                node = instance_node.node_id

                # 当前节点的审批信息
                approval_info = []
                for approval in instance_node.approval_ids:
                    # user_name = approval.user_id.name if approval.user_id.id != user_id else u'我'
                    # user_name += u'(%s)' % node.name
                    approval_info.append({
                        'user_name': approval.user_id.name , # 审批用户名
                        'approval_time': (datetime.strptime(approval.create_date, '%Y-%m-%d %H:%M:%S') + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S'), # 审批时间
                        'action_type': approval.action_type,
                        'say': approval.say or '',
                        'id': approval.id,
                        'user_id': approval.user_id.id,
                        'can_edit': compute_approval_info()
                    })
                approval_info.sort(key=lambda x: x['id'], reverse=True)

                is_increase = instance_node.is_increase # 是加签
                is_turn_to = instance_node.is_turn_to # 是转签

                can_approval = can_approval_current_node() # 是否可以审批当前节点

                instance_nodes.append({
                    'id': instance_node.id,
                    'serial_num': instance_node.serial_num,
                    'state': instance_node.state,
                    'is_increase': is_increase, # 是加签

                    'allow_increase_user_id': instance_node.allow_increase_user_id.id, # 加签申请人/转签申请人
                    'node_info': {
                        'node_name': compute_node_name(), # 节点名称
                        # 'node_name': u'%s-加(%s)' % (instance_node.parent_id.node_id.name, instance_node.user_id.name) if is_increase else node.name, # 节点名称
                        'allow_increase': node.allow_before_increase or node.allow_after_increase,  # 节点是否允许前加签
                        'allow_turn_to': node.allow_turn_to,  # 节点是允许转签

                    }, # 实例节点对应的节点信息

                    'approval_info': approval_info, # 实例节点对应的审批信息
                    'can_approval': can_approval, # 当前用户是否可以审批当前节点
                    'allow_increase': compute_allow_increase(),
                    'allow_turn_to': compute_allow_turn_to(),
                    'can_delete': compute_can_delete(), # 对于加签的节点，当前用户是否可以删除
                    'can_delete_turn_to': compute_can_delete_turn_to(), # 是否可删除转签
                    'can_edit_turn_to': compute_can_delete_turn_to(), # 是否可编辑转签
                })


        return {
            'instance_nodes': instance_nodes,
            'show_commit_btn': compute_btn_state(),
            'approval_state': res_state.approval_state or '',
            'show_buttons': compute_show_buttons(),
        }


    @staticmethod
    def commit_approval(model, res_id):
        """提交审批"""
        instance_obj = request.env['approval.flow.instance']
        instance_node_obj = request.env['approval.flow.instance.node']
        wait_approval_obj = request.env['wait.approval']

        instances = instance_obj.search([('res_id', '=', res_id), ('model_name', '=', model), ('state', '=', 'active')])
        if instances:
            raise ValidationError('模型的审批流程已经存在！')


        approval_flow = request.env['approval.flow'].get_approval_flow(model, res_id)
        if not approval_flow:
            return

        if not [a for a in approval_flow.action_ids if a.action_type == 'accept']:
            return {'show_create_btn': False, 'instance_nodes': []}

        # 开始节点、结束结点
        start_node = filter(lambda n: n.is_start, approval_flow.node_ids)[0]
        end_node = filter(lambda n: n.is_end, approval_flow.node_ids)[0]

        edges = [] # 边
        for node_action in approval_flow.action_ids:
            if node_action.action_type == 'refuse':
                continue

            if node_action.condition:
                condition = eval(node_action.condition)
                condition += [('id', '=', res_id)]
                if request.env[model].search(condition):
                    edges.append((node_action.sorce_node_id.id, node_action.target_node_id.id))
            else:
                edges.append((node_action.sorce_node_id.id, node_action.target_node_id.id))

        # 创建图
        G = nx.DiGraph(edges)
        try:
            # 整个审批流程的所有路径
            all_paths = [path for path in nx.all_simple_paths(G, source=start_node.id, target=end_node.id)]
        except nx.NodeNotFound:
            raise ValidationError('审批流程错误，应以开始节点开始，以结束节点结束！')

        # 实际开始节点
        start_node_id = start_node.id
        instance = instance_obj.search([('res_id', '=', res_id), ('model_name', '=', model)], order='id desc', limit=1) # 存在的实例
        if instance:
            next_instance_node_id = instance.next_instance_node_id # 下一实例开始节点
            if next_instance_node_id:
                start_node_id = next_instance_node_id

        real_paths = [path[path.index(start_node_id):] for path in all_paths]

        edges = [] # 边
        for path in real_paths:
            for i in range(len(path) - 1):
                edge = (path[i], path[i + 1])

                if edge not in edges:
                    edges.append(edge)

        # 创建图
        G = nx.DiGraph(edges)
        in_degree = {} # 入度
        for source, target in edges:
            in_degree.setdefault(target, []).append(source)

        # 入度为0的节点
        source = [v for v, d in G.in_degree() if d == 0]
        [in_degree.update({s: []}) for s in source]

        paths = []
        serial_num = 0
        while source:
            for s in source:
                in_degree.pop(s)
                paths.append({
                    'node_id': s,
                    'serial_num': serial_num
                })
                for d in in_degree.keys():
                    if s in in_degree[d]:
                        in_degree[d].remove(s)

            source = [v for v in in_degree.keys() if len(in_degree[v]) == 0]
            serial_num += 1

        _logger.info(u'审批路径：%s', json.dumps(paths, indent=4))
        if not paths:
            return

        # 更新记录审批状态的是否提交审批字段
        res_state = request.env['record.approval.state'].search([('model', '=', model), ('res_id', '=', res_id)])
        res_state.write({
            'is_commit_approval': True,
            'approval_state': 'active'
        })
        # 创建审批流程实例
        instance = instance_obj.create({
            'flow_id': approval_flow.id,
            'res_id': res_id,
            'model_name': model,
            'state': 'active',
            'str_node_ids': json.dumps(paths)
        })
        # 创建实例节点
        paths.sort(key=lambda x: x['serial_num'])
        # 不是开始节点(is_start=False)的最小的序号
        min_serial_num = 0
        for path in paths:
            node_id = path['node_id']
            node = request.env['approval.flow.node'].browse(node_id)
            if node.is_start:
                continue

            min_serial_num = path['serial_num']
            break

        for path in paths:
            node_id = path['node_id']
            node = request.env['approval.flow.node'].browse(node_id)
            if node.is_start or node.is_end:
                continue

            instance_node = instance_node_obj.create({
                'flow_id': approval_flow.id,
                'node_id': path['node_id'],
                'instance_id': instance.id,
                'serial_num': path['serial_num'],
                'state': 'running' if path['serial_num'] == min_serial_num else 'active'
            })

            # 创建待审批
            for user in node.groups_id.users:
                wait_approval_obj.create({
                    'instance_node_id': instance_node.id,
                    'apply_id': request.env.user.id,
                    'user_id': user.id
                })



        return {'state': 1}


    @http.route('/web/dataset/control_approval', type='json', auth="user")
    def control_approval(self, model, res_id, action_type):
        """控制工作流"""
        if action_type == 'commit_approval':
            return self.commit_approval(model, res_id)

        res_state = request.env['record.approval.state'].search([('model', '=', model), ('res_id', '=', res_id)])
        if action_type == 'pause_approval':
            res_state.approval_state = 'pause'
        elif action_type == 'resume_approval':
            res_state.approval_state = 'active'
        elif action_type == 'cancel_approval':
            res_state.approval_state = 'cancel'

        return {'state': 1}


    @http.route('/web_approval/get_approval_info', type='json', auth='user')
    def get_diagram_info(self, flow_id):

        approval_flow = request.env['approval.flow'].browse(flow_id)
        nodes = [{'id': node.id, 'name': node.name, 'is_start': node.is_start, 'is_end': node.is_end}for node in approval_flow.node_ids]
        actions = [{'id': action.id, 'action_type': action.action_type, 'condition': action.condition, 'source_node_id': action.sorce_node_id.id, 'target_node_id': action.target_node_id.id} for action in approval_flow.action_ids]

        edges = [] # 边
        for node_action in approval_flow.action_ids:
            if node_action.action_type == 'refuse':
                continue

            edges.append((node_action.sorce_node_id.id, node_action.target_node_id.id))

        # 创建图
        G = nx.DiGraph(edges)
        in_degree = {} # 入度
        for source, target in edges:
            in_degree.setdefault(target, []).append(source)

        # 入度为0的节点
        source = [v for v, d in G.in_degree() if d == 0]
        # source = [v for v, d in G.in_degree() if d == 0]
        [in_degree.update({s: []}) for s in source]

        paths = []
        serial_num = 0
        while source:
            for s in source:
                node = request.env['approval.flow.node'].browse(s)
                in_degree.pop(s)
                paths.append({
                    'node_id': s,
                    'serial_num': serial_num,
                    'node_name': node.name,
                    'is_start': node.is_start,
                    'is_end': node.is_end
                })
                for d in in_degree.keys():
                    if s in in_degree[d]:
                        in_degree[d].remove(s)

            source = [v for v in in_degree.keys() if len(in_degree[v]) == 0]
            serial_num += 1

        # nodes不在paths中的节点
        not_in_paths_nodes = list(set([node['id'] for node in nodes]) - set([path['node_id'] for path in paths]))
        for node_id in  not_in_paths_nodes:
            node = request.env['approval.flow.node'].browse(node_id)
            if node.is_start:
                for path in paths:
                    path['serial_num'] += 1

                paths.insert(0, {
                    'node_id': node_id,
                    'serial_num': 0,
                    'node_name': node.name,
                    'is_start': node.is_start,
                    'is_end': node.is_end
                })

            if node.is_end:
                paths.append({
                    'node_id': node_id,
                    'serial_num': paths[-1]['serial_num'] + 1 if paths else 0,
                    'node_name': node.name,
                    'is_start': node.is_start,
                    'is_end': node.is_end
                })

        not_in_paths_nodes = list(set([node['id'] for node in nodes]) - set([path['node_id'] for path in paths]))
        for node_id in not_in_paths_nodes:
            node = request.env['approval.flow.node'].browse(node_id)
            end_node = paths[-1]
            paths.insert(0, {
                'node_id': node_id,
                'serial_num': end_node['serial_num'],
                'node_name': node.name,
                'is_start': node.is_start,
                'is_end': node.is_end
            })
            end_node['serial_num'] += 1

        paths.sort(key=lambda x: x['serial_num'])

        return {
            'nodes': nodes,
            'actions': actions,
            'paths': paths
        }


class MyDataSet(DataSet):
    @http.route()
    def call_button(self, model, method, args, kwargs):
        res = super(MyDataSet, self).call_button(model, method, args, kwargs)

        # 安装不执行
        if not request.env.registry.models.get('increase.type'):
            return res

        for res_id in args[0]:
            approval_flow = request.env['approval.flow'].get_approval_flow(model, res_id)
            if not approval_flow:
                continue

            res_state = request.env['record.approval.state'].search([('model', '=', model), ('res_id', '=', res_id)])


            approval_can_run = approval_flow.approval_can_run
            approval_cannot_run = approval_flow.approval_cannot_run

            if approval_can_run:
                approval_can_run = map(lambda x: x.strip(), approval_can_run.split(','))
                if method in approval_can_run:
                    if res_state.approval_state != 'complete':
                        raise ValidationError(u'审批尚未完成！')

            if approval_cannot_run:
                approval_cannot_run = map(lambda x: x.strip(), approval_cannot_run.split(','))
                if method in approval_cannot_run:
                    if res_state.approval_state == 'complete':
                        raise ValidationError(u'审批完成，不能执行该动作！')

        return res


# class MyAction(Action):
#     @http.route()
#     def load(self, action_id, additional_context=None):
#         res = super(MyAction, self).load(action_id, additional_context=additional_context)
#         if not request.env.registry.models.get('increase.type'):
#             return res
#
#         if not additional_context:
#             return res
#
#         model = additional_context.get('active_model')
#         res_id = additional_context.get('active_id')
#         approval_flow = request.env['approval.flow'].get_approval_flow(model, res_id)
#
#         if not approval_flow:
#             return res
#
#         if action_id in approval_flow.act_window_ids.ids:
#             raise ValidationError(u'审批尚未完成！')
#
#         return res
















