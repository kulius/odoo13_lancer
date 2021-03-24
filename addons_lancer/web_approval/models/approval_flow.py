# coding=utf8
import sys
import json
from odoo import models, api, fields
from odoo.exceptions import ValidationError
import inspect


class TestCls(object):
    @classmethod
    def class_method(cls):
        pass

    @staticmethod
    def static_method():
        pass

    def general_method(self):
        pass


class ApprovalFlow(models.Model):
    _name = 'approval.flow'
    _description = u'审批流程'

    def _compute_domain(self):
        all_cls = inspect.getmembers(sys.modules[__name__], inspect.isclass)
        odoo_cls = [getattr(cls[1], '_name') for cls in all_cls if cls[1].__bases__[0].__name__ == 'Model'] # 排除当前的对象
        odoo_cls += [model.model for model in self.env['ir.model'].search([('transient', '=', True)])] # 排除临时对象

        return [('model', 'not in', odoo_cls)]

    name = fields.Char('名称')
    model_id = fields.Many2one('ir.model', '模型', domain=_compute_domain, index=1)
    condition = fields.Char('条件', help='请遵循odoo的domain的写法，如：[("field_name", "=", value)]')
    on_create = fields.Boolean('创建时', default=False, help='记录创建时创建审批流程')
    company_ids = fields.Many2many('res.company', 'approval_flow_company_rel', 'flow_id', 'company_id', '适用公司')

    node_ids = fields.One2many('approval.flow.node', 'flow_id', '流程节点')
    action_ids = fields.One2many('approval.flow.node.action', 'flow_id', '节点动作')

    commit_approval_group_id = fields.Many2one('res.groups', '提交审批组', help='执行提交审批的组，如果未指定，则记录所属公司的所有用户都可以提交审批')

    approval_can_run = fields.Char('审批后运行', help='审批流程完成后才能执行的功能，比如审核等，用英文逗号间隔')
    approval_cannot_run = fields.Char('审批前执行', help='审批流程完成后不能能执行的功能，比如修改、删除等，用英文逗号间隔')

    act_window_ids = fields.Many2many('ir.actions.act_window', 'approval_flow_act_window_rel', 'flow_id', 'act_window_id', '审批后执行的动作')

    accept_template = fields.Text('同意模板')
    refuse_template = fields.Text('拒绝模板')






    @api.model
    def create(self, vals):
        vals['node_ids'].append((0, False, {'name': '开始', 'is_start': True, 'is_end': False}))
        vals['node_ids'].append((0, False, {'name': '结束', 'is_start': False, 'is_end': True}))

        # if len([node for node in vals['node_ids'] if node[2]['is_start']]) == 0:
        #     vals['node_ids'].append((0, False, {'name': '开始', 'is_start': True, 'is_end': False}))
        #
        # # 不存在结束节点
        # if len([node for node in vals['node_ids'] if node[2]['is_end']]) == 0:
        #     vals['node_ids'].append((0, False, {'name': '结束', 'is_start': False, 'is_end': True}))

        if vals['approval_can_run']:
            vals['approval_can_run'] = ','.join([f.strip() for f in vals['approval_can_run'].split(',')])

        if vals['approval_cannot_run']:
            vals['approval_cannot_run'] = ','.join([f.strip() for f in vals['approval_cannot_run'].split(',')])

        res = super(ApprovalFlow, self).create(vals)

        # 检查条件
        res.check_condition(vals.get('condition'))
        # 检查审批后运行
        res.check_approval_can_run(vals.get('approval_can_run'))
        # 检查审批后不能运行
        res.check_approval_cannot_run(vals.get('approval_cannot_run'))

        return res


    def write(self, vals):
        # 检查条件
        self.check_condition(vals.get('condition'))
        # 检查审批后运行
        self.check_approval_can_run(vals.get('approval_can_run'))
        # 检查审批后不能运行
        self.check_approval_cannot_run(vals.get('approval_cannot_run'))

        if vals.get('approval_can_run'):
            vals['approval_can_run'] = ','.join([f.strip() for f in vals['approval_can_run'].split(',')])

        if vals.get('approval_cannot_run'):
            vals['approval_cannot_run'] = ','.join([f.strip() for f in vals['approval_cannot_run'].split(',')])

        return super(ApprovalFlow, self).write(vals)

    @api.onchange('on_create')
    def onchange_on_create(self):
        self.commit_approval_group_id = False

    def get_approval_flow(self, model, res_id):
        """ 得到审批流"""
        model_id = self.env['ir.model'].sudo().search([('model', '=', model)]).id

        document = self.env[model].browse(res_id) # 当前单据

        # 有适用公司有条件的审批流程
        flows = self.search([('model_id', '=', model_id), ('company_ids', '!=', False), ('condition', '!=', False)], order='id desc')
        for flow in flows:
            if document.company_id.id in flow.company_ids.ids:
                ids = self.env[model].search(eval(flow.condition)).ids
                if res_id in ids:
                    return flow


        # 有适用公司无条件的审批流程
        flows = self.search([('model_id', '=', model_id), ('company_ids', '!=', False), ('condition', '=', False)], order='id desc')
        for flow in flows:
            if document.company_id.id in flow.company_ids.ids:
                return flow


        # 无适用公司有条件的审批流程
        flows = self.search([('model_id', '=', model_id), ('company_ids', '=', False), ('condition', '!=', False)], order='id desc')
        for flow in flows:
            ids = self.env[model].search(eval(flow.condition)).ids
            if res_id in ids:
                return flow

        # 无适用公司无条件的审批流程
        flows = self.search([('model_id', '=', model_id), ('company_ids', '=', False), ('condition', '=', False)], order='id desc')
        if flows:
            return flows[0]

    def check_approval_can_run(self, approval_can_run):
        if not approval_can_run:
            return

        member = TestCls.__dict__

        exclude_types = [type(member[m]) for m in ['general_method', 'class_method', 'static_method']]
        exclude_methods = [n for n, t in models.BaseModel.__dict__.items() if type(t) in exclude_types]
        exclude_methods.sort()
        approval_can_run = map(lambda x: x.strip(), approval_can_run.split(','))
        model = self.env[self.model_id.model]
        methods = [method[0] for method in inspect.getmembers(model, predicate=inspect.ismethod) if method[0] not in exclude_methods]

        for f in approval_can_run:
            if f not in methods:
                raise ValidationError(u"'%s'不存在方法：'%s'" % (self.model_id.name, f))

    def check_approval_cannot_run(self, approval_cannot_run):
        if not approval_cannot_run:
            return

        member = TestCls.__dict__

        exclude_types = [type(member[m]) for m in ['general_method', 'class_method', 'static_method']]
        exclude_methods = [n for n, t in models.BaseModel.__dict__.items() if type(t) in exclude_types]
        exclude_methods.sort()
        approval_cannot_run = map(lambda x: x.strip(), approval_cannot_run.split(','))
        model = self.env[self.model_id.model]
        methods = [method[0] for method in inspect.getmembers(model, predicate=inspect.ismethod) if method[0] not in exclude_methods]
        methods += ['write', 'unlink']

        for f in approval_cannot_run:
            if f not in methods:
                raise ValidationError(u"'%s'不存在方法：'%s'" % (self.model_id.name, f))

    def check_condition(self, condition):
        if not condition:
            return

        try:
            self.env[self.model_id.model].search(eval(condition))
        except Exception as e:
            raise ValidationError("审批流程条件表达式：'%s'错误！" % condition)


