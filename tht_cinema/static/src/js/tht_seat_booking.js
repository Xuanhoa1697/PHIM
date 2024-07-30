// var programming_languages = [{"1":"php", "2":"java", "3":"javascript", "4":"ruby", "5":"go", "6":"shell script", "7":"c#", "8":"python", "9":"perl"}];

function fn_dongia(number){
    return new Intl.NumberFormat('vi-VN', { maximumSignificantDigits: 3 }).format(number)

}

function produceOptions(programming_languages) {
    var populated_options = "";
    $.each(programming_languages, function (key, value){
        var object = value;
        $.each(object, function(k,v) {
            populated_options += "<option value='"+k+"'>"+v+"</option>";
        })
    });

    return populated_options;
   }

//    var jsonData = {
//     "Table": [{
//         "stateid": "2",
//         "statename": "Texas"
//     }, {
//         "stateid": "3",
//         "statename": "Louisiana"
//     }, {
//         "stateid": "4",
//         "statename": "California"
//     }, {
//         "stateid": "5",
//         "statename": "Nevada"
//     }, {
//         "stateid": "6",
//         "statename": "Massachusetts"
//     }]
// };

function select_loaive(jsonData) {
    console.log('jsonData', jsonData)
    var listItems = ' <select id="opt_banggia" name="loaive" class="select-loaive"> <option> </option>';

    for (var i = 0; i < jsonData.length; i++) {
        selected_default = i == 0 ? 'selected': ''
        listItems += `<option value='${jsonData[i].dm_loaive_id}' ${selected_default} > ${jsonData[i].dm_loaive_name} </option>`;
    }
    listItems += "</select>" ;
    
    return listItems

}


function dropdown_loaive(jsonData) {
    var listItems = `<div id="dd" class="wrapper-dropdown-3" tabindex="1"> <ul class="dropdown">` ;

    for (var i = 0; i < jsonData.length; i++) {
        listItems += `<li> <i class="icon-envelope icon-large"></i> <b> ${jsonData[i].dm_loaive_name} </b> </li>`
        //  `<option value=' ${jsonData[i].dm_loaive_id}'> <b> ${jsonData[i].dm_loaive_name} </b> </option> ${jsonData[i].dongia}`;
    }

    listItems += "</ul> </div>" ;
    
    return listItems

}
   

