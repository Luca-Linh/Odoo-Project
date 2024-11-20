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

            // Hiện nút Apply nếu ít nhất một checkbox được chọn
            if (isColorChecked || isDateChecked) {
                $('#apply_button').removeClass('d-none');
            } else {
                $('#apply_button').addClass('d-none');
            }
        },
        // Apply
        _onApply: function () {
            var isColorChecked = $('#hide_color').is(':checked');
            var isDateChecked = $('#hide_date').is(':checked');

            if (isColorChecked) {
                this._toggleFieldVisibility('color', false); // hide column `color`
                $('#hide_color').prop('disabled', true);
            }
            if (isDateChecked) {
                this._toggleFieldVisibility('date', false); // hide column `date`
                 $('#hide_date').prop('disabled', true);
            }

            if ((isColorChecked && !isDateChecked) || (!isColorChecked && isDateChecked)) {
                // Show Apply and Clear
                $('#apply_button').removeClass('d-none');
                $('#clear_button').removeClass('d-none');
            } else {
                // Show Clear
                $('#apply_button').addClass('d-none');
                $('#clear_button').removeClass('d-none');
            }
        },
        // Clear
        _onClear: function () {
            this._toggleFieldVisibility('color', true);
            this._toggleFieldVisibility('date', true);

            $('#hide_color').prop('checked', false).prop('disabled', false);
            $('#hide_date').prop('checked', false).prop('disabled', false);

            // Reset
            $('#apply_button').addClass('d-none');
            $('#clear_button').addClass('d-none');
        },

        _toggleFieldVisibility: function (fieldName, isVisible) {
            var $fields = this.$el.find(`td[data-name="${fieldName}"], span[name="${fieldName}"]`);
            if (isVisible) {
                $fields.show(); // Show
            } else {
                $fields.hide(); // Hide
            }
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
