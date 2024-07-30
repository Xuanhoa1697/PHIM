var sc 
var checkout_status = 0
var datvetruoc_status = 0

function fn_dongia(number){
    return number.toLocaleString('vi-VN')
}

function select_loaive(jsonData, loaighe_id) {
    var listItems = ' <select id="opt_banggia" name="loaive" class="select-loaive"> ';
    for (var i = 0; i < jsonData.length; i++) {
        if (jsonData[i].dm_loaighe_id == loaighe_id) {
            selected_default = jsonData[i].dm_loaive_id == 1 ? 'selected': ''
            listItems += `<option value='${i}' ${selected_default} > ${jsonData[i].dm_loaive_name}  </option>`;    
        }
        
    }
    listItems += "</select>" ;
   
    return listItems
}




odoo.define("tht_cinema_website.web_seat_booking", function (require) {
    var rpc = require('web.rpc');
    var ajax = require("web.ajax");
    var pos_booking_fn = require('tht_cinema_website.ws_socket_fn')
    var client_name = ''
    var order_total = ''
    var change_amount = ''
    var payment_info = ''

    function broadcast_lichchieu(){
        var vals = {
            'style_map': $('#style_map').text(),
            'lichchieu_info': $('#lichchieu_info').html(),
            'cart_data':$('#donbanhang').html(),
            'seat_map':$('#seat-map').html(),
            'client_name':Math.random(),
            'order_total':order_total,
            'change_amount':change_amount,
            'payment_info':payment_info,
        }
        var res = rpc.query({
            model: 'dm.lichchieu',
            method: 'broadcast_data',
            args: [vals],
            /* args: args */
        }).then(function (products) {});
    }; // end broadcast_lichchieu
            
            
    function check_seat_exists(dm_lichchieu_id, vitrighe){
        var domain = [('id', '=', 2)];
        var vals = {
            'dm_lichchieu_id': dm_lichchieu_id,
            'vitrighe': vitrighe,
        }
        var res = rpc.query({
            model: 'dm.donbanve.line',
            method: 'check_seat_exists',
            args: [vals],
            /* args: args */
        })
        return res 
        };


    function tinhtienthua() {
        if ($('#khachdua').val()!=''){
            let total_dongia_f = parseFloat($('#total_dongia').html().replaceAll('.',''))
            let khachdua_f = parseFloat($('#khachdua').val().replaceAll('.',''))
            let result = khachdua_f - total_dongia_f

            return $('#tienthua').val(result.toLocaleString('vi-VN'))
        }       
    }


    
    $(document).ready(function () {
        $(window).on('beforeunload', function () {
            if (checkout_status == 0 && datvetruoc_status == 0 ) {
            ajax.jsonRpc('/cinema/map/out/', 'call', {flag: "out", seat_id: '', pos_source: 'pos_id', lichchieu_id: dm_lichchieu_id})
                // return "Warning, the record has been modified, your changes will be discarded.\n\nAre you sure you want to leave this page ?"            
            }
        })

        $('#donbanhang').change(function() {
            broadcast_lichchieu();
          });
  
        $('.form-tien-thua').on('input', function(){
            $('.money').autoNumeric('init',{
                aSep: '.',
                aDec: ',',
                vMax: '999999999',
                vMin: '0'
            });
            $('#khachdua').bind('blur focusout keypress keyup', function () {
                var demoGet = $('.money').autoNumeric('get');
                tienthua = parseFloat(demoGet) - parseFloat($('#total_dongia').html().replaceAll('.',''));
                $('#tienthua').val(tienthua.toLocaleString('vi-VN'))
            });
            
        })


        var firstSeatLabel = 1;
        if ($("#lichchieu_id").val()) {
            $.post(
                "/lichchieu/get_json_data",
                {
                    event_id: $("#lichchieu_id").val(),
                },
                function (bigData) {
                    bigData = JSON.parse(bigData);
                    
                    var map_list = bigData["data"];
                    
                    if (bigData["max_col_count"] <= 10) {
                        $("#seat-map").addClass("sh-20");
                    } else if (bigData["max_col_count"] <= 20 && bigData["max_col_count"] > 10) {
                        $("#seat-map").addClass("sh-20");
                    } else if (bigData["max_col_count"] <= 30 && bigData["max_col_count"] > 20) {
                        $("#seat-map").addClass("sh-30");
                    } else {
                        $("#seat-map").addClass("sh-50");
                    }

                    if (map_list.length > 0) {
                        
                        var $cart = $("#donbanhang_line"),
                            $counter = $("#counter"),
                            $total_dongia = $("#total_dongia")
                            
                            sc = $("#seat-map").seatCharts({
                                map: map_list,
                                seats: bigData["seats"],
                                naming: {
                                    top: false,
                                    left: true,
                                    columns: bigData["columns_map"],
                                    // columns: ["1", "2", "3", "4", "", "" , "5", "6", "7", "8", "9", "10"],
                                    rows: bigData["rows_map"],
                                    // rows: ['A','B','C',' ' ,' ' , 'D', 'E', 'F', 'G', 'H', 'I', "J", "K", "L", 'M', 'N', 'O', 'P'],
                                    // rows:['A','B','C', 'D', 'E', 'F', 'G', 'H', 'I', "J", "K", "L", 'M', 'N', 'O', 'P'],
                                    getLabel : function (character, row, column) {
                                        if (column == '' || row == ''){
                                            return ''
                                        }
                                        return row+column;
                                    }
                                },
                                legend: {
                                    node: $("#legend"),
                                    items: bigData["legend_items"],
                                },
                                click: function () {
                                    let seat_map_para = {'flag': "add" , 'seat_id': this.settings.id, 'pos_source': pos_id, 'lichchieu_id': dm_lichchieu_id}
                                    pos_booking_fn.push_seat_map_status(seat_map_para)
                                                            
                                    if (this.status() == "available") {
                                        

                                        var self = this
                                        var seat_exist = check_seat_exists(dm_lichchieu_id,this.settings.id);
                                        seat_exist.then(function(result){
                                            if (result == true){
                                                $('#cart-item-'+self.settings.id).remove()
                                                $total_dongia.text(reSumTotal('.dongia') )
                                                $('#'+self.settings.id).addClass('unavailable').removeClass('selected').off()
                                                $counter.text($('ul#donbanhang_line li').length)
                                            }
                                            broadcast_lichchieu();                                            
                                        })
                                        
                                        var selected_seat =  this.settings.label ;
                                        var seatCateg = this.data().category  ;

                                        $(`<li class='table-row '> <div class='col col-1'> ${selected_seat} </div> 
                                            <div class='col col-2 loaive' > ${select_loaive(bigData['banggia'], seatCateg )} </div> 
                                            
                                            <div class='col col-3 dongia' >  </div> 
                                            <div class='col col-4' >  <span> <a href="#" class="cancel-cart-item"><b class="fa fa-fw o_button_icon fa-close">X</b></a> </span>  </div>
                                            </li>  `)
                                            .attr("id", "cart-item-" + this.settings.id)
                                            .data("seatId", this.settings.id)
                                            .data("seatCateg", this.data().category)
                                            .appendTo($cart)
                                            .change(function () {
                                                banggia_id = $(this).find('select').val()
                                                $(this).find('.dongia').html(fn_dongia(bigData['banggia'][banggia_id].dongia))
                                                $total_dongia.text(reSumTotal('.dongia') )
                                                tinhtienthua()
                                            })
                                            
                                        getDongia('.loaive', bigData['banggia'])                                      
                                        
                                        // $counter.text(sc.find("selected").length + 1);
                                        $counter.text($('ul#donbanhang_line li').length)
                                        $total_dongia.text(reSumTotal('.dongia') )
                                        tinhtienthua()
                                        $("#checkout-button").removeAttr("disabled");
                                        $(".datvetruoc-button").removeAttr("disabled");
                                        return "selected";
                                    } else if (this.status() == "selected") {
                                        let seat_map_para = {'flag': "remove" , 'seat_id': this.settings.id, 'pos_source': pos_id, 'lichchieu_id': dm_lichchieu_id}
                                        pos_booking_fn.push_seat_map_status(seat_map_para)
                                        //update the counter
                                        // $counter.text(sc.find("selected").length - 1);
                                        $counter.text($('ul#donbanhang_line li').length)
                                        //and total
                                        //remove the item from our cart
                                        $("#cart-item-" + this.settings.id).remove();
                                        $total_dongia.text(reSumTotal('.dongia') )
                                        tinhtienthua()
                                        

                                        if ($counter.text($('ul#donbanhang_line li').length) <= 1) {

                                            $(".checkout-button").attr("disabled", "disabled");
                                        }

                                        //seat has been vacated
                                        return "available";
                                    } else if (this.status() == "unavailable") {
                                        //seat has been already booked
                                        return "unavailable";
                                    } else {
                                        return this.style();
                                    }
                                        
                                },
                            });
                        sc.get(bigData["booked_seat"]).status("unavailable");
                        sc.get(bigData["datvetruoc_list"]).status("datvetruoc");
                        $("#donbanhang_line").on("click", ".cancel-cart-item", function () {
                            sc.get($(this).parents("li:first").data("seatId")).click();
                            
                        });

                    }

                    

                    $(document).on("click", "#checkout-button", function (ev) {
                        var unavailble_seat_tickettype = {};
                        checkout_status = 1 // seat update status
                        $("#donbanhang_line")
                            .find("li")
                            .each(function (index) {
                                
                                if ($(this).data("seatCateg") in unavailble_seat_tickettype) {
                                    var seat_list = unavailble_seat_tickettype[$(this).data("seatCateg")];
                                    seat_list.push([$(this).data("seatId"), $(this).find('.dongia').text().replaceAll('.',''), event_banggia_id, $(this).find(' option:selected').text() ]);
                                    unavailble_seat_tickettype[$(this).data("seatCateg")] = seat_list;
                                } 
                                else {
                                    unavailble_seat_tickettype[$(this).data("seatCateg")] = [[$(this).data("seatId"), $(this).find('.dongia').text().replaceAll('.',''), event_banggia_id , $(this).find('option:selected').text() ]]
                                }
                            });
                        
                        let makhachhang = $('#makhachhang').val()
                        let sodienthoai = $('#sodienthoai').val()
                        let payment_method = $("[name=payment_method]:checked").val();
                        let dm_session_line_id = $('#dm_session_line_id').val()
                        let datvetruoc = $('#datvetruoc').val()
                        ev.preventDefault();
                        ev.stopPropagation();
                        var $form = $(ev.currentTarget).closest("form");
                        var $button = $(ev.currentTarget).closest('[type="submit"]');
                        $button.attr("disabled", true);

                        let post_vals = { unavailble_seat_tickettype: unavailble_seat_tickettype, 
                            makhachhang: makhachhang, 
                            sodienthoai: sodienthoai, 
                            dm_session_line_id: dm_session_line_id, 
                            datvetruoc: datvetruoc,
                            payment_method: payment_method
                        }

                        // return ajax.jsonRpc($form.attr("action"), "call", post_vals)
                        return ajax.jsonRpc($form.attr("action"), "call", post_vals)
                        .then(function (modal) {
                            console.log('then funtion======')
                            var $modal = $(modal);
                            $modal.modal({ backdrop: "static", keyboard: false });
                            $modal.find(".modal-body > div").removeClass("container"); // retrocompatibility - REMOVE ME in master / saas-19
                            $modal.appendTo("body").modal();
                            $modal.on("click", ".js_goto_event", function () {
                                $modal.modal("hide");
                                $button.prop("disabled", false);
                            });
                            $modal.on("click", ".close", function () {
                                $button.prop("disabled", false);
                            });
                        });
                    });


                    $(document).on("click", ".datvetruoc-button", function (ev) {
                        var unavailble_seat_tickettype = {};
                        datvetruoc_status = 1
                        $("#donbanhang_line")
                            .find("li")
                            .each(function (index) {
                                if ($(this).data("seatCateg") in unavailble_seat_tickettype) {
                                    var seat_list = unavailble_seat_tickettype[$(this).data("seatCateg")];
                                    seat_list.push([$(this).data("seatId"), $(this).find('.dongia').text().replaceAll('.',''), event_banggia_id, $(this).find('.loaive option:selected').text() ]);
                                    // seat_list.push($(this).find('select').val());
                                    unavailble_seat_tickettype[$(this).data("seatCateg")] = seat_list;
                                } 
                                else {
                                    unavailble_seat_tickettype[$(this).data("seatCateg")] = [[$(this).data("seatId"), $(this).find('.dongia').text().replaceAll('.',''), event_banggia_id, $(this).find('.loaive option:selected').text()] ]
                                }
                                
                            });
                        
                        let makhachhang = $('#makhachhang').val()
                        let sodienthoai = $('#sodienthoai').val()
                        let dm_session_line_id = $('#dm_session_line_id').val()
                        let datvetruoc = $('#datvetruoc').val()

                        if (makhachhang =='' && sodienthoai =='') {
                            alert('Nhập thông tin khách hàng')
                            return false
                        }
                        
                        ev.preventDefault();
                        ev.stopPropagation();
                        var $form = $(ev.currentTarget).closest("form");
                        var $button = $(ev.currentTarget).closest('[type="submit"]');
                        $button.attr("disabled", true);

                        let post_vals = { unavailble_seat_tickettype: unavailble_seat_tickettype, 
                            makhachhang: makhachhang, 
                            sodienthoai: sodienthoai, 
                            dm_session_line_id: dm_session_line_id, 
                            datvetruoc: datvetruoc }

                        return ajax.jsonRpc($form.attr("action"), "call", post_vals)
                        .then(function (modal) {
                            var $modal = $(modal);
                            $modal.modal({ backdrop: "static", keyboard: false });
                            $modal.find(".modal-body > div").removeClass("container"); // retrocompatibility - REMOVE ME in master / saas-19
                            $modal.appendTo("body").modal();
                            $modal.on("click", ".js_goto_event", function () {
                                $modal.modal("hide");
                                $button.prop("disabled", false);
                            });
                            $modal.on("click", ".close", function () {
                                $button.prop("disabled", false);
                            });
                        });
                    }); // fn datvetruoc-button


                //remove click on seat-map
                $('#seat-map').off();
                }
            ).done(function(){
                ajax.jsonRpc('/cinema/map/first_load/', 'call', {flag: "first_load", seat_id: '', pos_source: pos_id, lichchieu_id: dm_lichchieu_id})
                .then((result)=>{
                        let db_lc = result.db_lc
                        lichchieu_id = result.lichchieu_id
                        seat_arr = db_lc[lichchieu_id]
                        flag = result.flag
                        flag == 'first_load' && seat_arr && lichchieu_id == dm_lichchieu_id ? sc.get(seat_arr).status('unavailable') : ''
                    
                })
                
            })
            
        } // end if lichchieu_id
    });

   

    function getDongia(class_dongia, data_banggia) {
        self = this
        let dongia_id = 0;
        $(class_dongia).each(function (index) {
            dongia_id = $(this).find('select').val()
            $('#donbanhang_line').find('.dongia').eq(index).html(fn_dongia(data_banggia[dongia_id].dongia))
        });
        return dongia_id
        
    }

    function reSumTotal(class_price) {
        var total_price = 0;
        //basically find every selected seat and sum its price
        $(class_price).each(function (index) {
            if ( $(this).text() != '') {
                total_price += parseFloat($(this).text().replaceAll('.',''));
            }
            
        });
        return total_price.toLocaleString('vi-VN')
        
    }

    

    
});


   
