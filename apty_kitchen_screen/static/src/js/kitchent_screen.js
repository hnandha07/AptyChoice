odoo.define('apty_kitchen_screen.kitchen_screen', function (require) {
    'use strict';
    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var kitchenScreenWidget = AbstractAction.extend({
        hasControlPanel: true,
        init: function(parent, action) {
            this.actionManager = parent;
            this.report_model = action.context.model;
            if (this.report_model === undefined) {
                this.report_model = 'apty.kitchen.screen';
            }
            this.odoo_context = action.context;
           return this._super.apply(this, arguments);
        },
        start: function () {
            var self = this;
            self._refresh_screen(self.report_model, self.odoo_context);
        },
        _refresh_screen: function (model_id=false, context={}) {
            var extra_info = this._rpc({
                model: model_id,
                method: 'prepare_kitchen_screen',
                args: [context.id],
                context: context,
            }).then(function (result) {
                var content_div = $('.o_content')
                content_div.empty();
                content_div.html(result)
            });
        }
    });
    core.action_registry.add('kitchen_screen', kitchenScreenWidget);
    return kitchenScreenWidget;

})