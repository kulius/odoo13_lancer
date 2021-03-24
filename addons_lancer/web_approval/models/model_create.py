# -*- coding: utf-8 -*-
import logging

from odoo import models, api


_logger = logging.getLogger(__name__)


create_origin = models.BaseModel.create


@api.model
@api.returns('self', lambda value: value.id)
def create(self, vals):
    record = create_origin(self, vals)
    create_approval_flow(self, record)  # 创建审批流程

    return record


models.BaseModel.create = create



def create_approval_flow(self, record):
    """创建审批流程实例及节点"""
    # 安装本模块时不执行
    if not self.env.registry.models.get('increase.type'):
        return

    model = self._name
    res_id = record.id

    approval_flow = self.env['approval.flow'].get_approval_flow(model, res_id)
    # 没有对应的流程
    if not approval_flow:
        return

    # 创建审批状态
    self.env['record.approval.state'].create({
        'model': model,
        'res_id': res_id,
    })
    # TODO

    # if not approval_flow.action_ids:
    #     return
    #
    # if not approval_flow.on_create:
    #     return
    #
    # instance_obj = self.env['approval.flow.instance']
    # instance_node_obj = self.env['approval.flow.instance.node']
    # wait_approval_obj = self.env['wait.approval']
    #
    # # 开始节点、结束结点
    # start_node = filter(lambda n: n.is_start, approval_flow.node_ids)[0]
    # end_node = filter(lambda n: n.is_end, approval_flow.node_ids)[0]
    #
    # edges = []  # 边
    # for node_action in approval_flow.action_ids:
    #     if node_action.action_type == 'refuse':
    #         continue
    #
    #     if node_action.condition:
    #         condition = eval(node_action.condition)
    #         condition += [('id', '=', res_id)]
    #         if self.env[model].search(condition):
    #             edges.append((node_action.sorce_node_id.id, node_action.target_node_id.id))
    #     else:
    #         edges.append((node_action.sorce_node_id.id, node_action.target_node_id.id))
    #
    # # 创建图
    # G = nx.DiGraph(edges)
    # # 整个审批流程的所有路径
    # all_paths = [path for path in nx.all_simple_paths(G, source=start_node.id, target=end_node.id)]
    #
    #
    # # 实际开始节点
    # start_node_id = start_node.id
    # instance = instance_obj.search([('res_id', '=', res_id), ('model_name', '=', model)], order='id desc', limit=1)  # 存在的实例
    # if instance:
    #     next_instance_node_id = instance.next_instance_node_id  # 下一实例开始节点
    #     if next_instance_node_id:
    #         start_node_id = next_instance_node_id
    #
    # real_paths = [path[path.index(start_node_id):] for path in all_paths]
    #
    # edges = []  # 边
    # for path in real_paths:
    #     for i in range(len(path) - 1):
    #         edge = (path[i], path[i + 1])
    #
    #         if edge not in edges:
    #             edges.append(edge)
    #
    # # 创建图
    # G = nx.DiGraph(edges)
    # in_degree = {} # 入度
    # for source, target in edges:
    #     in_degree.setdefault(target, []).append(source)
    #
    # # 入度为0的节点
    # source = [v for v, d in G.in_degree() if d == 0]
    # [in_degree.update({s: []}) for s in source]
    #
    # paths = []
    # serial_num = 0
    # while source:
    #     for s in source:
    #         in_degree.pop(s)
    #         paths.append({
    #             'node_id': s,
    #             'serial_num': serial_num
    #         })
    #         for d in in_degree.keys():
    #             if s in in_degree[d]:
    #                 in_degree[d].remove(s)
    #
    #     source = [v for v in in_degree.keys() if len(in_degree[v]) == 0]
    #     serial_num += 1
    #
    # _logger.info(u'审批路径：%s', json.dumps(paths, indent=4))
    # if not paths:
    #     return
    #
    # # 是否已提交审批审请
    # self._cr.execute("UPDATE %s SET is_commit_approval = TRUE, approval_state = 'draft' WHERE id = %s" % (self._table, res_id))
    # # 创建审批流程实例
    # instance = instance_obj.create({
    #     'flow_id': approval_flow.id,
    #     'res_id': res_id,
    #     'model_name': model,
    #     'state': 'active',
    #     'str_node_ids': json.dumps(paths)
    # })
    # # 创建实例节点
    # paths.sort(key=lambda x: x['serial_num'])
    # # 不是开始节点(is_start=False)的最小的序号
    # min_serial_num = 0
    # for path in paths:
    #     node_id = path['node_id']
    #     node = self.env['approval.flow.node'].browse(node_id)
    #     if node.is_start:
    #         continue
    #
    #     min_serial_num = path['serial_num']
    #     break
    #
    # for path in paths:
    #     node_id = path['node_id']
    #     node = self.env['approval.flow.node'].browse(node_id)
    #     if node.is_start or node.is_end:
    #         continue
    #
    #     instance_node = instance_node_obj.create({
    #         'flow_id': approval_flow.id,
    #         'node_id': path['node_id'],
    #         'instance_id': instance.id,
    #         'serial_num': path['serial_num'],
    #         'state': 'running' if path['serial_num'] == min_serial_num else 'active'
    #     })
    #
    #
    #     # 创建待审批
    #     for user in node.groups_id.users:
    #         wait_approval_obj.create({
    #             'instance_node_id': instance_node.id,
    #             'apply_id': self.env.user.id,
    #             'user_id': user.id
    #         })
    #





