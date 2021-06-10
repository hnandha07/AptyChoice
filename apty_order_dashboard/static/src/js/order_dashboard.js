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
        "click .print-order": '_print_order',
        "click .js_custom_print": '_js_custom_print',

    },

    start: function () {
        var self = this;
        var args = arguments;
        var sup = this._super;
        var apty_list = this.$el.find('.list-order');
        var apty_order_table = this.$el.find('#order-list-table');
        // var src = "/apty_order_dashboard/static/src/sounds/notification.mp3";
        // $('body').append('<audio id="notification" src="'+src+'" autoplay="true"></audio>');
        console.log(">>>>>>>>>>>",  this.$el.find('#order-list-table'))
        var dt_order = $(apty_order_table).DataTable({
            destroy: true,
            pageLength : 5,
            searching: false,
            ordering:  false,
            bLengthChange: false,
            createdRow: function( row, data, dataIndex ) {
                $(row).attr('data-order-id', data[3]);
                $(row).attr('data-model', data[4]);
                $(row).addClass("order-row");
            }
        });
        ajax.rpc("/get_order_list", {
            "state": "order",
        }).then(function (data) {
            if(data['orders'].length){
                $(apty_list).find('tr').remove();
                _.each(data['orders'], function(order) {
                    var model_string = '';
                    if (order['model'] == 'pos.order'){
                        model_string = 'Point of Sale';
                    }
                    else{
                        model_string = 'Sales Portal'
                    }
                    dt_order.row.add([
                        order['name'],
                        order['partner_id'][1],
                        model_string,
                        order['id'],
                        order['model']
                    ]).draw( false );
                });
            }
        });
    return this;
    },

    _display_details: function(ev) {
        var order_id = $(ev.currentTarget).data('order-id');
        var order_screen = $('.order-details');
        var order_model = $(ev.currentTarget).data('model');
        rpc.query({
            model: order_model,
            method: 'get_order_details',
            args: [[[parseInt(order_id)]]],
        }).then(function (data) {
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
        if (state === 'order'){
            domain = [['apty_order_state', '=', state]];
        }
        else {
            domain = [['apty_order_state', '=', state]];
        }
        ajax.rpc("/get_order_list", {
            "state": state,
        }).then(function (data) {
            if(data['orders'].length){
                $(apty_list).find('tr').remove();
                _.each(data['orders'], function(order) {
                    var model_string = '';
                    if (order['model'] == 'pos.order'){
                        model_string = 'Point of Sale';
                    }
                    else{
                        model_string = 'Sales Portal'
                    }
                    var tr_string = "<tr class='order-row' data-order-id="+ order['id'] +" data-model="+ order['model'] +"><td>"+order['name']+"</td><td>"+order['partner_id'][1]+"</td><td>"+ model_string +"</td></tr>";
                    $(apty_list).append(tr_string);
                });
            }
        });
    },

    _process_order: function(ev) {
        var order_id = $(ev.currentTarget).parents().find('.details').data('order-id');
        var active_model = $(ev.currentTarget).parents().find('.details').data('model');
        var state = $(ev.currentTarget).data('new-state');
        var new_state = $('.state-btn[data-state='+ state +']');
        if (active_model === 'sale.order' && new_state === 'delivered'){
            console.log("COD")
        }
        
        rpc.query({
            model: active_model,
            method: 'write',
            args: [parseInt(order_id), {'apty_order_state': state}],
        }).then(function (data) {
            $(new_state).trigger('click');
        });
    },

    _order_cancel: function (ev) {
        $('#cancel-confirmation').modal('toggle');
    },

    _print_order: function (ev) {
        $('#print-confirmation').modal('toggle');
        $('.pos-receipt-container')
    },

    _js_custom_print: function (ev) {
        console.log('------window------', window)
        window.print();
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