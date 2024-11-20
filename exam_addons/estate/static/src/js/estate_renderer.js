odoo.define('estate.Renderer', function (require) {
    'use strict';

    var AbstractRenderer = require('web.AbstractRenderer');
    var core = require('web.core');
    var qweb = core.qweb;

    var EstateRenderer = AbstractRenderer.extend({
        events: _.extend({}, AbstractRenderer.prototype.events, {
            'click .o_primary_button': '_onClickButton',
        }),

        _render: function () {
            this.$el.empty();
            this.$el.append(qweb.render('ViewEstate', { 'data_list': this.state }));
            return this._super.apply(this, arguments);
        },

        _onClickButton: function (ev) {
            ev.preventDefault();
            var target = $(ev.currentTarget);
            var estate_id = target.data('id');
            this.trigger_up('view_estate', {
                'id': estate_id,
            });
        }
    });

    return EstateRenderer;

});