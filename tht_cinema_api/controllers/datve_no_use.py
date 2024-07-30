# -*- coding: utf-8 -*-

import json
from odoo import fields, http
from odoo.http import request
import math

import datetime
from dateutil.relativedelta import relativedelta


class CinemaDatve(http.Controller):

    @http.route(['''/cinema/datve/'''], type='http', auth="public", website=True)
    def cinema_datve(self, **kw):
        date_list = []
        dm_phim = request.env['dm.phim'].sudo()
        # today = datetime.datetime.now().strftime('%Y-%m-%d')
        today = datetime.date.today()
        for i in range(0,9): 
            date_list.append(today + relativedelta(days=i))

        if kw.get('ngaychieu', '') !='':
            ngaychieu = kw.get('ngaychieu')
            dm_phim_obj = dm_phim.search([('status','=', 'dangchieu'),('sudung','=', True)]) 
        else: 
            ngaychieu = today
            dm_phim_obj = dm_phim.search([('status','=', 'dangchieu'),('sudung','=', True)]) 

            # list_phim_obj = lichchieu_obj.read_group([('dm_diadiem_id', '=', dm_diadiem_obj.id),('ngaychieu','=', ngaychieu),('sudung','=', True)], fields=['id', 'dm_phim_id'],groupby=['dm_phim_id'],limit=limit, offset=offset) 
        
        # if list_phim_obj:
        #     for rec in list_phim_obj:
        #         event.append({
        #             'dm_phim': request.env['dm.phim'].sudo().browse(rec['dm_phim_id'][0]),
        #             'dm_lichchieu_obj' : lichchieu_obj.search([('ngaychieu','=', ngaychieu),('sudung','=', True),('dm_phim_id','=',rec['dm_phim_id'][1] )],order='batdau',limit=50),
        #         })
        
        values = {
            # 'date_list': date_list, 
            'today' : today,
            'dm_phim_obj': dm_phim_obj
            }


        return request.render("tht_cinema_website.phimdangchieu", values)

    # end phimdangchieu

    @http.route(['''/cinema/muave/<int:lichchieu_id>/'''], type='http', auth="user", website=True)
    def cinema_muave_lc_id(self, pos_line_id ='', lichchieu_id ='', **kwargs):
        if request.env.user.id == request.env.ref('base.public_user').id:
            return request.render('web.login', {})
        event = request.env['dm.lichchieu'].sudo().search([('id','=',lichchieu_id)])
        if len(event) < 1 :
            return "<div> Lịch chiếu không tồn tại </div>"

        values = {
            # 'dm_session': dm_session,
            'lichchieu_id': lichchieu_id, 
            'event': event,
            'dm_lichchieu': event,
        }

        return request.render("tht_cinema_website.muave", values)
        # end muave



    