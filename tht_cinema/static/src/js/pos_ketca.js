
odoo.define("tht_cinema.pos_ketca", function (require) {
    console.log('ketca:',)
    
    let ajax =  require('web.ajax')

    $(document).ready(function(){
        console.log(pos_id);
        console.log(pos_line_id);
        
        $('a#ketca').on('click', function(event){
            event.preventDefault();
            $.confirm({
                title: 'Xác nhận kết thúc ca làm việc !',
                content: 'Bạn có muốn kết thúc ca làm việc ?',
                buttons: {
                    
                    'Huỷ bỏ': function(){
                        
                    },
                    confirm: {
                        text: 'Đồng ý',
                        btnClass: 'btn-blue',
                        keys: [
                            'enter',
                        ],
                        action: function () {
                            let url_report = `/cinema/dm_session_line_report/${pos_id}/${pos_line_id}`
                            console.log(url_report);
                            
                            location.href = url_report
                            // this.$content // reference to the content

                            // vals = {
                            //     'id': 1,
                            //     'b': 2
                            // }
                            // ajax.jsonRpc('/web/dataset/call', 'call', {
                            //     model: 'dm.session',
                            //     method: 'test',
                            //     args: [[dm_session_id]],
                            // })
                            
                        }
                    }
                }
            });
        });
    

        // $('a#ketca').click(function(event){
        //     event.preventDefault();
        //     console.log('heee');

                            
        //     var confirm_ketca = confirm("Bạn có muốn kết thúc ca làm việc !");
        //     if (confirm_ketca == false) {
        //         return false
        //     } else {
        //         vals = {
        //             'a': 1,
        //             'b': 2
        //         }
        //         rpc.query({
        //             model: 'dm.session',
        //             method: 'test',
        //             args: [vals]
        //         })
        //     }

        //     // vals = {
        //     //     'a': 1,
        //     //     'b': 2
        //     // }
        //     // rpc.query({
        //     //     model: 'dm.session',
        //     //     method: 'test',
        //     //     args: [vals]
        //     // })
        
        // }) // end a click


    })
    
    
    
    
});


   
