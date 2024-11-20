odoo.define('estate.View', function (require) {
    'use strict';

    var AbstractView = require('web.AbstractView');
    var view_registry = require('web.view_registry');

    var EstateController = require('estate.Controller');
    var EstateModel = require('estate.Model');
    var EstateRenderer = require('estate.Renderer');

    var EstateView = AbstractView.extend({
        display_name: 'Estate',
        icon: 'fa-id-card-o',
        config: _.extend({}, AbstractView.prototype.config, {
            Model: EstateModel,
            Controller: EstateController,
            Renderer: EstateRenderer,
        }),
        viewType: 'estate',
        searchMenuTypes: ['filter', 'favorite'],
        accesskey: "a",
        init: function (viewInfo, params) {
            this._super.apply(this, arguments);
        },
    });

    view_registry.add('estate', EstateView);

    return EstateView;

});