class ApprovalFlowNode(models.Model):
    _name = 'approval.flow.node'
    _description = u'流程节点'

    flow_id = fields.Many2one('approval.flow', '流程', ondelete='cascade')
    name = fields.Char('名称')
    is_start = fields.Boolean('流程开始')
    is_end = fields.Boolean('流程结束')

    groups_id = fields.Many2one('res.groups', '节点执行组')
    is_all_approval = fields.Boolean('需全组审批', default=False)
    only_document_company = fields.Boolean('仅单据公司', default=True)

    duration = fields.Integer('审批时效', default=0)
    allow_before_increase = fields.Boolean('允许前加签', default=False)
    allow_after_increase = fields.Boolean('允许后加签', default=False)
    allow_turn_to = fields.Boolean('允许转签', default=False)

    action_in_ids = fields.One2many('approval.flow.node.action', 'target_node_id', '入动作')
    action_out_ids = fields.One2many('approval.flow.node.action', 'sorce_node_id', '出动作')


    @api.onchange('is_start', 'is_end')
    def onchange_is_start(self):
        self.user_id = False
        self.groups_id = False
        self.is_all_approval = False

    @api.model
    def create(self, vals):
        res = super(ApprovalFlowNode, self).create(vals)
        if vals.get('is_start'):
            if len(self.search([('flow_id', '=', vals['flow_id']), ('is_start', '=', True)])) > 1:
                raise ValidationError(u'审批流程只能有一个开始节点！')

        if vals.get('is_end'):
            if len(self.search([('flow_id', '=', vals['flow_id']), ('is_end', '=', True)])) > 1:
                raise ValidationError(u'审批流程只能有一个结束节点！')

        return res


    def write(self, vals):
        res = super(ApprovalFlowNode, self).write(vals)

        if len(self.search([('flow_id', '=', self.flow_id.id), ('is_start', '=', True)])) > 1:
            raise ValidationError(u'审批流程只能有一个开始节点！')

        if len(self.search([('flow_id', '=', self.flow_id.id), ('is_end', '=', True)])) > 1:
            raise ValidationError(u'审批流程只能有一个结束节点！')

        return res


    def unlink(self):
        if self.is_start or self.is_end:
            raise ValidationError('开始节点和结束节点不能删除！')

        return super(ApprovalFlowNode, self).unlink()


    def name_get(self):
        res = []
        for node in self:
            res.append((node.id, str(node.id) + '/' + node.name))
        return res

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        """只显示收银管理员"""
        if 'dont_show_start_end' in self.env.context:
            args = args or []
            args += [('is_start', '=', False), ('is_end', '=', False)]

        return super(ApprovalFlowNode, self).search(args, offset=offset, limit=limit, order=order, count=count)


