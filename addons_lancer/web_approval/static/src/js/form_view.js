odoo.define('web.approval_form_view', function (require) {
    var FormView = require('web.FormView');
    var data = require('web.data');
    // var Model = require('web.Model');
    var Model = require('web.DataModel');
    var session = require('web.session');
    var Dialog = require('web.Dialog');
    var core = require('web.core');
    var View = require('web.View');
    var FilterMenu = require('web.FilterMenu');
    var QWeb = core.qweb;
    var ActionManager = require('web.ActionManager');
    // var search_inputs = require('web.search_inputs');
    var data_manager = require('web.data_manager');

    ActionManager.include({
        ir_actions_act_window_close: function (action, options) {
            if (!this.dialog) {
                options.on_close();
            }
            this.dialog_stop(action);
            return $.when();
        }
    });

    /*
    * 窗体审批部分
    * */
    $.extend(View.prototype.events, {
        // 审批
        'click button.btn-approval': function (ev) {
            ev.preventDefault();
            this.do_approval($(ev.currentTarget).data('instance_node_id'));
        },
        // 加签
        'click button.btn-increase': function (ev) {
            ev.preventDefault();
            var self = this;
            this.do_action({
                name: '加签',
                type: 'ir.actions.act_window',
                view_type: 'form',
                view_mode: 'form',
                res_model: 'approval.increase.wizard',
                views: [[false, 'form']],
                target: 'new',
                context: {
                    instance_node_id: $(ev.currentTarget).data('instance_node_id')
                }
            }, {
                on_close: function(data) {
                    if(data && data.state)
                    self.get_approval_flow()
                }
            })
        },
        // 删除加签
        'click button.btn-delete-increase': function (ev) {
            ev.preventDefault();
            var self = this;
            Dialog.confirm(this, '确认要删除该加签节点吗？', {
                confirm_callback: function () {
                    self.delete_increase_node($(ev.currentTarget).data('instance_node_id'));
                }
            });
        },
        // 转签
        'click button.btn-turn-to': function (ev) {
            ev.preventDefault();
            var self = this;
            this.do_action({
                name: '转签',
                type: 'ir.actions.act_window',
                view_type: 'form',
                view_mode: 'form',
                res_model: 'approval.turn.to.wizard',
                views: [[false, 'form']],
                target: 'new',
                context: {
                    instance_node_id: $(ev.currentTarget).data('instance_node_id')
                }
            }, {
                on_close: function(data) {
                    if(data && data.state)
                    self.get_approval_flow()
                }
            })
        },
        // 删除转签
        'click button.btn-delete-turn-to': function (ev) {
            ev.preventDefault();
            var self = this;
            Dialog.confirm(this, '确认要删除该转签节点吗？', {
                confirm_callback: function () {
                    self.delete_turn_to_node($(ev.currentTarget).data('instance_node_id'));
                }
            });
        },
        // 编辑转签
        'click button.btn-edit-turn-to': function (ev) {
            ev.preventDefault();
            var self = this;
            this.do_action({
                name: '编辑转签',
                type: 'ir.actions.act_window',
                view_type: 'form',
                view_mode: 'form',
                res_model: 'approval.edit.turn.to.wizard',
                views: [[false, 'form']],
                target: 'new',
                context: {
                    instance_node_id: $(ev.currentTarget).data('instance_node_id')
                }
            }, {
                on_close: function(data) {
                    if(data && data.state)
                    self.get_approval_flow()
                }
            })
        },
        // 编辑审批
        'click button.btn-edit-approval': function (ev) {
            ev.preventDefault();
            this.do_edit_approval($(ev.currentTarget).data('approval_id'));
        }
    });


    FormView.include({
        do_execute_action: function (action_data, dataset, record_id, on_closed) {
            if(['commit_approval', 'pause_approval', 'resume_approval'].includes(action_data.type)){
                return this.control_approval(record_id, action_data.type);
            }
            if(action_data.type === 'cancel_approval'){
                return this.cancel_approval(record_id);
            }
            else if(action_data.type === 'approval'){
                var instance_node_id = $('.btn-do-approval').data('instance_node_id');
                if(instance_node_id === ''){
                    return
                }
                return this.do_approval(instance_node_id);
            }
            // else if(action_data.type === 'config_approval_can_run'){
            //     if(!this.fields.model_id.get_value()){
            //         return Dialog.alert(this, '请选择模型！');
            //     }
            //     return this.config_approval_can_run();
            // }
            // else if(action_data.type === 'config_approval_cannot_run'){
            //
            // }
            else{
                return this._super.apply(this, arguments)
            }
        },
        cancel_approval: function (record_id) {
            var def = new $.Deferred();
            var self = this;
            Dialog.confirm(this, '确认要取消审批吗？', {
                confirm_callback: function () {
                    def.resolve();
                    self.control_approval(record_id, 'cancel_approval');
                },
                cancel_callback: function () {
                    def.resolve();
                }
            });
            return def;
        },
        do_push_state: function(state) {
            this._super(state);
            this.init_config_condition();

            var btn_commit = $('.btn-commit-approval', this.$el);
            if(btn_commit.length === 0){
                return
            }
            $('.approval-wizard', this.$el).remove();

            // 创建时
            if(this.datarecord.id === undefined){
                btn_commit.addClass('o_form_invisible');
                $('.btn-pause-approval', this.$el).addClass('o_form_invisible');
                $('.btn-cancel-approval', this.$el).addClass('o_form_invisible');
                $('.btn-resume-approval', this.$el).addClass('o_form_invisible');
                $('.btn-do-approval', this.$el).addClass('o_form_invisible');
                return
            }
            this.get_approval_flow()

        },
        do_approval: function (instance_node_id) {
            var self = this;
            return this.do_action({
                name: '审批',
                type: 'ir.actions.act_window',
                view_type: 'form',
                view_mode: 'form',
                res_model: 'approval.wizard',
                views: [[false, 'form']],
                target: 'new',
                context: {
                    model: this.model,
                    res_id: this.datarecord.id,
                    instance_node_id: instance_node_id
                }
            }, {
                on_close: function(data) {
                    if(data && data.state)
                    self.get_approval_flow()
                }
            })
        },
        do_edit_approval: function (approval_id) {
            var self = this;
            return this.do_action({
                name: '编辑审批',
                type: 'ir.actions.act_window',
                view_type: 'form',
                view_mode: 'form',
                res_model: 'edit.approval.wizard',
                views: [[false, 'form']],
                target: 'new',
                context: {
                    model: this.model,
                    res_id: this.datarecord.id,
                    approval_id: approval_id
                }
            }, {
                on_close: function(data) {
                    if(data && data.state)
                    self.get_approval_flow()
                }
            })
        },
        control_approval: function (id, type) {
            var self = this;
            return session.rpc('/web/dataset/control_approval', {
                model: this.model,
                res_id: id,
                action_type: type
            }).then(function () {
                self.get_approval_flow()
            });
        },

        toggle_approval_buttons: function (show_commit_btn, show_buttons, approval_state) {
                var btn_commit = $('.btn-commit-approval', this.$el); // 提交审批
                var btn_pause = $('.btn-pause-approval', this.$el); // 暂停
                var btn_cancel = $('.btn-cancel-approval', this.$el); // 取消
                var btn_resume = $('.btn-resume-approval', this.$el); // 恢复
                // 显示提交审核按钮 显示暂停审核按钮
                if (show_commit_btn){
                    btn_commit.removeClass('o_form_invisible');
                }
                else{
                    btn_commit.addClass('o_form_invisible');
                }
                if(show_buttons){
                    if(approval_state === ''){
                        btn_pause.addClass('o_form_invisible');
                        btn_cancel.addClass('o_form_invisible');
                        btn_resume.addClass('o_form_invisible');
                    }
                    else if(approval_state === 'active'){
                        btn_pause.removeClass('o_form_invisible');
                        btn_cancel.removeClass('o_form_invisible');
                        btn_resume.addClass('o_form_invisible');
                    }
                    else if(approval_state === 'complete'){
                        btn_pause.addClass('o_form_invisible');
                        btn_cancel.addClass('o_form_invisible');
                        btn_resume.addClass('o_form_invisible');
                    }
                    else if(approval_state === 'cancel'){
                        btn_pause.addClass('o_form_invisible');
                        btn_cancel.addClass('o_form_invisible');
                        btn_resume.addClass('o_form_invisible');
                    }
                    // 暂停状态
                    else {
                        btn_pause.addClass('o_form_invisible');
                        btn_cancel.removeClass('o_form_invisible');
                        btn_resume.removeClass('o_form_invisible');
                    }
                }
                else{
                    btn_pause.addClass('o_form_invisible');
                    btn_cancel.addClass('o_form_invisible');
                    btn_resume.addClass('o_form_invisible');
                }
        },
        get_approval_flow: function () {
            var form_view = this.$el;

            var self = this;
            session.rpc('/web/dataset/get_approval_flow', {
                model: this.model,
                res_id: this.datarecord.id
            }).then(function (data) {

                self.toggle_approval_buttons(data.show_commit_btn, data.show_buttons, data.approval_state);

                // 显示审批流
                var btn_approval = $('.btn-do-approval', self.$el); // 审批按钮
                btn_approval.removeData('instance_node_id');
                btn_approval.addClass('o_form_invisible');
                if(data.instance_nodes.length > 0){
                    $('.approval-wizard', self.$el).remove();
                    var html = $(QWeb.render('ApprovalTemplate', {
                        instance_nodes: data.instance_nodes,
                        approval_state: data.approval_state
                    }));
                    // 在.o_form_view内添加审批流程
                    // 对于o_form_view 有o_form_nosheet视图， 添加到o_form_view最后
                    // 否则 如果o_form_view内存在oe_chatter，则在oe_chatter之前添加，否则添加到o_form_view最后
                    if(form_view.hasClass('o_form_nosheet')){
                        form_view.append(html)
                    }
                    else{
                        var chatter = $('.oe_chatter', form_view);
                        if(chatter.length > 0){
                            chatter.before(html)
                        }
                        else{
                            form_view.append(html)
                        }
                    }

                    data.instance_nodes.forEach(function (node) {
                        if(node.can_approval){
                            btn_approval.removeClass('o_form_invisible');
                            btn_approval.data('instance_node_id', node.id)
                        }
                    })
                }

            })
        },
        delete_increase_node: function (instance_node_id) {
            var self = this;
            new data.DataSet(this, 'approval.flow.instance.node').call('delete_increase_node', [instance_node_id]).done(function (data) {
                self.get_approval_flow()
            });
        },
        delete_turn_to_node: function (instance_node_id) {
            var self = this;
            new data.DataSet(this, 'approval.flow.instance.node').call('delete_turn_to_node', [instance_node_id]).done(function (data) {
                self.get_approval_flow()
            });
        }
    });

    /*
    * 审批流程部分
    * */
    FormView.include({
        init: function() {
            this._super.apply(this, arguments);
            this.bind_trigger_event();

        },
        start: function() {
            var def = this._super();
            if(this.model === 'approval.flow'){
                this.filter_menu = new FilterMenu(this, []);
            }
            return def
        },
        // config_approval_can_run: function () {
        //     var def = new $.Deferred();
        //         var self = this;
        //         this.do_action({
        //             name: '加签',
        //             type: 'ir.actions.act_window',
        //             view_type: 'form',
        //             view_mode: 'form',
        //             res_model: 'approval.increase.wizard',
        //             views: [[false, 'form']],
        //             target: 'new',
        //             context: {
        //                 instance_node_id: 23
        //             }
        //         }, {
        //             on_close: function(data) {
        //                 def.resolve();
        //                 if(data && data.state)
        //                 self.get_approval_flow()
        //             }
        //         });
        //
        //     return def;
        // },
        bind_trigger_event: function () {
            if(this.model === 'approval.flow') {
                this.ir_models = {};
                this.on("to_edit_mode", this, this.change_to_edit_mode);
                this.on("on_button_cancel", this, this.exit_edit_mode);
                this.on("to_view_mode", this, this.exit_edit_mode);
                this.on("load_record", this, function () {
                    if (this.get('actual_mode') === 'create') {
                        this.change_to_edit_mode();
                    }
                    else {
                        this.exit_edit_mode();
                    }
                });
                this.on('field_changed:model_id', this, this.model_id_changed);
            }
        },
        get_ir_model: function (def, model_id) {
            var model_name = this.ir_models[model_id];
            if(model_name){
                def.resolve();
            }
            else{
                var self = this;
                new Model('ir.model').call('read', [[self.fields.model_id.get_value()], ['model']]).then(function (fields) {
                    self.ir_models[fields[0].id] = fields[0].model;
                    def.resolve();
                });
            }
            return def;

        },
        model_id_changed: function () {
            var self = this;
            this.fields.condition.set_value('');
            this.fields.approval_can_run.set_value('');
            this.fields.approval_cannot_run.set_value('');
            _.invoke(this.filter_menu.propositions, 'destroy');
            this.filter_menu.propositions = [];
            var model_id = this.fields.model_id.get_value();
            if(!model_id)
                return;

            var def = new $.Deferred();
            $.when(self.get_ir_model(def, model_id)).done(function () {
                var model_name = self.ir_models[model_id];
                var dataset = new data.DataSet(self, model_name);
                data_manager.load_fields(dataset).then(function (data) {
                    var fields = {
                        id: { string: 'ID', type: 'id', searchable: true }
                    };
                    _.each(data, function(field_def, field_name) {
                        if (field_def.selectable !== false && field_name !== 'id') {
                            fields[field_name] = field_def;
                        }
                    });
                    return fields;
                });
            });
        },
        change_to_edit_mode: function () {
            $('.config_condition', this.$el).removeClass('o_form_invisible');
            $('.config_approval_can_run', this.$el).removeClass('o_form_invisible');
            $('.config_approval_cannot_run', this.$el).removeClass('o_form_invisible');
        },
        exit_edit_mode: function () {
            $('.config_condition', this.$el).addClass('o_form_invisible');
            $('.config_approval_can_run', this.$el).addClass('o_form_invisible');
            $('.config_approval_cannot_run', this.$el).addClass('o_form_invisible');
        },
        init_config_condition: function () {
            if(this.model === 'approval.flow'){
                var config_condition = $('.config_condition');
                if(config_condition.length === 0){
                    return
                }
                if(config_condition.children().length === 0){
                    this.filter_menu.appendTo(config_condition);
                    $('.caret', config_condition).remove();
                    $('button.o_dropdown_toggler_btn', config_condition).addClass('oe_link');
                    this.override_get_fields();
                    this.redelegate_events();
                }
            }
        },
        redelegate_events: function () {
            this.filter_menu.undelegateEvents();
            var self = this;
            var events = {
                'click .o_add_filter': function (event) {
                    event.preventDefault();
                    if(self.fields.model_id.get_value()){
                        self.filter_menu.toggle_custom_filter_menu();
                    }
                    else{
                        Dialog.alert(self, '请选择模型！');
                    }
                },
                'click li': function (event) {
                    event.preventDefault();
                    event.stopImmediatePropagation();
                },
                'hidden.bs.dropdown': function () {
                    self.filter_menu.toggle_custom_filter_menu(false);
                },
                'click .o_add_condition': 'append_proposition',
                'click .o_apply_filter': function (ev) {
                    var filters = _.map(this.propositions, function (proposition) {
                        var field = proposition.attrs.selected;
                        var op_select = proposition.$('.o_searchview_extended_prop_op')[0];
                        var operator = op_select.options[op_select.selectedIndex];
                        return proposition.value.get_domain(field, operator);
                    });
                    if(filters.length === 0)
                        return;


                    for(var i = 0, l = filters.length - 1; i < l; i++){
                        filters.unshift('|');
                    }

                    var domains = [];

                    for(i = 0, l = filters.length; i < l; i++){
                        if(filters[i] instanceof Array){
                            domains.push(filters[i][0])
                        }
                        else{
                            domains.push(filters[i])
                        }
                    }
                    var condition = JSON.parse(self.fields.condition.get_value() || '[]');
                    condition = condition.concat(domains);
                    self.fields.condition.set_value(JSON.stringify(condition));

                    _.invoke(this.propositions, 'destroy');
                    this.propositions = [];
                    this.append_proposition();
                    this.toggle_custom_filter_menu(false);

                },
            };
            for(var key in events) {

                var method = this.filter_menu.proxy(events[key]);

                var match = /^(\S+)(\s+(.*))?$/.exec(key);
                var event = match[1];
                var selector = match[3];

                event += '.widget_events';
                if (!selector) {
                    this.filter_menu.$el.on(event, method);
                } else {
                    this.filter_menu.$el.on(event, selector, method);
                }
            }
        },
        override_get_fields: function () {
            var self = this;

            this.filter_menu.get_fields = function () {
                var model_id = self.fields.model_id.get_value();
                var model_name = self.ir_models[model_id];
                var dataset = new data.DataSet(self, model_name);
                this._fields_def = data_manager.load_fields(dataset).then(function (data) {
                    var fields = {
                        id: { string: 'ID', type: 'id', searchable: true }
                    };
                    _.each(data, function(field_def, field_name) {
                        if (field_def.selectable !== false && field_name !== 'id') {
                            fields[field_name] = field_def;
                        }
                    });
                    return fields;
                });
                return this._fields_def
            };
        },
    });
});