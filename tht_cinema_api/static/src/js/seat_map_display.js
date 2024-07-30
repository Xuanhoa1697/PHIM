odoo.define('tht_cinema.seat_map_display', function (require) {
    "use strict";
    
	var Widget = require('web.Widget');
	var session = require('web.session');
	var core = require('web.core');
	var bus = require('bus.bus').bus;

	var SeatMapDisplayScreen = Widget.extend({
	    init: function() {
	    	var self = this;
	        this._super(arguments[0],{});	        
	    },
	    start: function(){
            this._super();
	    	var self = this;
	        bus.update_option('seat_map.display', session.uid);
            bus.on('notification', self, self._onNotificationSeatmap);
	    	bus.start_polling();
	    },

	    _onNotificationSeatmap: function(notifications2){
			for (var notif of notifications2) {
	    		if(notif[1][0] == "seat_map_display_data"){					
					let seat_id = notif[1][1].seat_id
					let pos_source = notif[1][1].pos_source
					let db_lc = notif[1][1].db_lc
					let lichchieu_id = notif[1][1].lichchieu_id
					let seat_arr = db_lc[lichchieu_id]
					let flag = notif[1][1].flag
					
					if (pos_source != pos_id){
						console.log('true :>> ', true);
						flag == 'add' && lichchieu_id == dm_lichchieu_id ? sc.get([seat_id]).status('unavailable noClick') : ''
						flag == 'remove' && lichchieu_id == dm_lichchieu_id ? sc.get([seat_id]).status('available') : ''
					} 
					flag == 'first_load' && seat_arr && lichchieu_id == dm_lichchieu_id ? sc.get(seat_arr).status('unavailable noClick') : ''

					if (notif[1][1].pos_selected){
						lichchieu_id == dm_lichchieu_id ? sc.get(notif[1][1].pos_selected).status('available') : ''
					}
					
	    		}
	    	}
	    	
	    },
	    
	});

	core.action_registry.add('seat_map_display.ui', SeatMapDisplayScreen);
});