odoo.define("tht_cinema.website_event", function (require) {
    console.log('seat_booking.js sh')
    var compiled = _.template(`<li> <select name="loaive" id="loaive">
                            <option value="nguoilon">Người lớn </option>
                            <option value="treem">Trẻ em</option>
                            
            </select>
    hello: <%= name %></li>`);

    var ajax = require("web.ajax");
    $(document).ready(function () {
        var firstSeatLabel = 1;

        

        console.log('event_id#' , $("#lichchieu_id").val())
        if ($("#lichchieu_id").val()) {
            $.post(
                "/lichchieu/get_json_data",
                {
                    event_id: $("#lichchieu_id").val(),
                    // banggia_id: $("#banggia_id").val(),
                },
                function (bigData) {
                    bigData = JSON.parse(bigData);
                    console.log('bigdata',bigData)

                    
                    
                    
                    var map_list = bigData["data"];
                    if (bigData["max_col_count"] <= 10) {
                        $("#seat-map").addClass("sh-10");
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
                            $total_dongia = $("#total_dongia"),
                            $total = $("#total"),
                            sc = $("#seat-map").seatCharts({
                                map: map_list,
                                seats: bigData["seats"],
                                naming: {
                                    top: false,
                                    left: true,
                                    // columns: ['1', '2' , '3', '4', '5', '6', '7', '8', '9', '10'],
                                    rows:['A','B','C', 'D', 'E', 'F', 'G', 'H', 'I', "J", "K", "L", 'M', 'N', 'O', 'P'],
                                    getLabel : function (character, row, column) {
                                        return row+column;
                                    }
                                },
                                legend: {
                                    node: $("#legend"),
                                    items: bigData["legend_items"],
                                },
                                click: function () {
                                    if (this.status() == "available") {
                                        console.log('this.data()', this.data())
                                        console.log('this.setting.id' , this.settings.id)
                                        // var selected_seat = "R" + this.settings.id.split("_")[0] + " S" + this.settings.id.split("_")[1];
                                        // var selected_seat =  this.settings.id.split("_")[0] + this.settings.id.split("_")[1];
                                        // var selected_seat =  this.settings.id ;
                                        var selected_seat =  this.settings.label ;
                                        console.log('this.setting.id--153' , this.settings)
                                        // $("<li>" + " Seat # " + "<b>" + selected_seat + ": $" + this.data().price + '</b> <a href="#" class="cancel-cart-item"><i class="fa fa-fw o_button_icon fa-close"></i></a></li>')
                                        $(`<li class='table-row '> <div class='col col-1'> ${selected_seat} </div> 
                                            <div class='col col-2' > ${select_loaive(bigData['banggia'])} </div> 
                                            <div class='col col-3 dongia' > ${fn_dongia(bigData['banggia'][0].dongia)}  </div> 
                                            <div class='col col-4' >  <span> <a href="#" class="cancel-cart-item"><i class="fa fa-fw o_button_icon fa-close"></i></a> </span>  </div>
                                            </li>  `)
                                            .attr("id", "cart-item-" + this.settings.id)
                                            .data("seatId", this.settings.id)
                                            .data("seatCateg", this.data().category)
                                            .appendTo($cart)
                                            .change(function () {
                                                console.log('change function run li')
                                                console.log(this)
                                                console.log($(this).find('select').val())
                                                var loaive_id = $(this).find('select').val()-1
                                                var el_dongia = $(this).find('.dongia')
                                                console.log(bigData['banggia'][loaive_id].dongia)
                                                var dongia = bigData['banggia'][loaive_id].dongia
                                                el_dongia.html(fn_dongia(dongia))
                                                // $( "#donbanhang_line > li" ).each(function( index ) {
                                                //     console.log( index + ": " + $( this ).text() );
                                                //   });

                                                $total_dongia.text(reSumTotal('.dongia') )
                                                
                                            })
                                        
                                        

                                        // $(this).find('.dongia').html(fn_dongia(dongia))
                                        $counter.text(sc.find("selected").length + 1);
                                        $total.text(recalculateTotal(sc) + this.data().price);
                                        $(".checkout-button").removeAttr("disabled");

                                        return "selected";
                                    } else if (this.status() == "selected") {
                                        //update the counter
                                        $counter.text(sc.find("selected").length - 1);
                                        //and total
                                        $total.text(recalculateTotal(sc) - this.data().price);
                                        

                                        //remove the item from our cart
                                        $("#cart-item-" + this.settings.id).remove();

                                        if (sc.find("selected").length <= 1) {
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
                        $("#donbanhang_line").on("click", ".cancel-cart-item", function () {
                            sc.get($(this).parents("li:first").data("seatId")).click();
                        });
                    }

                    $(document).on("click", ".checkout-button", function (ev) {
                        console.log('checkout-button hix hix')
                        var unavailble_seat_tickettype = {};
                        console.log('213', $(this).data("seatId")) ;
                        $("#donbanhang_line")
                            .find("li")
                            .each(function (index) {
                                console.log('find li')
                                console.log('218', unavailble_seat_tickettype)
                                if ($(this).data("seatCateg") in unavailble_seat_tickettype) {
                                    console.log('217---',$(this).data()) ;
                                    console.log('218', $(this).data("seatId")) ;
                                    var seat_list = unavailble_seat_tickettype[$(this).data("seatCateg")];
                                    seat_list.push([$(this).data("seatId"), $(this).find('select').val()]);
                                    // seat_list.push($(this).find('select').val());
                                    console.log(seat_list)
                                    unavailble_seat_tickettype[$(this).data("seatCateg")] = seat_list;
                                } 
                                else {
                                    console.log('222---',$(this).data()) ;
                                    console.log('223', $(this).data("seatId")) ;
                                    console.log('224', unavailble_seat_tickettype)
                                    console.log('225', $(this).data("seatId"))
                                    console.log('226', this)
                                    console.log('227', $(this).find('select').val())
                                    unavailble_seat_tickettype[$(this).data("seatCateg")] = [[$(this).data("seatId"), $(this).find('select').val()]]
                                    
                                    console.log('226', unavailble_seat_tickettype)
                                    console.log('228---',$(this).data()) ;
                                }
                            });
                        
                        console.log('242', unavailble_seat_tickettype)
                        ev.preventDefault();
                        ev.stopPropagation();
                        var $form = $(ev.currentTarget).closest("form");
                        var $button = $(ev.currentTarget).closest('[type="submit"]');
                        $button.attr("disabled", true);

                        return ajax.jsonRpc($form.attr("action"), "call", { unavailble_seat_tickettype: unavailble_seat_tickettype }).then(function (modal) {
                            console.log('250 unavailble_seat_tickettype', unavailble_seat_tickettype)
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
                }
            );
        }
    });

    function recalculateTotal(sc) {
        var total = 0;
        //basically find every selected seat and sum its price
        sc.find("selected").each(function () {
            total += this.data().price;
        });
        return total;
    }

    function reSumTotal(sc) {
        var total = 0;
        //basically find every selected seat and sum its price
        $(sc).each(function (index) {
            console.log($(this).text(), '296')
            if ( $(this).text() != '') {
                console.log(total, index, $(this).text());
                total += parseFloat($(this).text().replace(',',''));
            }
            
        });
        return new Intl.NumberFormat('vi-VN', { maximumSignificantDigits: 3 }).format(total);
        
    }

    // var _gaq = _gaq || [];
    // _gaq.push(["_setAccount", "UA-36251023-1"]);
    // _gaq.push(["_setDomainName", "jqueryscript.net"]);
    // _gaq.push(["_trackPageview"]);

    // (function () {
    //     var ga = document.createElement("script");
    //     ga.type = "text/javascript";
    //     ga.async = true;
    //     ga.src = ("https:" == document.location.protocol ? "https://ssl" : "http://www") + ".google-analytics.com/ga.js";
    //     var s = document.getElementsByTagName("script")[0];
    //     s.parentNode.insertBefore(ga, s);
    // })();
});

$( "select" )
    .change(function () {
        console.log('change function run')
        var str = "";
        $( "select option:selected" ).each(function() {
        str += $( this ).text() + " ";
        });
        $( "div" ).append( str );
    })
    .change();