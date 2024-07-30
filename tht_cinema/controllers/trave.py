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


class CinemaTrave(http.Controller):

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

    # trả vé
    # cinema/trave_order/4/
    @http.route(['/cinema/trave_order/<int:pos_id>/'], type='http', auth="user", website=True)
    def cinema_trave_order(self, pos_id='', **kw):
        dm_session = request.env['dm.session'].search([('id','=',pos_id),('user_id','=',request.session.uid),('state','=','opened')])
        # dm_session = request.env['dm.session'].browse(pos_id)
        if len(dm_session) < 1 :
            return "<div> Đăng nhập trước khi bán </div>"
        
        DonbanveOrder = request.env['dm.donbanve']
        domain = [
            ('state', '=', 'done'),
            ('date_order', '>=', str(datetime.date.today() - relativedelta(days=30) ) )
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
        orders = DonbanveOrder.search(domain, order='name desc', limit=1000, offset=0)
        values = {}
        values.update({
            'dm_session': dm_session,
            'orders': orders.sudo(),
        })
        return request.render("tht_cinema.trave_order", values)
        # end list trave
    
    @http.route(['/cinema/trave_line/<int:pos_id>/<int:order>'], type='http', auth="user", website=True)
    def cinema_trave_line(self, pos_id='', order=None, access_token=None, **kw):
        dm_session = request.env['dm.session'].search([('id','=',pos_id),('user_id','=',request.session.uid),('state','=','opened')])
        # dm_session = request.env['dm.session'].browse(pos_id)
        if len(dm_session) < 1 :
            return "<div> Đăng nhập trước khi bán </div>"

        try:
            order_sudo = self._order_check_access(order, access_token=access_token)
        except AccessError:
            return request.redirect('/cinema/trave_order')

        values = self._order_get_page_view_values(order_sudo, access_token, **kw)
        values.update({
            'dm_session': dm_session,
        })
        return request.render("tht_cinema.trave_order_line", values)
    # end dondattruoc detail

    @http.route(['/cinema/trave_inve/<int:pos_id>/<int:order>/'], type='http', auth="user", website=True)
    def cinema_trave_inve(self, pos_id='', order=None, access_token=None, **kw):
        dm_session = request.env['dm.session'].search([('id','=',pos_id),('user_id','=',request.session.uid),('state','=','opened')])
        # dm_session = request.env['dm.session'].browse(pos_id)
        if len(dm_session) < 1 :
            return "<div> Đăng nhập trước khi bán </div>"

        try:
            order_sudo = self._order_check_access(order, access_token=access_token)
        except AccessError:
            return request.redirect('/cinema/trave_order')

        
        values = self._order_get_page_view_values(order_sudo, access_token, **kw)

        payment_method = kw.get('payment_method', '')
        
        order_sudo.write({'state': 'done', 'payment_method': payment_method})
        # order_sudo.donbanve_invoice_create()
        
        return request.render("tht_cinema.dm_website_cinema_trave_inve", 
            {'tickets': values['order'], 'dm_session': dm_session, 'availability_check': 1 })
    # end dondattruoc in ve

    @http.route('/cinema/rpc/trave_line/delete', type='json', auth='user')
    def cinema_rpc_trave_line_delete(self, **k):
        if k.get('id', '') :
            dm_donbanve_line = request.env['dm.donbanve.line'].sudo().browse(k.get('id'))
            dm_donbanve_line.line_trave_hoantien()
            dm_donbanve = request.env['dm.donbanve'].sudo().browse(dm_donbanve_line.dm_donbanve_id.id)._amount_all()
            
        return dm_donbanve_line.unlink()
    
    @http.route('/cinema/rpc/trave/delete', type='json', auth='user')
    def cinema_rpc_trave_delete(self, **k):
        if k.get('id', '') :
            dm_donbanve = request.env['dm.donbanve'].sudo().browse(k.get('id'))
            dm_donbanve.trave_hoantien()
        return dm_donbanve.unlink()
    
    @http.route('/cinema/rpc/trave/delete_draft', type='json', auth='user')
    def cinema_rpc_trave_delete_draft(self, **k):
        if k.get('id', '') :
            domain = [('dm_lichchieu_id','=',k.get('id')), ('state','=','draft')]
            dm_donbanve = request.env['dm.donbanve'].sudo().search(domain)
        return dm_donbanve.unlink()


