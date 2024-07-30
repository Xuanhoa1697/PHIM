odoo.define('tht_cinema.trave', function (require) {
    'use strict';
    console.log('trave:',)
    
    var ajax = require('web.ajax');
        
    $( document ).ready(function() {
        $("a.dvt_line_delete").click(function() {
            let para = {
                'id': $(this).data("id")
            }
            ajax.jsonRpc("/cinema/rpc/trave_line/delete/", 'call', para).then(function (data) {
                location.reload();
            });
        });

        $("a.dvt_delete").click(function() {
            let para = {
                'id': $(this).data("id")
            }
            ajax.jsonRpc("/cinema/rpc/trave/delete/", 'call', para).then(function (data) {
                location.reload();
            });
        });

        $("button.dvt_delete_draft").click(function() {
            let para = {
                'id': $(this).data("id")
            }
            ajax.jsonRpc("/cinema/rpc/trave/delete_draft/", 'call', para).then(function (data) {
                location.reload();
            });
        });


      }); // end document
    
})