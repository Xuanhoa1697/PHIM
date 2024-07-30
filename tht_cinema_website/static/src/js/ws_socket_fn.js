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

socket.on('deleteVedattruoc', (data) => {
    console.log('deleteVedattruoc:', 'user deleteVedattruoc')
    console.log(data)
    sc.get(data.seat_ids).status('available')
})