class ApprovalFlowNodeAction(models.Model):
    _name = 'approval.flow.node.action'
    _description = u'节点动作'

    flow_id = fields.Many2one('approval.flow', '流程', ondelete='cascade')
    action_type = fields.Selection([('accept', '同意'), ('refuse', '拒绝')], '动作类型')
    condition = fields.Char('条件')
    sorce_node_id = fields.Many2one('approval.flow.node', '源节点', ondelete='cascade')
    target_node_id = fields.Many2one('approval.flow.node', '目标节点', ondelete='cascade')

    @api.model
    def create(self, vals):
        # 检查动作
        self.check_action(vals['flow_id'], vals['action_type'], vals['sorce_node_id'], vals['target_node_id'])

        res = super(ApprovalFlowNodeAction, self).create(vals)

        # 检查condition
        res.check_condition(vals.get('condition'))

        return res


    def write(self, vals):
        # 检查condition
        self.check_condition(vals.get('condition'))

        res = super(ApprovalFlowNodeAction, self).write(vals)
        # 检查动作
        self.check_action(self.flow_id.id, self.action_type, self.sorce_node_id.id, self.target_node_id.id, self.id)

        return res

    def check_condition(self, condition):
        if not condition:
            return

        try:
            self.env[self.flow_id.model_id.model].search(eval(condition))
        except Exception:
            raise ValidationError('节点动作条件表达式错误！')

    def check_action(self, flow_id, action_type, sorce_node_id, target_node_id, exclude_id=None):
        domain = [('flow_id', '=', flow_id), ('action_type', '=', action_type), ('sorce_node_id', '=', sorce_node_id),
                  ('target_node_id', '=', target_node_id)]

        if exclude_id:
            domain += [('id', '!=', exclude_id)]

        if self.search(domain):
            raise ValidationError(u'动作已经存在!')

        # 源节点和目标结点不能相同
        if sorce_node_id == target_node_id:
            raise ValidationError(u'源节点和目标结点不能相同!')

        # 开始节点和结束节点之前不能建立动作
        source_node = self.env['approval.flow.node'].browse(sorce_node_id)
        target_node = self.env['approval.flow.node'].browse(target_node_id)
        if (source_node.is_start and target_node.is_end) or (source_node.is_end and target_node.is_start):
            raise ValidationError(u'源节点和目标节点之前不能建立连接！')

        if source_node.is_start and action_type == 'refuse':
            raise ValidationError('开始节点不能建立拒绝动作！')

        if target_node.is_end and action_type == 'refuse':
            raise ValidationError('结束节点不能建立拒绝动作！')


