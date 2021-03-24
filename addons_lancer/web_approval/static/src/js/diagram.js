odoo.define('web_approval.DiagramView', function (require) {
    var View = require('web.View');
    var core = require('web.core');
    var Pager = require('web.Pager');
    var Dialog = require('web.Dialog');
    var data = require('web.data');
    var QWeb = core.qweb;

    var DiagramView = View.extend({
        display_name: '流程图',
        icon: 'fa-code-fork',
        multi_record: false,
        searchable: false,
        template: 'ApprovalDiagramView',
        start: function () {
            // 实例化jsPlumb
            this.instance = jsPlumb.getInstance({
                ConnectionOverlays: [
                    ["Arrow", {
                        location: 1,
                        id: "arrow",
                        width: 12,
                        length: 12
                    }],
                    ["Label", {id: "label", cssClass: "aLabel"}]
                ],
                Container: "diagramContainer"
            });

            return this._super();
        },
        destroy: function () {
            this.instance = null;
            this.$el.empty();
            return this._super.apply(this, arguments);
        },
        do_show: function() {
            this.do_push_state({});
            return $.when(this._super(), this.reload());
        },
        reload: function() {
            return this.dataset.read_index([], {})
                    .then(this.on_diagram_loaded)
                    .then(this.proxy('update_pager'));
        },
        render_pager: function($node) {
            var self = this;
            this.pager = new Pager(this, this.dataset.ids.length, this.dataset.index + 1, 1);
            this.pager.appendTo($node || this.options.$pager);
            this.pager.on('pager_changed', this, function (new_state) {
                self.pager.disable();
                self.dataset.index = new_state.current_min - 1;
                $.when(this.reload()).then(function () {
                    self.pager.enable();
                });
            });
        },
        render_buttons: function($node) {
            var self = this;

            this.$buttons = $(QWeb.render("ApprovalDiagramView.buttons", {'widget': this}));
            this.$buttons.on('click', '.o_diagram_new_button', function() {
                self.add_node();
            });

            this.$buttons.appendTo($node);
        },
        update_pager: function() {
            if (this.pager) {
                this.pager.update_state({
                    size: this.dataset.ids.length,
                    current_min: this.dataset.index + 1
                });
            }
        },
        on_diagram_loaded: function(record) {
            this.set({ 'title' : record.id ? record.name : '新建节点' });

            var id_record = record['id'];
            if (id_record) {
                this.id = id_record;
                this.get_diagram_info();
                this.do_push_state({id: id_record});
            } else {
                this.do_push_state({});
            }
        },
        get_diagram_info: function () {
            var self = this;
            var params = {
                flow_id: this.id
            };
            return this.rpc(
                '/web_approval/get_approval_info', params).done(function (result) {
                    self.actions = result.actions;
                    self.paths = result.paths;
                    self.draw_diagram();
                }
            );
        }

    });

    DiagramView.include({
        draw_diagram: function () {
            // 重置绘图区
            this.instance.reset();
            this.$el.empty();
            // 绘制节点
            this.draw_nodes();
            // 绘制连线
            this.draw_connector();
            // // 添加右键菜单
            // this.add_connection_menu();
            // this.add_node_menu();
        },
        operate_connection_node: function (id, operate, type) {
            var self = this, options, action;
            if(type === 'node'){
                var node = this.paths.filter(function (path) {
                    return path['node_id'] === parseInt(id)
                })[0];
                // 开始节点和结否节点不可以删除
                if(node['is_start'] || node['is_end']){
                    Dialog.alert(this, '开始节点和结束节点不能删除或编辑！');
                    return
                }
                if(operate === 'delete'){
                    options = {
                        confirm_callback: function () {
                            new data.DataSet(this, 'approval.flow.node')
                                .unlink([parseInt(id, 10)])
                                .done(function() {
                                    self.delete_node_done(id);
                                });
                        }
                    };
                    Dialog.confirm(this, '确认要删除该节点吗？', options);
                }
                if(operate === 'edit'){
                    action = {
                        name: '编辑节点',
                        type: 'ir.actions.act_window',
                        view_type: 'form',
                        view_mode: 'form',
                        res_model: 'edit.node.wizard',
                        views: [[false, 'form']],
                        target: 'new',
                        context: {
                            node_id: parseInt(id),
                            type: 'edit'
                        }
                    };
                    this.do_action(action, {
                        on_close: function(action) {
                            self.edit_node_done(action)
                        }
                    })
                }
            }
            else{
                if(operate === 'delete'){
                    options = {
                        confirm_callback: function () {
                            new data.DataSet(this, 'approval.flow.node.action')
                                .unlink([parseInt(id, 10)])
                                .done(function() {
                                    self.delete_connection_done(id);
                                });
                        }
                    };
                    Dialog.confirm(this, '确认要删除该动作吗？', options);
                }
                if(operate === 'edit'){
                    var a = this.actions.filter(function (t) {
                        return t.id === parseInt(id)
                    })[0];
                    if(a.action_type === 'refuse'){
                        return
                    }
                    action = {
                        name: '编辑动作',
                        type: 'ir.actions.act_window',
                        view_type: 'form',
                        view_mode: 'form',
                        res_model: 'edit.node.action.wizard',
                        views: [[false, 'form']],
                        target: 'new',
                        context: {node_action_id: parseInt(id)}
                    };
                    this.do_action(action, {
                        on_close: function(action) {
                            self.edit_connection_done(action)
                        }
                    })
                }
            }
        },
        add_node_menu: function () {
            var self = this;
            $.contextMenu({
                selector: '#diagramContainer .item',
                callback: function (key) {
                    self.operate_connection_node($(this).attr('id').replace('node_', ''), key, 'node')
                },
                items: {
                    "edit": {name: "编辑", icon: "edit"},
                    "delete": {name: "删除", icon: "delete"}
                }
            });
        },
        add_connection_menu: function () {
            var self = this;
            $.contextMenu({
                selector: '.jtk-connector',
                callback: function (key) {
                    self.operate_connection_node($(this).data('action_id'), key, 'contention')
                },
                items: {
                    "edit": {name: "编辑", icon: "edit"},
                    "delete": {name: "删除", icon: "delete"}
                }
            });
        },

        add_node: function () {
            var action = {
                name: '添加节点',
                type: 'ir.actions.act_window',
                view_type: 'form',
                view_mode: 'form',
                res_model: 'edit.node.wizard',
                views: [[false, 'form']],
                target: 'new',
                context: {
                    flow_id: this.id,
                    type: 'add'
                }
            };
            var self = this;
            this.do_action(action, {
                on_close: function(action) {
                    self.add_node_done(action)
                }
            })
        },
        add_node_done: function (result) {
            var action = result.action;
            if(action === undefined){
                return
            }
            // 绘制节点
            var end_node = this.paths.filter(function (path) {
                return path.is_end
            })[0];
            var serial_num = end_node.serial_num;

            end_node.serial_num++;
            this.paths.splice(this.paths.length - 1, 0, {
                node_id: action.id,
                serial_num: serial_num,
                node_name: action.name,
                is_start: false,
                is_end: false
            });
            this.draw_diagram();
        },
        edit_node_done: function (result) {
            var action = result.action;
            if(action === undefined){
                return
            }
            $('#node_' + action.id).text(action.name)
        },
        delete_node_done: function (node_id) {
            var id = 'node_' + node_id, self = this;
            // 删除与节点相关的连接
            this.instance.getConnections().forEach(function (connection) {
                if(connection.sourceId === id || connection.targetId === id){
                    self.instance.deleteConnection(connection)
                }
            });
            for(var i=0, l=this.paths.length; i<l; i++){
                if(this.paths[i].node_id === parseInt(node_id, 10)){
                    this.paths.splice(i, 1);
                    break;
                }
            }
            // 删除节点
            $('#' + id).remove();
            this.draw_diagram();
        },

        on_connection: function (info) {
            var source_node_id = parseInt(info.sourceId.replace('node_', '')), target_node_id = parseInt(info.targetId.replace('node_', ''));
            if(source_node_id === target_node_id){
                return
            }
            var source_node = {}, target_node = {};
            this.paths.forEach(function (path) {
                if(path.node_id === source_node_id){
                    source_node = path;
                }
                if(path.node_id === target_node_id){
                    target_node = path
                }
            });
            if((source_node.is_start && target_node.is_end) || (source_node.is_end && target_node.is_start)){
                Dialog.alert(this, '开始节点和结束节点不能建立连接！');
                return
            }

            var action = {
                name: '添加动作',
                type: 'ir.actions.act_window',
                view_type: 'form',
                view_mode: 'form',
                res_model: 'add.node.action.wizard',
                views: [[false, 'form']],
                target: 'new',
                context: {
                    source_node_id: source_node_id,
                    target_node_id: target_node_id,
                    source_serial_num: source_node.serial_num,
                    target_serial_num: target_node.serial_num,
                    flow_id: this.id
                }
            };
            var self = this;
            this.do_action(action, {
                on_close: function(action) {
                    self.add_connection_done(action)
                }
            })
        },
        add_connection_done: function (result) {
            var action = result.action;
            if(action === undefined){
                return
            }
            this.actions.push(action);
            if(action.action_type === 'accept'){
                this.draw_accept_connection(action);
            }
            else{
                this.draw_refuse_connection(action)
            }
        },
        edit_connection_done: function (result) {
            var action = result.action;
            if(action === undefined){
                return
            }
            this.actions.forEach(function (a) {
                if(a.id === action.id){
                    a['condition'] = action.condition
                }
            });
            this.instance.getConnections().forEach(function (connection) {
                var data = connection.getData();
                if(data.action_id === action.id){
                    var label = $(connection.getOverlay("label").getElement());
                    label.text(action.condition);
                    if(action.condition === ''){
                        label.hide();
                    }
                    else{
                        label.show()
                    }
                }
            });

        },
        delete_connection_done: function (action_id) {
            var self = this;
            this.instance.getConnections().forEach(function (connection) {
                var data = connection.getData();
                if(data.action_id === parseInt(action_id)){
                    self.instance.deleteConnection(connection)
                }
            });
        },
        draw_connector: function () {
            var self = this;
            this.instance.bind("connection", function (info) {
                var data = info.connection.getData();
                if(data.action_id !== undefined){
                    if(data.condition){
                        info.connection.getOverlay("label").setLabel(data.condition);
                    }
                    else{
                        $(info.connection.getOverlay("label").getElement()).hide();
                    }
                    $(info.connection.canvas).data('action_id', data.action_id);
                }
                // 新建: 删除连接，弹出新建连接对话框
                else{
                    self.instance.deleteConnection(info.connection);
                    self.on_connection(info)
                }
            });

            jsPlumb.getSelector("#diagramContainer .item").forEach(function (el) {
                self.instance.draggable(el); // 可拖动
                self.instance.makeSource(el, {
                    filter: ".ep"
                });
                self.instance.makeTarget(el);
            });
            this.actions.forEach(function (action) {
                if(action.action_type === 'accept'){
                    self.draw_accept_connection(action)
                }
                else{
                    // self.draw_refuse_connection(action)
                }
            });


        },
        draw_accept_connection: function (action) {
            this.instance.connect({
                source: "node_" + action.source_node_id,
                target: "node_" + action.target_node_id,
                anchors:[ "RightMiddle", "LeftMiddle" ],
                paintStyle:{ strokeWidth: 3, stroke: "#428bca" },
                connector:[ "Flowchart", { gap: 6, cornerRadius: 5, alwaysRespectStubs: false } ],
                hoverPaintStyle: {stroke: "#428bca", strokeWidth: 6},
                endpointStyle:{fill: '#428bca'},
                endpoint:["Dot", {radius: 6}],
                data: {
                    condition: action.condition,
                    action_id: action.id
                }
            });
        },
        draw_refuse_connection: function (action) {
            var is_left;
            this.paths.forEach(function (path) {
                if(path.node_id === action.source_node_id){
                    is_left = path.is_left
                }
            });
            this.instance.connect({
                source: "node_" + action.source_node_id,
                target: "node_" + action.target_node_id,
                anchors:is_left ? [ "LeftMiddle", "LeftMiddle" ] : ['RightMiddle', 'RightMiddle'],
                paintStyle:{ strokeWidth: 3, stroke: "#ff0000" },
                connector:[ "Flowchart", { stub: [10, 20], gap: 6, cornerRadius: 5, alwaysRespectStubs: true } ],
                hoverPaintStyle: {stroke: "#ff0000", strokeWidth: 6},
                endpointStyle:{fill: '#ff0000'},
                endpoint:["Dot", {radius: 6}],
                data: {
                    condition: action.condition,
                    action_id: action.id
                }
            });
        },

        draw_nodes: function () {
            //----------【1】将节点添加到容器-------------
            var container = this.$el;
            var max_serial_num = 0;
            this.paths.forEach(function (path) {
                var node = $(QWeb.render("ApprovalDiagramView.node", {'path': path}));
                node.appendTo(container);
                path.node_width = parseInt(node.css('width'));
                path.node_el = node;

                if(path.serial_num > max_serial_num)
                    max_serial_num = path.serial_num
            });

            //----------【2】计算节点间水平间隙---------
            var node_total_width = 0;
            var paths, max_node_width, node_total_height;
            for(var i = 0; i <= max_serial_num; i++){
                paths = this.paths.filter(function (path) {
                    return path.serial_num === i;
                });

                max_node_width = 0;
                paths.forEach(function (path) {
                    if(path.node_width > max_node_width)
                        max_node_width = path.node_width
                });
                node_total_width += max_node_width;
            }

            var container_height = parseInt(container.css('height')); // 容器高度
            var container_width = parseInt(container.css('width')); // 容器宽度

            var start_gap = 30, end_gap = 20, node_max_gap = 80, node_min_gap = 50;
            var node_gap = (container_width - start_gap - end_gap - node_total_width) / max_serial_num;
            node_gap = Math.min(node_gap, node_max_gap);
            node_gap = Math.max(node_gap, node_min_gap);

            var vertical_gap = 80;

            //------------【3】画节点--------------------
            node_total_width = 0;
            for(i = 0; i <= max_serial_num; i++){
                paths = this.paths.filter(function (path) {
                    return path.serial_num === i;
                });
                max_node_width = 0;
                node_total_height = 0;
                paths.forEach(function (path) {
                    if(path.node_width > max_node_width)
                        max_node_width = path.node_width;

                    node_total_height += parseInt(path.node_el.css('height'));
                });
                var start_top = (container_height - (node_total_height + (paths.length - 1) * vertical_gap)) / 2;

                node_total_height = 0;
                var css_left = start_gap + i * node_gap + node_total_width;
                paths.forEach(function (path, index) {
                    var css_top = start_top + index * vertical_gap + node_total_height;
                    path.node_el.css({top: css_top + 'px', left: css_left + 'px'});
                    node_total_height += parseInt(path.node_el.css('height'))
                });

                node_total_width += max_node_width;

            }






            console.log(this.paths)


        }
    });

    core.view_registry.add('approval_diagram', DiagramView);




});