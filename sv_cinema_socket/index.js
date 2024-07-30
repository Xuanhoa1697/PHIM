var fs = require('fs')
const app = require('express')()
// var https = require('https')
const httpServer = require("https").createServer({
    // home.tien.info
    // key: fs.readFileSync('./private.key'),
    // cert: fs.readFileSync('./certificate.crt')
    // key: fs.readFileSync('/home/ubuntu/ssl/test2.tien.info/privkey1.pem'),
    // cert: fs.readFileSync('/home/ubuntu/ssl/test2.tien.info/fullchain1.pem')
    // key: fs.readFileSync('/home/ubuntu/ssl/test3.tien.info/privkey1.pem'),
    // cert: fs.readFileSync('/home/ubuntu/ssl/test3.tien.info/fullchain1.pem')
    // key: fs.readFileSync('/home/ubuntu/dev-thegold/ajin05.ddns.net/privkey1.pem'),
    // cert: fs.readFileSync('/home/ubuntu/dev-thegold/ajin05.ddns.net/fullchain1.pem')
    key: fs.readFileSync('/etc/letsencrypt/live/thegoldcinema.com/privkey.pem'),
    cert: fs.readFileSync('/etc/letsencrypt/live/thegoldcinema.com/fullchain.pem')
    
  }, app);
const io = require("socket.io")(httpServer, {
    cors: {
        // origin: ['192.168.1.28'],
        origin: '*',
    }
});

var port = process.env.PORT || 3003

app.get('/', function (req, res) {
    res.send('hello world')
  })

let lc_id = 0

const socket_obj = {}
const checkout_obj = {}
const socketSeats_obj = {}
const socketLc_obj = {}
const lcSeats_obj = {}

io.on("connection", (socket) => {
    console.log('socket.adapter.rooms:', socket.adapter.rooms)
    let date = new Date();
    date.setSeconds(date.getSeconds() + 25200)
    console.log('=============*** connection ***================ ',socket.id, date  )
        
    socket.on('userLcInfo', (data) => {
        console.log('socket.on userInfo', data)
        socketLc_obj[socket.id] = data.lc_id
        socketSeats_obj[socket.id] = []
        lcSeats_obj.hasOwnProperty(data.lc_id) ? '' : lcSeats_obj[data.lc_id] = []
        socket.join(data.lc_id)
        console.log('57 io.sockets.adapter.rooms', io.sockets.adapter.rooms);
        
    })

    socket.on('getMapInfo', (data) => {
        console.log('getMapInfo:', data)
        socket.emit("mapInfo", {'seat_ids': lcSeats_obj[data.lc_id]});
    })

    socket.on('clickSeat', (data) => {
        console.log('----- clickSeat socket.id:', socket.id)
        console.log('clickSeat data', data)
        data.flag == 'add' && socketSeats_obj[socket.id] ? socketSeats_obj[socket.id].push(data.seat_id) : ''
        data.flag == 'remove' && socketSeats_obj[socket.id] ? lcSeats_obj[data.lc_id] = socketSeats_obj[socket.id].filter(item => item !== data.seat_id) : ''
        
        data.flag == 'add' && lcSeats_obj[data.lc_id] ? lcSeats_obj[data.lc_id].push(data.seat_id) : ''
        data.flag == 'remove' && lcSeats_obj[data.lc_id] ? lcSeats_obj[data.lc_id] = lcSeats_obj[data.lc_id].filter(item => item !== data.seat_id) : ''
        
        console.log('data.lc_id:', data.lc_id)

        socket.to(data.lc_id).emit('syncSeatMap', data)
        // socket.emit('syncSeatMap', data)
        if (data.hasOwnProperty('socket_id')) {
            io.to(data.socket_id).emit('syncSeatMapOnApp', data)
        }
        
    })

    socket.on('userCheckout', data => {
        console.log('===== userCheckout =====', data)
        checkout_obj[socket.id] = data.lc_id
    })

    socket.on('getVedattruoc', data => {
        console.log('getVedattruoc-data:', data)
        socket.to(data.lc_id).emit('deleteVedattruoc', {'seat_ids': data.seatIds})

    })
    
    socket.on('disconnect', (data) => {
        let date = new Date();
        date.setSeconds(date.getSeconds() + 25200)
        console.log('---------------------------------- disconnect:-------------------- ', date)
        console.log('---------------------------------- disconnect socket.id', socket.id)
        
        lc_id = socketLc_obj[socket.id]
        checkout_obj.hasOwnProperty(socket.id) ? '' : socket.to(lc_id).emit('removeUserSelectSeat', {'seat_ids': socketSeats_obj[socket.id]}) 
        socketSeats_obj[socket.id] ? lcSeats_obj[lc_id] = lcSeats_obj[lc_id].filter(item => !socketSeats_obj[socket.id].includes(item)) : ""
        // delete socketSeats_obj[socket.id]
    });
    // end disconnect
})

httpServer.listen(port, '0.0.0.0', function() {
    console.log("i am listening at port 3003");
})
