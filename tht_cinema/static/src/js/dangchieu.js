odoo.define('tht_cinema.dangchieu', function (require) {
    'use strict';
    var timeout_id = null;
    // var ajax = require('web.ajax');
        
    $( document ).ready(function() {
        //Main ajax that runs to check the continous updation of the screen
        function longpolling() {
            
            $.ajax({
                type: 'GET',
                url: '/cinema/dangchieu/',
                dataType: 'html',
                // beforeSend: function(xhr){xhr.setRequestHeader('Content-Type', 'application/json');},
                data: {"limit": limit,"page": page, "page_next_load": page_next_load},
                success: function(data) {
                    $('#content').html(data)
                    timeout_id = setTimeout(longpolling, load_delay);
                    page_next_load = page + 1 ;
                    page = page + 1
                },
                error: function (jqXHR, status, err) {
                    if(timeout_id)
                        clearTimeout(timeout_id);
                        timeout_id = setTimeout(longpolling, load_delay * 4);
                },

                timeout: load_delay,
            });
        }
            
        longpolling();
        
        

    }); // end doc

}); // end define
    
