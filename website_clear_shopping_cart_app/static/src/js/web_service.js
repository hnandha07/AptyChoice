odoo.define('npa_base.npa_base', function(require) {
    "use strict";    
    
    var DateWidget = require('web.datepicker');
    
    DateWidget.DateWidget.include({
        _onDateTimePickerShow: function () {
            if (this.$input.val().length !== 0 && this.isValid()) {
                this.$input.select();
            }
            var value = moment();
            this.setValue(value);
            return this._super.apply(this, arguments);
        },
    });

    DateWidget.DateTimeWidget.include({
        type_of_date: "datetime",
        init: function (parent, options) {
            this._super(parent, _.extend({
                buttons: {
                    showToday: true,
                    showClear: true,
                    showClose: true,
                },
            }, options || {}));
        },
    });

});