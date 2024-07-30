$('doccument').ready(function(){
    console.log('ready')
    
    // $("#order_name").keypress(function(event) {
    //     if (event.keyCode === 13) {
    //         console.log('enter')
    //         console.log($("#order_name").val())
    //         $("#order_name").val('')
    //     }
    //     });


})

odoo.define("tht_cinema_website.soatve", function (require) {
    var rpc = require('web.rpc');
    var ajax = require("web.ajax");

    $('doccument').ready(function(){
        $("#order_name").focus();

        $( "#form_soatve" ).submit(function( event ) {
            event.preventDefault();
            console.log('enter')
            console.log($("#order_name").val())
            
            let post_vals = {
                order_name: 'TGC-2021080000214'
            }
            $("#order_name").val('')

            console.log(post_vals)

            return ajax.jsonRpc('/cnm/soatve/result', "call", post_vals)
            .then(function (result) {
                console.log('then funtion======', result)
                // $('div#result').html('<h1>asdfas dasdf</h1>')
                $('div#result').html(result)
                // $('div.wrapper').html(modal)

            });

        });
    })
})