class ApprovalFlowInstance(models.Model):
    _name = "approval.flow.instance"
    _description = u'审批流实例'

    flow_id = fields.Many2one('approval.flow', string='审批流程', ondelete='cascade', index=True)
    res_id = fields.Integer('模型ID')
    model_name = fields.Char('模型')
    state = fields.Selection([('active', '激活'), ('complete', '完成')], default='active')

    next_instance_node_id = fields.Integer('下一实例开始节点')

    str_node_ids = fields.Char('审批节点')


class ApprovalFlowInstanceNode(models.Model):
    _name = "approval.flow.instance.node"
    _description = u"审批流实例节点"

    flow_id = fields.Many2one('approval.flow', string='审批流程', ondelete='cascade', index=True)
    node_id = fields.Many2one('approval.flow.node', string='节点', ondelete="cascade", index=True)
    instance_id = fields.Many2one('approval.flow.instance', string='实例', ondelete="cascade", index=True)
    state = fields.Selection([('active', '草稿'), ('running', '正在审批'), ('complete', '完成'), ('turn_to', '转签')], index=True, string='状态', default='active')

    res_id = fields.Integer('记录ID', related='instance_id.res_id', store=1)
    model_name = fields.Char('模型', related='instance_id.model_name', store=1)

    serial_num = fields.Integer('序号')

    approval_ids = fields.One2many('approval', 'instance_node_id', '审批')

    # ####加签相关
    is_increase = fields.Boolean('是加签')
    user_id = fields.Many2one('res.users', '加签审批人或转签审批人')
    allow_increase_user_id = fields.Many2one('res.users', '加签申请人或转签申请人', help='由谁提出的加签或由谁提出的转签')
    parent_id = fields.Many2one('approval.flow.instance.node', '关联节点')
    increase_type = fields.Char('加签类型')

    # 转签
    is_turn_to = fields.Boolean('是转签')


    @api.model
    def delete_increase_node(self, instance_node_id):
        """删除加签节点"""
        instance_node = self.browse(instance_node_id)

        # 被删节点后的节点的serial_num字段值减1
        for inn in self.search([('instance_id', '=', instance_node.instance_id.id)]):
            if inn.serial_num > instance_node.serial_num:
                inn.serial_num -= 1

        # 更新instance_node.instance_id.str_node_ids字段内容
        str_node_ids = json.loads(instance_node.instance_id.str_node_ids)
        delete_node = None
        for nn in str_node_ids:
            if nn['serial_num'] > instance_node.serial_num:
                nn['serial_num'] -= 1

            if nn.get('parent_id') == instance_node.parent_id.id and nn.get('increase_type') == instance_node.increase_type:
                delete_node = nn

        if delete_node:
            str_node_ids.remove(delete_node)

        str_node_ids.sort(key=lambda x: x['serial_num'])
        instance_node.instance_id.str_node_ids = json.dumps(str_node_ids)

        # if instance_node.state == 'running':
        #     instance_node.parent_id.state = 'running'
        instance_node.parent_id.state = instance_node.state
        instance_node.unlink()

        return True

    @api.model
    def delete_turn_to_node(self, instance_node_id):
        """删除转签节点"""
        instance_node = self.browse(instance_node_id)
        instance_node.parent_id.state = instance_node.state

        instance_node.unlink()

        return True



