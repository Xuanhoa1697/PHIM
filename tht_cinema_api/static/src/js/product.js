
odoo.define("tht_cinema_website.product_test", function (require) {
    var rpc = require('web.rpc');
    var ajax = require("web.ajax");
    var pos_booking_fn = ''
    var client_name = ''
    var order_total = ''
    var change_amount = ''
    var payment_info = ''


    
    $(document).ready(function () {

        $('#product').click(function(){
            console.log('click product')
            return ajax.jsonRpc('/product', "call", {}).then(
                (data)=> {
                    console.log(data)
                    $('main').append(data)
                }
            )
        })
      
    });

   

    
});


   
