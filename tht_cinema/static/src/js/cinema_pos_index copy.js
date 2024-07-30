odoo.define('tht_cinema.cinema_pos_index', function (require) {
    "use strict";

    console.log('cinema_pos_index fn:', )
    var client_name = ['hix', 'hix', 'hix']
    var order_total = '10k'
    var change_amount = 'change_amount'
    var payment_info = 'adfasd'


    
        // var pos_model = require('point_of_sale.models');
        // var Model = require('web.rpc');
        var rpc = require('web.rpc');
        // var screens = require('point_of_sale.screens');
        // var chrome = require('point_of_sale.chrome');
        // var PosBaseWidget = require('point_of_sale.BaseWidget');
        var core = require('web.core');
    
        var _t = core._t;

        $(document).ready(function() {
            var rpc = require('web.rpc');
        
            $('#query').click(getProductBySKU);
            function getProductBySKU(){
                // console.log("Hello world!");
                var domain = [('id', '=', 2)];
                // var args = [domain];
                var vals = {
                    'cart_data':$('.order-container').html(),
                    'client_name':Math.random(),
                    'order_total':order_total,
                    'change_amount':change_amount,
                    'payment_info':payment_info,
                }
        
                var res = rpc.query({
                    model: 'dm.lichchieu',
                    method: 'broadcast_data',
                    args: [vals],
                    /* args: args */
                }).then(function (products) {});
                };
            });
        

        // var abc = rpc.query({
        //     model: 'dm.lichchieu',
        //     method: 'broadcast_data',
        //     args: [vals],
        // })
        // .then(function(result) {});

        // console.log(abc)

        
            
    
        // screens.PaymentScreenWidget.include({
        //     render_paymentlines: function(){
        //         this._super();
        //         console.log('this:', this)
        //         var customer_display = this.pos.config.customer_display;
        //         if(customer_display){
        //             this.pos.get_order().mirror_image_data();
        //         }
        //     },
        // });
    
        // screens.ReceiptScreenWidget.include({
        //     renderElement: function() {
        //         var self = this;
        //         this._super();
        //         var customer_display = this.pos.config.customer_display;
        //         this.$('.next').click(function(){
        //             if(self.pos.get_order()){
        //                 if(customer_display){
        //                     self.pos.get_order().mirror_image_data();
        //                 }
        //             }
        //         });
        //     },
        // });
    
        // chrome.OrderSelectorWidget.include({
        //     start: function(){
        //         this._super();
        //         var customer_display = this.pos.config.customer_display;
        //         if(this.pos.get_order()){
        //             if(customer_display){
        //                 console.log('this:', this)
        //                 this.pos.get_order().mirror_image_data();
        //             }
        //         }
        //     },
        //     renderElement: function(){
        //         var self = this;
        //         this._super();
        //         console.log('this 54:', this )
        //         var customer_display = this.pos.config.customer_display;
        //         console.log('customer_display:', customer_display)
        //         this.$('.order-button.select-order').click(function(event){
        //             console.log('self.pos.get_order().mirror_image_data():', self.pos.get_order().mirror_image_data())
        //             if(self.pos.get_order() && customer_display){
        //                 self.pos.get_order().mirror_image_data();
        //             }
        //         });
        //         this.$('.neworder-button').click(function(event){
        //             if(self.pos.get_order() && customer_display){
        //                 self.pos.get_order().mirror_image_data();
        //             }
        //         });
        //         this.$('.deleteorder-button').click(function(event){
        //             if(self.pos.get_order() && customer_display){
        //                 self.pos.get_order().mirror_image_data();
        //             }
        //         });
        //     },
        //     deleteorder_click_handler: function(event, $el) {
        //         var self  = this;
        //         var order = this.pos.get_order();
        //         var customer_display = this.pos.config.customer_display;
        //         var session_id = order.pos_session_id;
        //         if (!order) {
        //             return;
        //         } else if ( !order.is_empty() ){
        //             this.gui.show_popup('confirm',{
        //                 'title': _t('Destroy Current Order ?'),
        //                 'body': _t('You will lose any data associated with the current order ,Cancelling this sale will notify Head Office'),
        //                 confirm: function(){
        //                     self.pos.delete_current_order();
        //                     if(customer_display){
        //                         self.pos.get_order().mirror_image_data();
        //                     }
        //                 },
        //             });
        //         } else {
        //             this.pos.delete_current_order();
        //             if(customer_display){
        //                 self.pos.get_order().mirror_image_data();
        //             }
        //         }
        //     },
        // });
    
        // var _modelproto = pos_model.Order.prototype;
        // pos_model.Order = pos_model.Order.extend({
        //     add_product:function(product, options){
        //         var self = this;
        //         _modelproto.add_product.call(this,product, options);
        //         var customer_display = this.pos.config.customer_display;
        //         if(customer_display){
        //             console.log('this 108:', this)
        //             self.mirror_image_data();
        //         }
        //     },
        //     mirror_image_data:function(){
        //         console.log('this 113:', this)
        //         var self = this;
        //         var client_name = false;
        //         var order_total = self.get_total_with_tax();
        //         var change_amount = self.get_change();
        //         var payment_info = [];
        //         var paymentlines = self.paymentlines.models;
        //         if(paymentlines && paymentlines[0]){
        //             paymentlines.map(function(paymentline){
        //                 payment_info.push({
        //                     'name':paymentline.name,
        //                     'amount':paymentline.amount,
        //                 });
        //             });
        //         }
        //         if(self.get_client()){
        //             client_name = self.get_client().name;
        //         }
        //         var vals = {
        //             'cart_data':$('.order-container').html(),
        //             'client_name':client_name,
        //             'order_total':order_total,
        //             'change_amount':change_amount,
        //             'payment_info':payment_info,
        //         }
        //         rpc.query({
        //             model: 'customer.display',
        //             method: 'broadcast_data',
        //             args: [vals],
        //         })
        //         .then(function(result) {});
        //     },
        //     set_client: function(client){
        //         console.log('this 142:', this)
        //         _modelproto.set_client.apply(this, arguments);
        //         this.mirror_image_data();
        //     }
        // });
    
        // screens.NumpadWidget.include({
        //     start: function() {
        //         var self = this;
        //         this._super();
        //         var customer_display = this.pos.config.customer_display;
        //         this.$(".input-button").click(function(){
        //             if(customer_display){
        //                 self.pos.get_order().mirror_image_data();
        //             }
        //         });
        //     },
        // });
        // var CustomerDisplay = screens.ActionButtonWidget.extend({
        //     template : 'CustomerDisplay',
        //     button_click : function() {
        //         self = this;
        //         window.open(self.pos.attributes.origin+'/web/customer_display' , '_blank');
        //     },
        // });
        // screens.define_action_button({
        //     'name' : 'CustomerDisplay',
        //     'widget' : CustomerDisplay,
        //     condition: function(){
        //         return this.pos.config.customer_display;
        //     },
        // });
    });
    