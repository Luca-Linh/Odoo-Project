odoo.define('bap_project.popup_task_widget', function (require) {
    "use strict";

    var ListView = require('web.ListView');
    var Dialog = require('web.Dialog');
    var core = require('web.core');
    var FieldFloat = require('web.basic_fields').FieldFloat;

    var PopupTaskWidget = FieldFloat.extend({
        events: _.extend({}, FieldFloat.prototype.events, {
            'click': '_onClickField',
        }),

        _onClickField: function () {
            var fieldName = this.field.name;
            console.log("Field clicked:", fieldName);
            var domain = this._getDomain(fieldName);
            console.log("Domain generated:", domain);
            this._showPopup(domain);
        },

        _getDomain: function (fieldName) {
            var projectId = this.recordData.project_id.data.id;
            console.log("Record data:", this.recordData);
            console.log("Project ID:", projectId);
            var taskType = "";

            switch (fieldName) {
                case 'total_task_count':
                    taskType = "";
                    break;
                case 'task_new_count':
                    taskType = "new";
                    break;
                case 'task_dev_count':
                    taskType = "dev";
                    break;
                case 'task_qc_count':
                    taskType = "qc";
                    break;
                case 'task_done_count':
                    taskType = "done";
                    break;
            }

            return [['project_id', '=', projectId], ['status', '=', taskType]];
        },

        _showPopup: function (domain) {
            console.log("Preparing to show popup with domain:", domain);
            var self = this;

            // Sử dụng Dialog Odoo để hiển thị popup thay vì do_action
            var dialog = new Dialog(this, {
                title: 'Task Popup',
                size: 'medium',
                $content: $('<div>').text('Domain: ' + JSON.stringify(domain)),  // Hiển thị domain hoặc thông tin khác ở đây
            });
            dialog.open();

            console.log("Popup opened successfully.");
        }

    });

    core.form_widget_registry.add('popup_task_widget', PopupTaskWidget);
});
