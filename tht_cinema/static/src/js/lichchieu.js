

odoo.define("tht_cinema.lichchieu", function (require) {

    var ajax = require("web.ajax");
    $(document).ready(function () {
        $('#chonphim').click(function(){
            let url_lichchieu , para_lichchieu = '' ;
            console.log('click:', 'CL')
            url_lichchieu = '/lichchieu/sudung'
            $.get(url_lichchieu, para_lichchieu, function(data){
                $('#seat-map').remove()    
                $('#lichchieu').html(data).show()
            })
            
        })
    })
 

})