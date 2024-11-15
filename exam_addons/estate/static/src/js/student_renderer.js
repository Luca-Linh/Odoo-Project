odoo.define('Renderer', function (require) {
    'use strict';

    var AbstractRenderer = require('web.AbstractRenderer');
    var core = require('web.core');
    var qweb = core.qweb;

    var StudentRenderer = AbstractRenderer.extend({
        events: _.extend({}, AbstractRenderer.prototype.events, {
            'click .o_primary_button': '_onClickButton',
        }),

        _render: function () {
            this.$el.empty();
            this.$el.append(qweb.render('ViewStudent', { 'data_list': this.state }));
            return this._super.apply(this, arguments);
        },

        _onClickButton: function (ev) {
            ev.preventDefault();
            var target = $(ev.currentTarget);
            var student_id = target.data('id');
            this.trigger_up('view_student', {
                'id': student_id,
            });
        }
    });

    return StudentRenderer;

});