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
users_obj = {}
io.on("connection", (socket) => {
    console.log('connection socket.id=======35 ', socket.id)

    socket.emit("get_status", map_info);
    

    socket.on('client_user_id', (data)=>{
        // data = [user_id, lc_id]
        console.log('user_id data', data);
        users_obj[socket.id] = data
        console.log('users_obj', users_obj);
        data.length > 1 ? socket.join(data[1]) : ''
        console.log('io.sockets.adapter.rooms', io.sockets.adapter.rooms);
    })

    // io.to(${socketId}).emit('hey', 'I just met you');
    

    // socket.on('click_select_seat', function(data) {
    //     socket.join(data);
    //     seat_map_obj[data] = {}
    //     console.log('socket.adapter.rooms:', socket.adapter.rooms)

    //     console.log('lc_seat_selected_obj', lc_seat_selected_obj);
    //     socket.to(data).emit('sync_seat', lc_seat_selected_obj[data])
    //   });

    socket.on('click_select_seat', data => {
        // console.log('data======== click_select_seat 42', data);
        seat_map_obj[data.lichchieu_id] = data
        
        if (lc_seat_selected_obj[data.lichchieu_id] === undefined ){
            lc_seat_selected_obj[data.lichchieu_id] = []
        }
        let lcSeats = lc_seat_selected_obj[data.lichchieu_id]
        lcSeats.includes(data.seat_id) ? lcSeats.pop(data.seat_id) : lcSeats.push(data.seat_id)        

        if (user_seat_selected_obj[data.user_id] === undefined ){
            user_seat_selected_obj[data.user_id] = []
        }
        let uSeats = user_seat_selected_obj[data.user_id]
        uSeats.includes(data.seat_id) ? uSeats.pop(data.seat_id) : uSeats.push(data.seat_id)
        
         
        // console.log('seat_map_obj', seat_map_obj);
        // console.log('lc_seat_selected_obj', lc_seat_selected_obj);
        // console.log('user_seat_selected_obj', user_seat_selected_obj);

        // console.log('data.lichchieu_id', data.lichchieu_id);
        socket.to(data.lichchieu_id).emit('sync_seat', seat_map_obj)

    })
    socket.on('new-user-joined', name => {
        // console.log("New User", name);
        users[socket.id] = name;
        socket.broadcast.emit('user-joined', name);
        
    });

    // socket.to('room-name').emit('event-name', data)
    // socket.on('push_lichieu_id', message => {
    //     console.log('push_lc_id===== ', message)
    // });

    socket.on('send', message => {
        socket.broadcast.emit('receive', { message: message, name: users[socket.id] })
    });
    socket.on('disconnect', message => {
        if (users_obj[socket.id]) {
            let user_id = users_obj[socket.id][0]
            let lc_id = users_obj[socket.id][1]
            let remove_info = []
            // console.log('disconnect=======user_id ', socket.id, user_id)
            // console.log('socket.id, lc_id', socket.id, lc_id);

            // console.log('user_seat_selected_obj', user_seat_selected_obj[user_id]);
            if (user_seat_selected_obj[user_id]) {
                console.log('true', true);
                // remove_info.push(user_seat_selected_obj[user_id])
                remove_info = [[...user_seat_selected_obj[user_id]]]
                console.log('lc_seat_selected_obj', lc_seat_selected_obj)
                user_seat_selected_obj[user_id].map(seat_item => lc_seat_selected_obj[lc_id].pop(seat_item))
                console.log('lc_seat_selected_obj', lc_seat_selected_obj)

                user_seat_selected_obj[user_id] = []
                remove_info.push(lc_id)
                
                socket.to(lc_id).emit('remove_seat', remove_info)

                // ds ghe trong lich chieu
                if (lc_seat_selected_obj[lc_id]) {
                    let seat_ids_remove = user_seat_selected_obj[user_id]
                    console.log('seat_ids_remove', seat_ids_remove);
                    console.log('lc_seat_selected_obj[lc_id]', lc_seat_selected_obj[lc_id]);

                    lc_seat_selected_obj[lc_id] = lc_seat_selected_obj[lc_id].filter(item => !seat_ids_remove.includes(item))
                    console.log('lc_seat_selected_obj[lc_id]', lc_seat_selected_obj[lc_id]);

                }                
                
            } else {
                console.log('false', false);
            }

            
            console.log('remove_info', remove_info)
            console.log('user_seat_selected_obj[user_id]', user_seat_selected_obj[user_id])

        }
        
        
        
        // delete user_seat_selected_obj
        
        // delete users_obj[socket.id];
    });
})

httpServer.listen(port, function() {
    console.log("i am listening at port 3000");
})