# -*- coding: utf-8 -*-

import json

from werkzeug import redirect
from odoo import fields, http
from odoo.http import request
from odoo import tools
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import AccessError, UserError
from odoo.tools import html_escape


import pytz
import math
import json
import datetime
from dateutil.relativedelta import relativedelta


class ThtCinemaWebsitePhim(http.Controller):

    def _order_access(self, order_id, access_token=None):
        order = request.env['dm.donbanve'].sudo()
        order_sudo = order.browse([order_id])
        try:
            order.check_access_rights('read')
            order.check_access_rule('read')
        except AccessError:
            if not access_token or not consteq(order_sudo.access_token, access_token):
                raise
        return order_sudo
    
    def _order_get_page_view_values(self, order, access_token, **kwargs):
        values = {
            'order': order,
        }
        if access_token:
            values['no_breadcrumbs'] = True
            values['access_token'] = access_token
        return values

    
    @http.route(['/cnm/phim/dangchieu'], type='http', auth="public", methods=['GET'], csrf=False, website=True)
    def cnm_phim_dangchieu(self, **kw):
        # today = datetime.date.today()
        today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        event = []
        
        event_obj = request.env['dm.lichchieu'].sudo()
        diadiem_obj = request.env['dm.diadiem'].sudo().search([])
        # if kwargs.get('lichchieu_id', False):
        #     lichchieu_id = kwargs.get('lichchieu_id')
        #     # banggia_id = kwargs.get('banggia_id')
        #     event = event_obj.sudo().browse(lichchieu_id)
        # event = event_obj.search([('sudung','=', True)],limit=500)
        phim_obj = event_obj.read_group([('sudung','=', True), ('batdau','>=', today)], fields=['id', 'dm_phim_id'],groupby=['dm_phim_id']) 
        if phim_obj:
            for rec in phim_obj:
                event.append({
                    'dm_phim': request.env['dm.phim'].sudo().browse(rec['dm_phim_id'][0]),
                    'dm_lichchieu_obj' : event_obj.search([('sudung','=', True),('dm_phim_id','=',rec['dm_phim_id'][1] )],limit=500),
                })
        
     
        response = http.Response(template='tht_cinema_website.dangchieu', qcontext= { 'event': event, 'diadiem_obj': diadiem_obj} )
        return response.render()  
    #end dangchieu

    # lich chieu theo phim_id
    @http.route(['''/cnm/phim/dangchieu/<int:phim_id>/'''], type='http', auth="public", website=True)
    def cnm_phim_dangchieu_phim_id(self, phim_id='', **kwargs):
        event = []
        date_list = []
        dm_diadiem_obj = request.env['dm.diadiem'].sudo().search([],limit=1)
        lichchieu_obj = request.env['dm.lichchieu'].sudo()
        # today = datetime.datetime.now().strftime('%Y-%m-%d')
        today = datetime.date.today()
        for i in range(0,9): 
            date_list.append(today + relativedelta(days=i))

        now_val = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if kwargs.get('ngaychieu', '') !='':
            ngaychieu = kwargs.get('ngaychieu')
        else: 
            ngaychieu = today
        domain_val = [('dm_diadiem_id', '=', dm_diadiem_obj.id), ('ngaychieu','=', ngaychieu),
                    ('sudung','=', True),('dm_phim_id','=', phim_id), ('batdau','>=', now_val)]
        list_phim_obj = lichchieu_obj.read_group(domain_val, fields=['id', 'dm_phim_id'],groupby=['dm_phim_id']) 
        if list_phim_obj:
            for rec in list_phim_obj:
                event.append({
                    'dm_phim': request.env['dm.phim'].sudo().browse(rec['dm_phim_id'][0]),
                    'dm_lichchieu_obj' : lichchieu_obj.search([('ngaychieu','=', ngaychieu),('sudung','=', True),('dm_phim_id','=',rec['dm_phim_id'][1] ), ('batdau','>=', now_val)],order='batdau',limit=500),
                })
        
        values = {
            'ngaychieu' : ngaychieu,
            'dm_diadiem_obj': dm_diadiem_obj, 
            'date_list': date_list, 
            'event': event,
            'list_phim_obj': list_phim_obj,
            'phim_id': phim_id,
            }

        return request.render("tht_cinema_website.dangchieu_phim_id", values)

    # end ccnm_phim_dangchieu_phim_id
    
    
    @http.route(['/cnm/phim/lichchieu/<int:phim_id>'], type='http', auth="user", methods=['GET'], csrf=False, website=True)
    def cnm_phim_lichchieu(self, phim_id='', **kw):
        today = datetime.datetime.now()

        event = []
        
        event_obj = request.env['dm.lichchieu']
        diadiem_obj = request.env['dm.diadiem'].search([])
        # if kwargs.get('lichchieu_id', False):
        #     lichchieu_id = kwargs.get('lichchieu_id')
        #     # banggia_id = kwargs.get('banggia_id')
        #     event = event_obj.sudo().browse(lichchieu_id)
        # event = event_obj.search([('sudung','=', True)],limit=500)
        dm_phim_obj = request.env['dm.phim'].sudo().browse(phim_id)
        phim_obj = event_obj.read_group([('sudung','=', True),('dm_phim_id','=',phim_id)], fields=['id', 'ngaychieu'],groupby=['ngaychieu:day']) 
        if phim_obj:
            for rec in phim_obj:
                event.append({
                    # 'dm_phim': request.env['dm.phim'].browse(rec['ngaychieu'][0]),
                    'dm_phim': request.env['dm.phim'].browse(phim_id),
                    # 'dm_lichchieu_obj' : event_obj.search([('sudung','=', True) ],limit=100),
                    'dm_lichchieu_obj' : event_obj.search(rec['__domain'],limit=100),
                    'dm_lc': event_obj.search(rec['__domain'],limit=1),
                })
        
     
        response = http.Response(template='tht_cinema_website.lichchieu', qcontext= { 'event': event, 'diadiem_obj': diadiem_obj, 'dm_phim_obj': dm_phim_obj} )
        return response.render()      
