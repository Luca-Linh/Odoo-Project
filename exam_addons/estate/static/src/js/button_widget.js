odoo.define('estate.button_widget', function (require) {
    "use strict";

     var ListController = require('web.ListController');
     var ListView = require('web.ListView');
     var viewRegistry = require('web.view_registry');

     var AlertListController = ListController.extend({
        buttons_template: 'estate.demo_widget_buttons',
        events: _.extend({}, ListController.prototype.events, {
            'click .o_button_alert_notification': '_onNotify',
            'change #hide_color': '_onCheckboxChange',
            'change #hide_date': '_onCheckboxChange',
            'click #apply_button': '_onApply',
            'click #clear_button': '_onClear',

        }),
        _onNotify: function () {
             this.do_notify("'Inventory Overview' added to dashboard",
             'Please refresh your browser for the change to take effect.');
        },
        _onCheckboxChange: function () {
            var isColorChecked = $('#hide_color').is(':checked');
            var isDateChecked = $('#hide_date').is(':checked');

            // Show Apply button if any checkbox is selected
            this._toggleButtonVisibility(false);
        },
        _onInitState: function () {
            var self = this;

            // Fetch saved flags from the server
            this._rpc({
                model: 'demo.widget',
                method: 'get_hide_flags',
            }).then(function (flags) {
                var [hideColor, hideDate] = flags;

                // Update checkbox states
                $('#hide_color').prop('checked', hideColor).prop('disabled', hideColor);
                $('#hide_date').prop('checked', hideDate).prop('disabled', hideDate);

                // Update Apply/Clear button visibility
                self._toggleButtonVisibility(hideColor || hideDate);
            });
        },

        _toggleButtonVisibility: function (hasSelection) {
            if (hasSelection) {
                $('#apply_button').addClass('d-none');
                $('#clear_button').removeClass('d-none');
            } else {
                $('#apply_button').removeClass('d-none');
                $('#clear_button').addClass('d-none');
            }
        },

        // Apply
        _onApply: function () {
            var self = this;
            var isColorChecked = $('#hide_color').is(':checked');
            var isDateChecked = $('#hide_date').is(':checked');
            console.log("Hide Color:", isColorChecked, "Hide Date:", isDateChecked);
            this._rpc({
                model: 'demo.widget',
                method: 'update_hide_flags',
                args: [[isColorChecked, isDateChecked]],
            }).then(function () {
                self.do_notify("Fields Updated", "The visibility of fields has been updated.");
                if (isColorChecked) {
                     $('#hide_color').prop('disabled', true);
                }
                if (isDateChecked) {
                     $('#hide_date').prop('disabled', true);
                }

                self._toggleButtonVisibility(true);
                self.reload(); // Reload the view to apply changes
            });
        },
        // Clear
        _onClear: function () {
            var self = this;
            // Reset tất cả các cờ về False
            this._rpc({
                model: 'demo.widget',
                method: 'update_hide_flags',
                args: [[false, false]], // Truyền danh sách [False, False]
            }).then(function () {
                // Hiển thị thông báo và reload view
                self.do_notify("Fields Reset", "The visibility of fields has been reset.");

                 $('#hide_color').prop('disabled', false).prop('checked', false);
                 $('#hide_date').prop('disabled', false).prop('checked', false);

                self._toggleButtonVisibility(false);
                self.reload(); // Reload lại tree view để áp dụng thay đổi
            });
        },
        _start: function () {
            this._super.apply(this, arguments);
            this._onInitState(); // Gọi hàm khởi tạo trạng thái
        },
    });
     var WidgetListView = ListView.extend({
         config: _.extend({}, ListView.prototype.config, {
             Controller: AlertListController,
         }),
     });

    // Bind the custom ListView class to the `demo_widget_tree_class`
    viewRegistry.add('demo_widget_tree_class', WidgetListView);
});
