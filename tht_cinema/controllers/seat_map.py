# -*- coding: utf-8 -*-
import json
from odoo import fields, http, _
from odoo.addons.bus.controllers.main import BusController
from odoo.http import request
import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import AccessError, UserError

import pickle


import pytz
import werkzeug
import math

# from .seat_db import db_lc, db_pos
from .seat_db import db_seat
    
class SeatMapController(BusController):
    def _poll(self, dbname, channels, last, options):
        """Add the relevant channels to the BusController polling."""
        if options.get('seat_map.display'):
            channels = list(channels)
            seat_map_channel = (
                request.db,
                'seat_map.display',
                options.get('seat_map.display')
            )
            channels.append(seat_map_channel)

        return super(SeatMapController, self)._poll(dbname, channels, last, options)

class SeatMapDisplay(http.Controller):

    @http.route(['''/cinema/map/first_load/'''], type='json', auth="user",  csrf=False)
    def cinema_map_first_load(self, **kw):
        val ={}
        data = {
            'flag': kw.get('flag', ''),
            'seat_id': kw.get('seat_id', ''),
            'pos_source': kw.get('pos_source', ''),
            'lichchieu_id': kw.get('lichchieu_id', ''),
        }
        db_seat_lc = db_seat('db_lc')
        db_lc = db_seat_lc.load()

        vals = {
            'from': '/cinema/check_seat_map_status/', 
            'db_lc': db_lc,
            'flag': data['flag'],
            'seat_id': data['seat_id'],
            'pos_source': data['pos_source'],
            'lichchieu_id': data.get('lichchieu_id', ''),
            
        }
        
        if data['lichchieu_id'] and data['pos_source'] :
            key_lichchieu = data['lichchieu_id']
            key_pos_lc = '{}_{}'.format(data['pos_source'],data['lichchieu_id'])

            if key_pos_lc in db_lc:
                for i in db_lc[key_pos_lc]: 
                    if i in db_lc[key_lichchieu]:
                        db_lc[key_lichchieu].remove(i)
                    # db_lc[key_pos_lc].remove(i)
                db_lc[key_pos_lc].clear()
       
            db_seat_lc.dump(db_lc)                

        return vals

    @http.route(['''/cinema/map/out/'''], type='json', auth="user",  csrf=False)
    def cinema_map_out(self, **kw):
        pos_selected = []
        
        val ={}
        data = {
            'flag': kw.get('flag', ''),
            'seat_id': kw.get('seat_id', ''),
            'pos_source': kw.get('pos_source', ''),
            'lichchieu_id': kw.get('lichchieu_id', ''),
        }

        db_seat_lc = db_seat('db_lc')
        db_lc = db_seat_lc.load()

        if data['lichchieu_id'] and data['pos_source'] :
            key_lichchieu = data['lichchieu_id']
            key_pos_lc = '{}_{}'.format(data['pos_source'],data['lichchieu_id'])

            if key_pos_lc in db_lc:
                pos_selected = db_lc[key_pos_lc].copy()
                for i in db_lc[key_pos_lc]: 
                    if i in db_lc[key_lichchieu]:
                        db_lc[key_lichchieu].remove(i)
                    # db_lc[key_pos_lc].remove(i)
                db_lc[key_pos_lc].clear()
        
            db_seat_lc.dump(db_lc)   


        notifications = []
        vals = {
            'from': '/cinema/check_seat_map_status/', 
            'db_lc': db_lc,
            'flag': data['flag'],
            'seat_id': data['seat_id'],
            'pos_source': data['pos_source'],
            'lichchieu_id': data.get('lichchieu_id', ''),
            'pos_selected': pos_selected,
            
        }
        users_list = []
        for user in request.env['dm.session'].sudo().search([],limit=50):
            users_list.append(user.user_id.id) if user.user_id.id not in users_list else ''
        for user_id in users_list:
            notifications.append( ((request._cr.dbname, 'seat_map.display', user_id), ('seat_map_display_data', vals)) )
        request.env['bus.bus'].sendmany(notifications)

        return ''

    @http.route(['''/cinema/check_seat_map_status/'''], type='json', auth="user",  csrf=False)
    def cinema_check_seat_map_status(self, **kw):
        val ={}
        data = {
            'flag': kw.get('flag', ''),
            'seat_id': kw.get('seat_id', ''),
            'pos_source': kw.get('pos_source', ''),
            'lichchieu_id': kw.get('lichchieu_id', ''),
        }

        db_seat_lc = db_seat('db_lc')
        db_lc = db_seat_lc.load()


        notifications = []
        vals = {
            'from': '/cinema/check_seat_map_status/', 
            'db_lc': db_lc,
            'flag': data['flag'],
            'seat_id': data['seat_id'],
            'pos_source': data['pos_source'],
            'lichchieu_id': data.get('lichchieu_id', ''),
            
        }

        users_list = []
        for user in request.env['dm.session'].sudo().search([],limit=50):
            users_list.append(user.user_id.id) if user.user_id.id not in users_list else ''
        for user_id in users_list:
            notifications.append( ((request._cr.dbname, 'seat_map.display', user_id), ('seat_map_display_data', vals)) )
        request.env['bus.bus'].sendmany(notifications)

        
        if data['lichchieu_id'] and data['pos_source'] :
            key_lichchieu = data['lichchieu_id']
            key_pos_lc = '{}_{}'.format(data['pos_source'],data['lichchieu_id'])

            if key_pos_lc in db_lc:
                for i in db_lc[key_pos_lc]: 
                    if i in db_lc[key_lichchieu]:
                        db_lc[key_lichchieu].remove(i)
                    # db_lc[key_pos_lc].remove(i)
                db_lc[key_pos_lc].clear()
            db_seat_lc.dump(db_lc)                

        return ''
    
    
    @http.route(['''/cinema/seat_map/'''], type='json', auth="user", website=True)
    def tht_polling3(self, **kw):
        data = {
            'flag': kw.get('flag', ''),
            'seat_id': kw.get('seat_id', ''),
            'pos_source': kw.get('pos_source', ''),
            'lichchieu_id': kw.get('lichchieu_id', ''),
        }

        self.broadcast_seat_map(data)

        return True

    def broadcast_seat_map(self, data):
        db_seat_lc = db_seat('db_lc')
        db_lc = db_seat_lc.load()

        if data['lichchieu_id'] :
            lichchieu_id = data['lichchieu_id']
            if lichchieu_id not in db_lc:
                db_lc.update({ lichchieu_id: []})
            if data['flag'] == 'add' :
                db_lc[lichchieu_id].append(data['seat_id']) if data['seat_id'] not in db_lc[lichchieu_id] else ''
            if data['flag'] == 'remove' :
                db_lc[lichchieu_id].remove(data['seat_id']) if data['seat_id'] in db_lc[lichchieu_id] else ''

        if data['lichchieu_id'] and data['pos_source'] :
            key_pos_lc = '{}_{}'.format(data['pos_source'],data['lichchieu_id'])
            if key_pos_lc not in db_lc:
                db_lc.update({ key_pos_lc: []})
            if data['flag'] == 'add' :
                db_lc[key_pos_lc].append(data['seat_id']) if data['seat_id'] not in db_lc[key_pos_lc] else ''
            if data['flag'] == 'remove' :
                db_lc[key_pos_lc].remove(data['seat_id']) if data['seat_id'] in db_lc[key_pos_lc] else ''

        db_seat_lc.dump(db_lc)

        notifications = []
        vals = {
            'from': '/cinema/seat_map/', 
            'db_lc': db_lc,
            'seat_id': data['seat_id'],
            'pos_source': data['pos_source'],
            'lichchieu_id': data.get('lichchieu_id', ''),
            'flag': data['flag'],
            
        }
        
        users_list = []
        for user in request.env['dm.session'].sudo().search([],limit=50):
            users_list.append(user.user_id.id) if user.user_id.id not in users_list else ''
        for user_id in users_list:
            notifications.append( ((request._cr.dbname, 'seat_map.display', user_id), ('seat_map_display_data', vals)) )
        
        # request.env['bus.bus'].sendone('seat_map.display',notifications)
        request.env['bus.bus'].sudo().sendmany(notifications)

        return True

