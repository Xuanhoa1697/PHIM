odoo.define('tht_cinema.datvetruoc', function (require) {
    'use strict';
    
    var ajax = require('web.ajax');
        
    $( document ).ready(function() {
        $("a.dvt_line_delete").click(function() {
            let para = {
                'id': $(this).data("id")
            }
            ajax.jsonRpc("/cinema/rpc/datvetruoc_line/delete/", 'call', para).then(function (data) {
                location.reload();
            });
        });

        $("a.dvt_delete").click(function() {
            let para = {
                'id': $(this).data("id")
            }
            ajax.jsonRpc("/cinema/rpc/datvetruoc/delete/", 'call', para).then(function (data) {
                location.reload();
            });
        });

        $("button.dvt_delete_draft").click(function() {
            let para = {
                'id': $(this).data("id")
            }
            ajax.jsonRpc("/cinema/rpc/datvetruoc/delete_draft/", 'call', para).then(function (data) {
                location.reload();
            });
        });


      }); // end document
    
})