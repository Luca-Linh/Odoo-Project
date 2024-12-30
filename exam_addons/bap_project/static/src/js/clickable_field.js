odoo.define('bap_project.clickable_field', function (require) {
    'use strict';

   var ListView = require('web.ListView');
    var core = require('web.core');
    var _t = core._t;

    ListView.include({
        events: {
            'click .o_report_task_sprint_field': 'onClickField',  // Lắng nghe sự kiện click vào field
        },

        onClickField: function (event) {
            var fieldName = $(event.currentTarget).attr('name');  // Lấy tên field đang được nhấp
            var recordId = $(event.currentTarget).data('record-id');  // Lấy ID của record

            if (fieldName && recordId) {
                this._rpc({
                    model: 'report.task.sprint',
                    method: 'show_tasks_based_on_field',
                    args: [fieldName, recordId],
                }).then(function (result) {
                    if (result.action) {
                        // Mở view popup (action sẽ trả về)
                        self.do_action(result.action);
                    }
                });
            }
        },
    });
});