odoo.define('View', function (require) {
    'use strict';

    var AbstractView = require('web.AbstractView');
    var view_registry = require('web.view_registry');

    var StudentController = require('Controller');
    var StudentModel = require('Model');
    var StudentRenderer = require('Renderer');

    var StudentView = AbstractView.extend({
        display_name: 'Student',
        icon: 'fa-id-card-o',
        config: _.extend({}, AbstractView.prototype.config, {
            Model: StudentModel,
            Controller: StudentController,
            Renderer: StudentRenderer,
        }),
        viewType: 'student',
        searchMenuTypes: ['filter', 'favorite'],
        accesskey: "a",
        init: function (viewInfo, params) {
            this._super.apply(this, arguments);
        },
    });

    view_registry.add('student', StudentView);

    return StudentView;

});