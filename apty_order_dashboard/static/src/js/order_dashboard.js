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

Number.prototype.padLeft = function(base,chr){
    var  len = (String(base || 10).length - String(this).length)+1;
    return len > 0? new Array(len).join(chr || '0')+this : this;
 }
     

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
        "click .confirm-assign": '_confirm_assign',
        "click .confirm-cod-received": '_confirm_cod_received',
    },

    start: function () {
        var self = this;
        var args = arguments;
        var sup = this._super;
        var apty_list = this.$el.find('.list-order');
        var apty_order_table = this.$el.find('#order-list-table');
        // var src = "/apty_order_dashboard/static/src/sounds/notification.mp3";
        // $('body').append('<audio id="notification" src="'+src+'" autoplay="true"></audio>');
        var dt_order = $(apty_order_table).DataTable({
            destroy: true,
            pageLength : 5,
            searching: false,
            ordering:  false,
            bLengthChange: false,
            createdRow: function( row, data, dataIndex ) {
                $(row).attr('data-order-id', data[4]);
                $(row).attr('data-model', data[5]);
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
                        order['payment_mode'],
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
        var apty_list = this.$el.find('.list-order');
        var apty_order_table = this.$el.find('#order-list-table');
        $('.state-row').find('.active').removeClass('active');
        $('.details').empty();
        $(ev.currentTarget).addClass('active');
        var state = $(ev.currentTarget).data('state');
        $(apty_order_table).DataTable().clear();
        var dt_order = $(apty_order_table).DataTable({
            destroy: true,
            pageLength : 5,
            searching: false,
            ordering:  false,
            bLengthChange: false,
            createdRow: function( row, data, dataIndex ) {
                $(row).attr('data-order-id', data[4]);
                $(row).attr('data-model', data[5]);
                $(row).addClass("order-row");
            }
        });
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
                    dt_order.row.add([
                        order['name'],
                        order['partner_id'][1],
                        model_string,
                        order['payment_mode'],
                        order['id'],
                        order['model']
                    ]).draw( false );
                });
            }
        });
    },

    _process_order: function(ev) {
        var order_id = $(ev.currentTarget).parents().find('.details').data('order-id');
        var active_model = $(ev.currentTarget).parents().find('.details').data('model');
        var state = $(ev.currentTarget).data('new-state');
        var payment_method = $(ev.currentTarget).parents().find('.details').data('payment-type');
        var delivery_popup = $('#assign-delivery-partner');
        var delivery_list = $(delivery_popup).find('#delivery_person');
        var cod_confirmation_popup = $('#cod-confirmation');
        var new_state = $('.state-btn[data-state='+ state +']');
        var old_state = $(ev.currentTarget).data('old-state');
        var update_date = old_state + '_date';
        var update_by = old_state + '_by';
        var d = new Date();
        var dformat = [ d.getFullYear(), (d.getMonth()+1).padLeft(), d.getDate().padLeft()].join('-')+
            ' ' +
          [ d.getUTCHours().padLeft(), d.getUTCMinutes().padLeft(), d.getUTCSeconds().padLeft()].join(':');
        if (active_model === 'sale.order' && state === 'delivered' &&  payment_method === 'cash_on_delivery'){
            $(cod_confirmation_popup).modal('toggle');
        }
        else{
            if (state === 'picked'){
                ajax.rpc("/get_delivery_partners", {
                }).then(function ( partners ) {
                    $(delivery_list).empty()
                    _.each(partners['partners'], function (partner) {
                        $(delivery_list).append('<option value='+ partner['id'] +'>'+ partner['name'] +'</option>')
                    });
                    $(delivery_popup).modal('toggle');
                    $(new_state).trigger('click');
                });
            }
            else{
                var args_c = {
                    'apty_order_state': state,
                }
                args_c[update_by] = session.uid;
                args_c[update_date] =  dformat,
                rpc.query({
                    model: active_model,
                    method: 'write',
                    args: [parseInt(order_id), args_c],
                }).then(function (data) {
                    $(new_state).trigger('click');
                });
            }
        }
    },

    _order_cancel: function (ev) {
        $('#cancel-confirmation').modal('toggle');
    },

    _print_order: function (ev) {
        $('#print-confirmation').modal('toggle');
        $('.pos-receipt-container')
    },

    _js_custom_print: function (ev) {
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

    _confirm_assign: function (ev) {
        var order_id = $(ev.currentTarget).data('order-id');
        var confirm_modal = $('#assign-delivery-partner');
        var order_row = $('.order-row[data-order-id='+ order_id +']');
        var partner_selected = $( "#delivery_person option:selected" ).val();
        var active_model = $(ev.currentTarget).data('model');
        var d = new Date();
        var dformat = [ d.getFullYear(), (d.getMonth()+1).padLeft(), d.getDate().padLeft()].join('-')+
            ' ' +
          [ d.getUTCHours().padLeft(), d.getUTCMinutes().padLeft(), d.getUTCSeconds().padLeft()].join(':');
        rpc.query({
            model: active_model,
            method: 'write',
            args: [parseInt(order_id), {
                'picked_by': parseInt(partner_selected),
                'apty_order_state': 'picked',
                'picked_date': dformat,
            }]
        }).then( function (data) {
            $(confirm_modal).modal('toggle');
            $(order_row).trigger('click');
        });
    },

    _confirm_cod_received: function(ev) {
        var order_id = $(ev.currentTarget).data('order-id');
        var confirm_modal = $('#cod-confirmation');
        var order_row = $('.order-row[data-order-id='+ order_id +']');
        var active_model = $(ev.currentTarget).data('model');
        var new_state = $('.state-btn[data-state=delivered]');
        ajax.rpc("/order/process/cod", {
                'order_id': order_id,
                'model': active_model
            }).then(function (data) {
                $(confirm_modal).modal('toggle');
                $(new_state).trigger('click');
            });
    }
});
core.action_registry.add('order_process_dashboard', OrderProcessDashboard);


return OrderProcessDashboard;

});
