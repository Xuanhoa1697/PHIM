# -*- coding: utf-8 -*-
import json
from odoo import fields, http, _
from odoo.addons.bus.controllers.main import BusController
from odoo.http import request
import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import AccessError, UserError


import pytz
import werkzeug
import math


class CinemaSessionReport(http.Controller):

    def _order_check_access(self, order_id, access_token=None):
        order = request.env['dm.donbanve'].browse([order_id])
        order_sudo = order.sudo()
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

    @http.route(['/cinema/dm_session_line_report/<int:pos_id>/<int:pos_line_id>'], type='http', auth="user", website=True)
    def cinema_dm_session_line_report(self, pos_id='', pos_line_id='', **kw):
        dm_session = request.env['dm.session'].search([('id','=',pos_id),('user_id','=',request.session.uid),('state','=','opened')])
        dm_session_line = request.env['dm.session.line'].browse(dm_session.current_session_line_id.id)
        # dm_session = request.env['dm.session'].browse(pos_id)
        if len(dm_session) < 1 :
            return "<div> Đăng nhập trước khi bán </div>"
        
        domain = [('dm_session_line_id', '=', dm_session.current_session_line_id.id), ('state','=', 'done') ]
        dbv_line_obj = request.env['dm.donbanve.line']

        payment_group = dbv_line_obj.read_group(domain, fields=['id', 'payment_method', 'price_total'],groupby=['payment_method'] )
        
        loaive_group = dbv_line_obj.read_group(domain, fields=['id', 'loaive', 'price_total'],groupby=['loaive'] )
        
        dbv_line_dongia = dbv_line_obj.search(domain)
        dongia_arr = dbv_line_dongia.mapped('price_total')
        

        # loaighe_group = dbv_line_obj.read_group(domain, fields=['id', 'loaighe', 'price_total'],groupby=['loaighe'] )
        
        
        dm_session.close_dm_session()
        values = {}
        values.update({
            'pos_id': pos_id,
            'pos_line_id': pos_line_id,
            'dm_session': dm_session,
            'dm_session_line': dm_session_line,
            'payment_group': payment_group, 
            'loaive_group': loaive_group,
            'tongtien': sum(dongia_arr),
            # 'orders': orders.sudo(),
        })
        return request.render("tht_cinema.session_line_report", values)
        # end list trave

    # in kết ca
    @http.route(['/cinema/open_in_ket_ca/<int:pos_line_id>'], type='http', auth="user", website=True)
    def cinema_dm_session_line_in_ket_ca(self, pos_line_id='', **kw):
        dm_session_line = request.env['dm.session.line'].browse(pos_line_id)
        # dm_session = request.env['dm.session'].browse(pos_id)
        if dm_session_line.end_at == "" or dm_session_line.state == 'opened':
            return "<div> Ca bán chưa kết thúc </div>"
        
        dm_session = request.env['dm.session'].search([('id','=',dm_session_line.dm_session_id.id)])

        # 2021/04/26 - sửa lỗi in lại kết ca cho khớp với báo , lý do sai biến domain
        domain = [('dm_session_line_id', '=', pos_line_id), ('state','=', 'done') ]
        dbv_line_obj = request.env['dm.donbanve.line']

        payment_group = dbv_line_obj.read_group(domain, fields=['id', 'payment_method', 'price_total'],groupby=['payment_method'] )
        
        loaive_group = dbv_line_obj.read_group(domain, fields=['id', 'loaive', 'price_total'],groupby=['loaive'] )
        
        dbv_line_dongia = dbv_line_obj.search(domain)
        dongia_arr = dbv_line_dongia.mapped('price_total')
        

        # loaighe_group = dbv_line_obj.read_group(domain, fields=['id', 'loaighe', 'price_total'],groupby=['loaighe'] )
        
        
        # dm_session.close_dm_session()
        values = {}
        values.update({
            'pos_id': dm_session_line.dm_session_id,
            'pos_line_id': pos_line_id,
            'dm_session': dm_session,
            'dm_session_line': dm_session_line,
            'payment_group': payment_group, 
            'loaive_group': loaive_group,
            'tongtien': sum(dongia_arr),
            # 'orders': orders.sudo(),
        })
        return request.render("tht_cinema.session_line_report", values)
        # end list trave
    
    