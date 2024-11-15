odoo.define('color_integer_widget', function(require) {
    "use strict";

    var AbstractField = require('web.AbstractField');
    var fieldRegistry = require('web.field_registry');
    var core = require('web.core');

    var qweb = core.qweb;

    var colorField = AbstractField.extend({
        className: 'o_int_color',
        tagName: 'span',
        supportedFieldTypes: ['integer'],

        events: {
            'click .o_color_pill': 'clickColorPill',
        },

        init: function() {
            this.totalColors = 10;
            this.totalRecords = 0;
            this._super.apply(this, arguments);
        },

        willStart: function () {
            var self = this;
            this.colorGroupData = {};
            var colorDataPromise = this._rpc({
                model: this.model,
                method: 'read_group',
                domain: [],
                fields: ['color'],
                groupBy: ['color'],
            }).then(function (result) {
                _.each(result, function (r) {
                    self.colorGroupData[r.color] = r.color_count;
                });
            });
            return Promise.all([this._super.apply(this, arguments), colorDataPromise]);
        },

        _renderEdit: function() {
            this.$el.empty();
            var pills = qweb.render('FieldColorPills', { widget: this });
            this.$el.append(pills);
            this.$el.find('[data-toggle="tooltip"]').tooltip();
            this._updateColorCount();
        },

        _renderReadonly: function() {
            var className = 'o_color_pill active readonly o_color_' + this.value;
            this.$el.append($('<span>', {
                'class': className,
            }));
            this._updateColorCount();
        },

        clickColorPill: function(ev) {
            var $target = $(ev.currentTarget);
            var data = $target.data();
            this._setValue(data.val.toString());
            this._updateColorCount();
        },

        _updateColorCount: function() {
            // Tìm màu đã được chọn và hiển thị số lượng record
            var colorCount = this.colorGroupData[this.value] || 0;
            this.$el.find('.color-count').text('This colorCount is ' + colorCount);
        }
    });

    fieldRegistry.add('int_color', colorField);

    return {
        colorField: colorField,
    };
});
