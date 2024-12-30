odoo.define('bap_project.button_task', function (require) {
    "use strict";

    const ListController = require('web.ListController');
    const ListView = require('web.ListView');
    const viewRegistry = require('web.view_registry');
    const rpc = require('web.rpc');

    const AlertListController = ListController.extend({
        buttons_template: 'bap_project.bap_project_task_buttons',

        willStart: function () {
            const self = this;
            return this._super(...arguments).then(function () {
                const context = self.model.loadParams.context || {};
                self.showButton = context.stat_button_view;
            });
        },

        renderButtons: function ($node) {
            this._super($node);
            if (this.showButton) {
                this.$buttons.find('.o_button_alert_notification').removeClass('d-none');
            }
        },

        events: _.extend({}, ListController.prototype.events, {
            'click .o_button_alert_notification': '_onNotify',
        }),

        _onNotify: function () {
            const self = this;

            // Lấy context từ loadParams
            const context = self.model.loadParams.context || {};
            const projectId = context.default_project_id;

            if (projectId) {
                rpc.query({
                    model: 'bap.project.task',
                    method: 'action_update_newest_sprint',
                    args: [projectId],
                }).then(function (result) {
                    if (result.error) {
                        // Hiển thị thông báo lỗi nếu không có sprint mở hoặc không có task để cập nhật
                        self.do_warn('Error', result.error);
                    } else if (result.success) {
                        // Hiển thị thông báo thành công nếu task được cập nhật
                        self.do_notify('Tasks Updated', result.success);
                    }
                }).catch(function (error) {
                    console.error('Error:', error);
                    self.do_warn('Error', 'An error occurred while updating tasks');
                });
            } else {
                self.do_warn('Error', 'Project ID not found in context');
            }
        },
    });

    const WidgetListView = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Controller: AlertListController,
        }),
    });

    viewRegistry.add('project_task_tree_class', WidgetListView);
});