class Approval(models.Model):
    _name = 'approval'
    _description = u'审批'

    instance_node_id = fields.Many2one('approval.flow.instance.node', '实例节点', ondelete='cascade')
    action_id = fields.Many2one('approval.flow.node.action', '动作')
    action_type = fields.Char('动作')
    say = fields.Text('审批意见')

    user_id = fields.Many2one('res.users', '审批人')

    res_id = fields.Integer('模型ID', related='instance_node_id.res_id', store=1)
    model_name = fields.Char('模型', related='instance_node_id.model_name', store=1)


class WaitApproval(models.Model):
    _name = 'wait.approval'
    _description = u'待审批'

    instance_node_id = fields.Many2one('approval.flow.instance.node', '实例节点', ondelete='cascade')

    model_name = fields.Char('模型', related='instance_node_id.model_name', store=1, index=1)
    res_id = fields.Integer('记录ID', related='instance_node_id.res_id', store=1)
    serial_num = fields.Integer(string='顺序', related='instance_node_id.serial_num')
    state = fields.Selection([('active', ''), ('running', ''), ('complete', '')], index=True, string='状态', related='instance_node_id.state', store=1)

    apply_id = fields.Many2one('res.users', '申请人')

    user_id = fields.Many2one('res.users', '待审批用户', index=1)


class WaitApprovalSummary(models.Model):
    _name = 'wait.approval.summary'
    _description = u'待审批汇总'
    _auto = False

    model_id = fields.Many2one('ir.model', '模型', index=True, compute='_compute_model_id')
    model_name = fields.Char('模型')

    wait_approval_count = fields.Integer('待审批数据')

    res_ids = fields.Char('IDS')

    user_id = fields.Many2one('res.users', '待审批用户')

    def _compute_model_id(self):
        model_obj = self.env['ir.model']
        for summary in self:
            summary.model_id = model_obj.search([('model', '=', summary.model_name)]).id


    def init(self):
        self._cr.execute("""
        CREATE OR REPLACE VIEW wait_approval_summary AS (
            SELECT 
                ROW_NUMBER() OVER() AS id,
                model_name,
                user_id,
                COUNT(*) AS wait_approval_count,
                string_agg(res_id || '', ',') AS res_ids
            FROM wait_approval
            --WHERE state != 'turn_to'
            GROUP BY model_name, user_id
        )
        """)

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=80, order=None):
        domain = domain or []
        domain.append(('user_id', '=', self.env.user.id))

        fields = fields or []
        fields += ['res_ids', 'model_name']
        result = super(WaitApprovalSummary, self).search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order)

        res = []
        for r in result:
            ids = map(lambda x: int(x), r['res_ids'].split(','))
            count = len(self.env[r['model_name']].search([('id', 'in', ids)]))
            if count > 0:
                r['wait_approval_count'] = count
                res.append(r)


        return res



    def to_approval(self):
        self.ensure_one()

        res_ids = map(lambda x: int(x), self.res_ids.split(','))

        if len(res_ids) == 1:
            return {
                'name': u'%s审批' % self.model_id.name,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': self.model_id.model,
                # 'view_id': False,
                # 'views': [(False, 'form')],
                'type': 'ir.actions.act_window',
                'res_id': res_ids[0],
            }
        else:
            return {
                'name': u'%s审批' % self.model_id.name,
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': self.model_id.model,
                # 'view_id': False,
                # 'views': [(False, 'form'), (False, 'tree')],
                'type': 'ir.actions.act_window',
                'domain': [('id', 'in', res_ids)]
            }


class RecordApprovalState(models.Model):
    _name = 'record.approval.state'
    _description = u'记录审批状态'

    model = fields.Char('Model', index=1)
    res_id = fields.Integer('记录ID', index=1)
    approval_state = fields.Selection([('active', '活动'), ('complete', '完成'), ('pause', '暂停'), ('cancel', '取消')], '审批状态')
    is_commit_approval = fields.Boolean('是否提交审批', default=False)


class IncreaseType(models.Model):
    _name = 'increase.type'
    _description = u'加签类型'

    code = fields.Char('代码')
    name = fields.Char('名称')

