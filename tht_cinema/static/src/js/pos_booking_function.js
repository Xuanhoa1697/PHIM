// sync map
// const socket = io("ws://"+sv_socket_io, {secure: true});
const socket = io.connect('https://'+sv_socket_io);

const clickSeat = (data) => {
    socket.emit('clickSeat', data)
}

const clickCheckout = (data) => {
    socket.emit('userCheckout', data)
}

const getMapInfo = (data) => {
    socket.emit('getMapInfo', data)
}

socket.emit('userLcInfo', {user_id, lc_id})

socket.on('mapInfo', (data) => {
    sc.get(data.seat_ids).status('unavailable noClick')
})

socket.on('syncSeatMap', (data) => {
    data.flag == 'add' && data.lc_id == lichchieu_id ? sc.get([data.seat_id]).status('unavailable noClick') : ''
    data.flag == 'remove' && data.lc_id == lichchieu_id ? sc.get([data.seat_id]).status('available') : ''
})

socket.on('removeUserSelectSeat', (data) => {
    console.log('removeUserSelectSeat:', 'user disconnect')
    console.log(data)
    sc.get(data.seat_ids).status('available')
})


odoo.define("tht_cinema.pos_booking_function", function (require) {
    var ajax = require("web.ajax");

    push_seat_map_status = async function(para) {
        // let para = {'flag': "add" , 'seat_id': this.settings.id, 'pos_source': pos_id, 'lichchieu_id': dm_lichchieu_id}
        // return ajax.jsonRpc('/cinema/seat_map/','call', para)
        console.log('push_seat_map_status fn')
        console.log('lichchieu_id', lichchieu_id);
        // io.emit('client_push-lc-id', lichchieu_id)
        
        
        para.user_id = user_id
        para.lichchieu_id = lichchieu_id

        socket.emit('click_select_seat', para) 

                

    }

    let ws_socket_fn = {
        'map_first_load': '',
        'check_seat_map_status': '',
        'push_seat_map_status': push_seat_map_status,
    }

    return ws_socket_fn


    
});


   


// odoo.define("tht_cinema.pos_booking_function", function (require) {
//     var ajax = require("web.ajax");

//     map_first_load = async function(para) {
//         // let seat_map_para = {'flag': "add" , 'seat_id': this.settings.id, 'pos_source': pos_id, 'lichchieu_id': dm_lichchieu_id}
//         return ajax.jsonRpc('/cinema/map/first_load/', 'call', para)
        
//     }

//     check_seat_map_status = async function(para) {
//         // let seat_map_para = {'flag': "add" , 'seat_id': this.settings.id, 'pos_source': pos_id, 'lichchieu_id': dm_lichchieu_id}
//         let result = ajax.jsonRpc('/cinema/check_seat_map_status/', 'call', para)
//         return result 
       
//     }

//     push_seat_map_status = async function(para) {
//         // let para = {'flag': "add" , 'seat_id': this.settings.id, 'pos_source': pos_id, 'lichchieu_id': dm_lichchieu_id}
//         return ajax.jsonRpc('/cinema/seat_map/','call', para)
       
//     }

//     var pos_booking_fn = {
//         'map_first_load': map_first_load,
//         'check_seat_map_status': check_seat_map_status,
//         'push_seat_map_status': push_seat_map_status,
//     }

//     return pos_booking_fn


    
// });


   
