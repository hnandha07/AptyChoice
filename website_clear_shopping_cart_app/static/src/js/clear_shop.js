 odoo.define('website_clear_shopping_cart.clear_shop', function (require) {
'use strict';
	$(document).ready(function(){
		$('.shopcartbtn').click(function() {
		var order_id = $(this).attr('value');
		var dataitem = {order_id: order_id};
		$.ajax({
				type: 'GET',
				url: '/shop/cartempty',
				dataType: 'json',
				data : dataitem,
				success: function() {
					window.location.href="/shop/cart";
				},
			});
		});
		$('body').on('click', '.popbutton', function(){
		var order_id = $(this).attr('value');
		var dataitem = {order_id: order_id};
		$.ajax({
				type: 'GET',
				url: '/shop/cartempty',
				dataType: 'json',
				data : dataitem,
				success: function(){
					window.location.href="/shop/cart";
				},
			});
		});
	});
});
