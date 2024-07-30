odoo.define("tht_cinema.pos_booking_function", function (require) {
    var ajax = require("web.ajax");

    map_first_load = async function(para) {
        // let seat_map_para = {'flag': "add" , 'seat_id': this.settings.id, 'pos_source': pos_id, 'lichchieu_id': dm_lichchieu_id}
        return ajax.jsonRpc('/cinema/map/first_load/', 'call', para)
        
    }

    check_seat_map_status = async function(para) {
        // let seat_map_para = {'flag': "add" , 'seat_id': this.settings.id, 'pos_source': pos_id, 'lichchieu_id': dm_lichchieu_id}
        let result = ajax.jsonRpc('/cinema/check_seat_map_status/', 'call', para)
        return result 
       
    }

    push_seat_map_status = async function(para) {
        // let para = {'flag': "add" , 'seat_id': this.settings.id, 'pos_source': pos_id, 'lichchieu_id': dm_lichchieu_id}
        return ajax.jsonRpc('/cinema/seat_map/','call', para)
       
    }

    var pos_booking_fn = {
        'map_first_load': map_first_load,
        'check_seat_map_status': check_seat_map_status,
        'push_seat_map_status': push_seat_map_status,
    }

    return pos_booking_fn


    
});


   
