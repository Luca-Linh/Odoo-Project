odoo.define('estate.button_alert', function (require) {
    "use strict";

     var ListController = require('web.ListController');
     var ListView = require('web.ListView');
     var viewRegistry = require('web.view_registry');

     var AlertListController = ListController.extend({
        buttons_template: 'estate.demo_widget_buttons',
        events: _.extend({}, ListController.prototype.events, {
            'click .o_button_alert_notification': '_onNotify',
        }),
        _onNotify: function () {
             this.do_notify("'Inventory Overview' added to dashboard",
             'Please refresh your browser for the change to take effect.');
        }
    });
    var WidgetListView = ListView.extend({
       config: _.extend({}, ListView.prototype.config, {
           Controller: AlertListController,
       }),
    });

    // Bind the custom ListView class to the `demo_widget_tree_class`
    viewRegistry.add('demo_widget_tree_class', WidgetListView);
});
