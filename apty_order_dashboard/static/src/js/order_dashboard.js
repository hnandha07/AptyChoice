odoo.define('order_dashboard.Dashboard', function (require) {
"use strict";

var AbstractAction = require('web.AbstractAction');
var ajax = require('web.ajax');
var core = require('web.core');
var rpc = require('web.rpc');
var session = require('web.session');
var web_client = require('web.web_client');
var _t = core._t;
var QWeb = core.qweb;

var OrderProcessDashboard = AbstractAction.extend({
    template: 'OrderProcessDashboardMain',

    events: {
        "click .order-row": '_display_details',
        "click .state-btn": '_change_state',
        "click .process-order": '_process_order',
        "click .order-cancel": '_order_cancel',
        "click .confirm-cancel": '_confirm_cancel',
    },

    start: function () {
        var self = this;
        var args = arguments;
        var sup = this._super;
        var apty_list = this.$el.find('.list-order');
        console.log($(apty_list));
        rpc.query({
                    model: 'sale.order',
                    method: 'search_read',
                    args: [[['state', '=', 'sale']], ['name', 'id', 'partner_id', 'apty_order_state']],
                }).then(function (data) {
                    if (data.length) {
                        $(apty_list).find('tr').remove();
                        _.each(data, function(order) {
                            var tr_string = "<tr class='order-row' data-order-id="+ order['id'] +"><td>"+order['name']+"</td><td>"+order['partner_id'][1]+"</td></tr>";
                            $(apty_list).append(tr_string);
                        });
                    } else {
                        resolve(null);
                    }
                });
    return this;
    },

    _display_details: function(ev) {
        var order_id = $(ev.currentTarget).data('order-id');
        var order_screen = $('.order-details');
        rpc.query({
            model: 'sale.order',
            method: 'get_order_details',
            args: [[[parseInt(order_id)]]],
        }).then(function (data) {
            console.log(">>>>>>>> data : ", data)
            if (data){
                $(order_screen).html(QWeb.render('OrderDetail', {
                    order: data[0],
                    partner: data[0]['partner_id'][0],
                }));
            }
        });
    },

    _change_state: function(ev) {
        var apty_list = $(ev.currentTarget).parents().find('.list-order');
        $(ev.currentTarget).parents().find('.list-order').empty();
        $('.state-row').find('.active').removeClass('active');
        $('.details').empty();
        $(ev.currentTarget).addClass('active');
        var state = $(ev.currentTarget).data('state')
        var domain = false;
        console.log(">>>>>>>>>> state: ", state)
        if (state === 'all'){
            domain = [['state', '=', 'sale']];
        }
        else {
            domain = [['state', '=', 'sale'],['apty_order_state', '=', state]];
        }
        rpc.query({
            model: 'sale.order',
            method: 'search_read',
            args: [domain, ['name', 'id', 'partner_id', 'apty_order_state']],
        }).then(function (data) {
            if (data.length) {
                $(apty_list).find('tr').remove();
                _.each(data, function(order) {
                    var tr_string = "<tr class='order-row' data-order-id="+ order['id'] +"><td>"+order['name']+"</td><td>"+order['partner_id'][1]+"</td></tr>";
                    $(apty_list).append(tr_string);
                });
            }
        });
    },

    _process_order: function(ev) {
        var order_id = $(ev.currentTarget).parents().find('.details').data('order-id');
        var state = $(ev.currentTarget).data('new-state');
        var order_row = $('.order-row[data-order-id='+ order_id +']');
        rpc.query({
            model: 'sale.order',
            method: 'write',
            args: [parseInt(order_id), {'apty_order_state': state}],
        }).then(function (data) {
            console.log("data :  : : : ", data)
            $(order_row).trigger('click');
        });
    },

    _order_cancel: function (ev) {
        $('#cancel-confirmation').modal('toggle');
    }, 

    _confirm_cancel: function (ev) {
        var order_id = $(ev.currentTarget).data('order-id');
        var confirm_modal = $('#cancel-confirmation');
        var order_row = $('.order-row[data-order-id='+ order_id +']');
        rpc.query({
          model: 'sale.order',
          method: 'write',
          args: [parseInt(order_id), {'reason': $('input[name="reason"]').val(), 'apty_order_state': 'cancel'}],
        }).then(function (data){
            $(confirm_modal).modal('toggle');
            $(order_row).trigger('click');
        });
    },
});
core.action_registry.add('order_process_dashboard', OrderProcessDashboard);

return OrderProcessDashboard;

});