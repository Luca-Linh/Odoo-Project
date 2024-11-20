odoo.define('MonthYearWidget', function (require) {
    "use strict";

    const basicFields = require('web.basic_fields');
    const registry = require('web.field_registry');
    const fieldUtils = require('web.field_utils');

    const MonthYearWidget = basicFields.FieldDate.extend({
        // Ghi đè hàm _renderReadonly để chỉ hiển thị MM/YYYY khi ở chế độ readonly
        _renderReadonly: function () {
            if (this.value) {
                const date = moment(this.value);
                // Định dạng lại thành MM/YYYY khi ở chế độ readonly
                this.$el.text(date.format('MM/YYYY'));
            } else {
                this.$el.text('');
            }
        },
    });

    // Đăng ký widget mới
    registry.add('month_year', MonthYearWidget);
    return MonthYearWidget;
});
