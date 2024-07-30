odoo.define("event_seat_booking_board", function (require) {
    "use strict";

    var core = require("web.core");
    var Widget = require("web.Widget");
    var rpc = require("web.rpc");
    var ajax = require("web.ajax");
    var QWeb = core.qweb;
    var _t = core._t;

    var AbstractAction = require("web.ControlPanelMixin");

    var seatBookingBoard = Widget.extend({
        template: "seatBookingBoardMain",

        events: {},

        init: function (parent, action) {
            var firstSeatLabel = 1;

            if (action.context && action.context.active_id && action.context.active_model) {
                $.post(
                    "/get_json_data_from_registration",
                    {
                        event_registration_id: action.context.active_id,
                    },
                    function (bigData) {
                        bigData = JSON.parse(bigData);
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
                            var $cart = $("#selected-seats"),
                                $counter = $("#counter"),
                                $total = $("#total"),
                                sc = $("#seat-map").seatCharts({
                                    map: map_list,
                                    seats: bigData["seats"],
                                    naming: {
                                        top: false,
                                        getLabel: function (character, row, column) {
                                            return firstSeatLabel++;
                                        },
                                    },
                                    legend: {
                                        node: $("#legend"),
                                        items: bigData["legend_items"],
                                    },
                                    click: function () {
                                        if (this.status() == "available") {
                                            var selected_seat = "R" + this.settings.id.split("_")[0] + " S" + this.settings.id.split("_")[1];
                                            $(
                                                "<li>" +
                                                    this.data().category +
                                                    " Seat # " +
                                                    "<b>" +
                                                    selected_seat +
                                                    ": $" +
                                                    this.data().price +
                                                    '</b> <a href="#" class="cancel-cart-item"><i class="fa fa-fw o_button_icon fa-close"></i></a></li>'
                                            )
                                                .attr("id", "cart-item-" + this.settings.id)
                                                .data("seatId", this.settings.id)
                                                .data("seatCateg", this.data().category)
                                                .appendTo($cart);

                                            $counter.text(sc.find("selected").length + 1);
                                            $total.text(recalculateTotal(sc) + this.data().price);
                                            $(".change-seat-button").removeAttr("disabled");

                                            return "selected";
                                        } else if (this.status() == "selected") {
                                            //update the counter
                                            $counter.text(sc.find("selected").length - 1);
                                            //and total
                                            $total.text(recalculateTotal(sc) - this.data().price);

                                            //remove the item from our cart
                                            $("#cart-item-" + this.settings.id).remove();

                                            if (sc.find("selected").length <= 1) {
                                                $(".change-seat-button").attr("disabled", "disabled");
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
                            $("#selected-seats").on("click", ".cancel-cart-item", function () {
                                sc.get($(this).parents("li:first").data("seatId")).click();
                            });
                        }

                        $(document).on("click", ".change-seat-button", function (ev) {
                            var seat_list = [];
                            var seat_categ = "";
                            $("#selected-seats")
                                .find("li")
                                .each(function (index) {
                                    seat_list.push($(this).data("seatId"));
                                    seat_categ = $(this).data("seatCateg");
                                });
                            if (seat_list.length > 1) {
                                alert("You cannot select more then 1 seat !");
                            } else {
                                $.post(
                                    "/change_seat",
                                    {
                                        event_registration_id: action.context.active_id,
                                        seat_no: seat_list[0],
                                        seat_categ: seat_categ,
                                    },
                                    function (bigData) {
                                        location.reload();
                                    }
                                );
                            }
                        });
                    }
                );

                function recalculateTotal(sc) {
                    var total = 0;
                    //basically find every selected seat and sum its price
                    sc.find("selected").each(function () {
                        total += this.data().price;
                    });
                    return total;
                }

                var _gaq = _gaq || [];
                _gaq.push(["_setAccount", "UA-36251023-1"]);
                _gaq.push(["_setDomainName", "jqueryscript.net"]);
                _gaq.push(["_trackPageview"]);

                (function () {
                    var ga = document.createElement("script");
                    ga.type = "text/javascript";
                    ga.async = true;
                    ga.src = ("https:" == document.location.protocol ? "https://ssl" : "http://www") + ".google-analytics.com/ga.js";
                    var s = document.getElementsByTagName("script")[0];
                    s.parentNode.insertBefore(ga, s);
                })();
                return this._super.apply(this, arguments);
            }
        },

        start: function () {
            var self = this;

            return this.load();
        },

        load: function (dashboards) {
            var self = this;
        },
    });

    core.action_registry.add("eventBoard.main", seatBookingBoard);

    return {
        seatBookingBoard: seatBookingBoard,
    };
});
