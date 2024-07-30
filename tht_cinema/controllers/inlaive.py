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


class CinemaInlaive(http.Controller):

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

    # inlaive
    # cinema/inlaive_order/4/
    @http.route(['/cinema/inlaive/'], type='http', auth="user", website=True)
    def cinema_inlaive_order(self, pos_id='', **kw):
                
        DonbanveOrder = request.env['dm.donbanve']
        domain = [
            ('state', '=', 'done'),
            ('date_order', '>=', str(datetime.date.today() - relativedelta(days=7) ) )
        ]

        if kw.get('sodienthoai', '') !='' :
            domain.append(('sodienthoai','=',kw.get('sodienthoai')))
        
        if kw.get('donbanve', '') !='' :
            domain.append(('name','=',kw.get('donbanve')))

        searchbar_sortings = {
            'date': {'label': _('Order Date'), 'order': 'date_order desc'},
            'name': {'label': _('Reference'), 'order': 'name'},
            'stage': {'label': _('Stage'), 'order': 'state'},
        }
        
        # content according to pager and archive selected
        orders = DonbanveOrder.search(domain, order='date_order desc', limit=1000, offset=0)
        values = {}
        values.update({
            
            'orders': orders.sudo(),
        })
        return request.render("tht_cinema.inlaive_order", values)
        # end inlaive

    @http.route(['/cinema/inlaive_line/<int:order>'], type='http', auth="user", website=True)
    def cinema_inlaive_line(self, order=None, access_token=None, **kw):
        
        try:
            order_sudo = self._order_check_access(order, access_token=access_token)
        except AccessError:
            return request.redirect('/cinema/inlaive_order')

        values = self._order_get_page_view_values(order_sudo, access_token, **kw)
        
        return request.render("tht_cinema.inlaive_order_line", values)
    # end inlaive detail

    @http.route(['/cinema/inlaive/vexemphim/<int:order>'], type='http', auth="user", website=True)
    def cinema_inlaive_vexemphim(self, order=None, access_token=None, **kw):
        try:
            order_sudo = self._order_check_access(order, access_token=access_token)
        except AccessError:
            return request.redirect('/cinema/inlaive_order')

        values = self._order_get_page_view_values(order_sudo, access_token, **kw)

        vn_timezone = pytz.timezone('Asia/Ho_Chi_Minh')
        values['order'].write({
            'inlaive' : True,
            'nhanvienin': request.env.uid,
            'thoigianin': datetime.datetime.now(vn_timezone),
        })

        values.update({
            'event': request.env['dm.lichchieu'].browse(values['order'].dm_lichchieu_id.id)
        })
        
        return request.render("tht_cinema.inlaive_vexemphim", values)
    # end inlaive vexemphim

    @http.route(['/cinema/inlaive_line/vexemphim/<int:order>/<int:line_id>'], type='http', auth="user", website=True)
    def cinema_inlaive_line_vexemphim(self, order=None, line_id=None, access_token=None, **kw):
        try:
            order_sudo = self._order_check_access(order, access_token=access_token)
        except AccessError:
            return request.redirect('/cinema/inlaive_order')

        values = self._order_get_page_view_values(order_sudo, access_token, **kw)

        vn_timezone = pytz.timezone('Asia/Ho_Chi_Minh')
        values['order'].write({
            'inlaive' : True,
            'nhanvienin': request.env.uid,
            'thoigianin': datetime.datetime.now(vn_timezone).strftime('%d/%m/%Y %H:%M'),
        })

        order_line = request.env['dm.donbanve.line'].browse(line_id)

        values.update({
            'event': request.env['dm.lichchieu'].browse(values['order'].dm_lichchieu_id.id) ,
            'ticket': order_line,
        })
        
        return request.render("tht_cinema.inlaive_line_vexemphim", values)
    # end inlaive vexemphim

    

    
