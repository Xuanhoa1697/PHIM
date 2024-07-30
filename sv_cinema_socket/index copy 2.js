var fs = require('fs')
const app = require('express')()
// var https = require('https')
const httpServer = require("https").createServer({
    // home.tien.info
    // key: fs.readFileSync('./private.key'),
    // cert: fs.readFileSync('./certificate.crt')
    key: fs.readFileSync('/home/ubuntu/ssl/test.tien.info/privkey.pem'),
    cert: fs.readFileSync('/home/ubuntu/ssl/test.tien.info/fullchain.pem')
    
  }, app);
const io = require("socket.io")(httpServer, {
    cors: {
        //origin: ['192.168.1.28'],
        origin: '*',
    }
});

var port = process.env.PORT || 3000

app.get('/', function (req, res) {
    res.send('hello world')
  })

const users = {};
const uSeat_obj = {}
const lc_list = [];
const seat_map_obj = {}
const lc_seat_selected_obj = {}
const user_seat_selected_obj = {}
const map_info = {seat_map_obj, lc_seat_selected_obj, user_seat_selected_obj}
let lc_id = 0
const users_obj = {}
const lc_obj = {}
const book_obj = {}
const socket_obj = {}
const checkout_obj = {}

io.on("connection", (socket) => {
    let date = new Date();
    date.setSeconds(date.getSeconds() + 25200)
    console.log('======= connection ================ ', date  )
    console.log('================ ')
    console.log('users_obj:', users_obj)
    console.log('lc_obj:', lc_obj)
    console.log('socket_obj:', socket_obj)
    
    socket.on('userLcInfo', (data) => {
        console.log('socket.on userInfo', data)
        socket_obj[socket.id] = [data.user_id, data.lc_id ]
        console.log('socket_obj:', socket_obj)

        // users_obj[data.user_id] = []
        users_obj[socket.id] = new Array()
        console.log('---------------------', typeof(users_obj[socket.id]) )
        console.log('users_obj:', users_obj)
        lc_obj.hasOwnProperty(data.lc_id) ? '' : lc_obj[data.lc_id] = []
        console.log('lc_obj:', lc_obj)

        socket.join(data.lc_id)
        console.log('46 io.sockets.adapter.rooms', io.sockets.adapter.rooms);
        console.log('users_obj:', users_obj)
        console.log('lc_obj:', lc_obj)
        console.log('socket_obj:', socket_obj)
        console.log('end =======  socket.on userInfo', data)
    })

    socket.on('getMapInfo', (data) => {
        console.log('getMapInfo:', data)
        socket.emit("mapInfo", {'users_obj': users_obj, 'lc_obj': lc_obj});
    })

    socket.on('clickSeat', (data) => {
        console.log('click Seat data:', data)
        // data.flag == 'add' ? users_obj[data.user_id].push(data.seat_id) : ''
        // data.flag == 'remove' ? users_obj[data.user_id].pop(data.seat_id) : ''
        data.flag == 'add' ? users_obj[socket.id].push(data.seat_id) : ''
        data.flag == 'remove' ? users_obj[socket.id].pop(data.seat_id) : ''
        console.log('users_obj:', users_obj)
        
        data.flag == 'add' ? lc_obj[data.lc_id].push(data.seat_id) : ''
        data.flag == 'remove' ? lc_obj[data.lc_id].pop(data.seat_id) : ''
        console.log('lc_obj:', lc_obj)

        socket.to(data.lc_id).emit('syncSeatMap', data)
    })

    socket.on('userCheckout', data => {
        console.log('userCheckout =====', data)
        checkout_obj[data.user_id] = data.lc_id
        console.log('checkout_obj:', checkout_obj)
    })
    

    // socket.on('client_user_id', (data)=>{
    //     // data = [user_id, lc_id]
    //     console.log('user_id data', data);
    //     // users_obj[socket.id] = data
    //     // console.log('users_obj', users_obj);
    //     data.length > 1 ? socket.join(data[1]) : ''
    //     console.log('io.sockets.adapter.rooms', io.sockets.adapter.rooms);
    // })
 

    socket.on('disconnect', (data) => {
        let date = new Date();
        date.setSeconds(date.getSeconds() + 25200)
        console.log('----------------------------------disconnect:-------------------- ', date)
        console.log('users_obj:', users_obj)
        console.log('lc_obj:', lc_obj)
        console.log('disconnect data:', data)
        console.log('====================== disconnect socket.id', socket.id)
        console.log('====================== disconnect socket_obj', socket_obj[socket.id])
        console.log('users_obj[socket.id]:', users_obj[socket.id], typeof(users_obj[socket.id]))
        let lc_id = socket_obj[socket.id][1]
        users_obj[socket.id] ? users_obj[socket.id].map(item => lc_obj[lc_id].pop(item)) : console.log('false')
        users_obj[socket.id] = []
        // users_obj[socket.id].length > 0 ? users_obj[socket.id].map(item => lc_obj[lc_id].pop(item)) : ''
        
        // if (socket_obj[socket.id]) {
        //     console.log('socket_obj:', socket_obj)
        //     let seat_ids = users_obj[socket_obj[socket.id][0]]
        //     let lc_id = socket_obj[socket.id][1]

        //     if (checkout_obj.hasOwnProperty(socket_obj[socket.id][0])) {
        //         console.log('checkout_obj:', checkout_obj)
        //     } else {
        //     socket.to(socket_obj[socket.id][1]).emit('removeUserSelectSeat', {'seat_ids': seat_ids})
            
        //     console.log('lc_id:', lc_id)
        //     }

        //     console.log('seat_ids:', seat_ids)
            
        //     seat_ids.map(item => lc_obj[lc_id].pop(item))
        //     seat_ids = []
        //     delete socket_obj[socket.id]
        // }
        
        
    });
})

httpServer.listen(port, function() {
    console.log("i am listening at port 3000");
})