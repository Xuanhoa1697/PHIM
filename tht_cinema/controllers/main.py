# -*- coding: utf-8 -*-
import json
from odoo import fields, http, _
from odoo.addons.bus.controllers.main import BusController
from odoo.http import request
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
from odoo import tools

import datetime
from dateutil.relativedelta import relativedelta

import pytz
import werkzeug
import math

# def check_sv_socket_io(ip_addr):
#     print(ip_addr)
#     if ip_addr == '':
#         print('vui lòng cài đặt ')
#     return ip_addr


class DmSodoghe(http.Controller):

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

    def _process_tickets_form(self,  event, form_details):
        # data in vexemphim
        ticket_order = {}
        unavailble_seat_tickettype = form_details.get(
            'unavailble_seat_tickettype')
        nb_register_data = []

        for each_type in unavailble_seat_tickettype:
            ticket_obj = request.env['dm.lichchieu'].sudo().search(
                [('id', '=', event.id)], limit=1)
                # [('dm_phim_id', '=', event.id), ('name', 'ilike', each_type)], limit=1)
            if ticket_obj:
                seat_list = []
                for seat_arr in unavailble_seat_tickettype[each_type]:
                    if seat_arr:
                        
                        seat = seat_arr[0]
                        # seat_list.append([seat.split('_')[0]+seat.split('_')[1], seat_arr[1] ])
                        seat_list.append([seat_arr[0], seat_arr[1], seat_arr[3] ])

                nb_register_data.append({
                                        'id': ticket_obj.id,
                                         'name': each_type, # loai ghe
                                        #  'quantity': len(unavailble_seat_tickettype[each_type]),
                                        #  'price': ticket_obj.price,
                                         'seat_list': seat_list
                                         })

        return nb_register_data
    
    # don gia ve
    def _dongiave(self, dm_banggia_id, dm_loaighe_id, dm_loaive_id):
        dongia_obj = request.env['dm.banggia.line'].sudo().search(
                [('dm_banggia_id', '=', dm_banggia_id.id), 
                    ('dm_loaighe_id', '=', int(dm_loaighe_id)),
                    ('dm_loaive_id', '=', int(dm_loaive_id)),
                ], limit=1)
        return dongia_obj.dongia


    def _donbanve_create_attendees_from_registration_post(self, event, registration_data, donbanve_info):
        donbanve_line_ids = []
        total_dongia = []
        for rec_arr in registration_data:
            for rec in rec_arr['seat_list']:
                giave = self._dongiave(event.dm_banggia_id, rec_arr['name'], rec[1])
                total_dongia.append(float(rec[1]))
                rec_one = {
                    'loaighe': int(rec_arr['name']),
                    'dm_lichchieu_id': event.id,
                    'name': rec[0],
                    'vitrighe': rec[0],
                    'dongia': rec[1],
                    'soluong': 1,
                    'price_total': rec[1],
                    'loaive': rec[2],
                    'dm_session_id': donbanve_info['dm_session_id'],
                    'dm_session_line_id': donbanve_info['dm_session_line_id'],
                }
                donbanve_line_ids.append((0,0, rec_one))


        #     registrations_to_create.append(registration_values)

        list_seat = []
        list_seat.append({
            'name': 'seat1'
        })

        donbanve_state = 'done'
        donbanve_source = 'posbanve'
        date_hoadon = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        print_status = True
        if donbanve_info['datvetruoc'] == 'True':
            donbanve_state = 'draft'
            donbanve_source = 'posdatvetruoc'
            print_status = False
            date_hoadon = ''

        registrations_to_create = {
            'dm_lichchieu_id' : event.id,
            'user_id': request.session.uid,
            # 'dm_diadiem_id': event.dm_diadiem_id.id,
            'marap': event.dm_diadiem_id.marap,
            'dm_phim_id' : event.dm_phim_id.id,
            'dm_phong_id' : event.dm_phong_id.id,
            'dm_banggia_id' : event.dm_banggia_id.id,
            'dm_donbanve_line_ids': donbanve_line_ids,
            'amount_total': sum(total_dongia),
            'state': donbanve_state,
            'source': donbanve_source,
            'print_status': print_status,
            'makhachhang': donbanve_info['makhachhang'],
            'sodienthoai': donbanve_info['sodienthoai'],
            'date_order': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            # 'payment_method': donbanve_info['payment_method'],
            'ht_thanhtoan': donbanve_info['ht_thanhtoan'],
            # self._ptthanhtoan(donbanve_info['ptthanhtoan_id']).hinhthucthanhtoan
            # 'dm_ptthanhtoan_id': donbanve_info['payment_method'],
            'dm_ptthanhtoan_id': donbanve_info['ptthanhtoan_id'],
            
            'dm_session_id': donbanve_info['dm_session_id'],
            'dm_session_line_id': donbanve_info['dm_session_line_id'],
            'date_hoadon': date_hoadon,
            # 'date_hoadon': datetime.datetime.now(vn_timezone).strftime('%d/%m/%Y %H:%M:%S'),
        }
        # try: 
        #     create_dbv = request.env['dm.donbanve'].sudo().create(registrations_to_create)
        #     create_dbv.donbanve_invoice_create()
        #     return [create_dbv,create_dbv.name]
        # except:
        #     return False
        create_dbv = request.env['dm.donbanve'].sudo().create(registrations_to_create)
        # create_dbv.donbanve_invoice_create()
        return [create_dbv,create_dbv.name]

    @http.route(['/donbanve/<model("dm.lichchieu"):event>/registration/seat'], type='json', auth="public", methods=['POST'], website=True)
    def registration_new(self, event, **post):
        # o11 khong co
        # if not event.can_access_from_current_website():
        #     raise werkzeug.exceptions.NotFound()
        
        tickets = self._process_tickets_form(event, post)

        ptthanhtoan_id_val = post.get('ptthanhtoan_id', '')

        if ptthanhtoan_id_val == '':
            donbanve_info = {
                'makhachhang' : post.get('makhachhang', '') ,
                'sodienthoai' : post.get('sodienthoai', '') ,
                'payment_method' : '' ,
                'ptthanhtoan_id' : '' ,
                # đặt vé trước default là tiền mặt
                'ht_thanhtoan': 'cash', 
                'dm_session_line_id' : post.get('dm_session_line_id', '') ,
                'dm_session_id' : post.get('dm_session_id', '') ,
                'datvetruoc' : post.get('datvetruoc', '') ,
            }

        else: 
            ptthanhtoan = request.env['dm.ptthanhtoan'].sudo().browse(int(post.get('ptthanhtoan_id', '')))
            
            donbanve_info = {
                'makhachhang' : post.get('makhachhang', '') ,
                'sodienthoai' : post.get('sodienthoai', '') ,
                'payment_method' : post.get('payment_method', '') ,
                'ptthanhtoan_id' : post.get('ptthanhtoan_id', '') ,
                'ht_thanhtoan': ptthanhtoan.ht_thanhtoan, 
                'dm_session_line_id' : post.get('dm_session_line_id', '') ,
                'dm_session_id' : post.get('dm_session_id', '') ,
                'datvetruoc' : post.get('datvetruoc', '') ,
            }
        
        availability_check = True
        
        if not tickets:
            return False

        donbanve_sudo = self._donbanve_create_attendees_from_registration_post( event, tickets , donbanve_info)
        vn_timezone = pytz.timezone('Asia/Ho_Chi_Minh')
        # return True
        if donbanve_sudo :
            madonbanve = donbanve_sudo[1]
            if donbanve_info['datvetruoc'] == 'True':
                return request.env['ir.ui.view'].render_template("tht_cinema.dm_website_cinema_booking_datvetruoc", 
            {'tickets': tickets, 'event': event, 'availability_check': availability_check, 'vn_timezone': vn_timezone, 'madonbanve': madonbanve  })
            else:
                return request.env['ir.ui.view'].render_template("tht_cinema.dm_website_cinema_booking_result", 
            {'tickets': tickets, 'event': event, 'availability_check': availability_check, 'vn_timezone': vn_timezone, 'madonbanve': madonbanve  })
        else:
            return False

    @http.route(['''/phong/get_json_data'''], type='http', auth="public", website=True, csrf=False)
    def phong_get_json_data(self, event_id, banggia_id):
        # event_obj = request.env['event.event'].sudo().browse(int(event_id))
        phong_obj = request.env['dm.phong'].sudo().browse(int(event_id))
        banggia_obj = request.env['dm.banggia'].sudo().browse(int(banggia_id))
        data = []
        seats = {}
        legend_items = []
        max_col_count = 0
        ticket_type_list = ['0', 'a', 'b', 'c', 'd', 'e',
                            'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o']
        # if event_obj and event_obj.event_ticket_ids:
        if phong_obj and phong_obj.dm_phong_line_ids:
            # max_col_ticket = event_obj.event_ticket_ids.sorted(
            max_col_ticket = phong_obj.dm_phong_line_ids.sorted(
                lambda x: x.col_count, reverse=True)[:1]
            max_cols = max_col_ticket.col_count
            if max_col_count < max_cols:
                max_col_count = max_cols
            i = 1
            # for each_ticket_id in event_obj.event_ticket_ids.sorted(lambda x: x.sequence):
            for each_ticket_id in phong_obj.dm_phong_line_ids.sorted(lambda x: x.sequence):
                seats[ticket_type_list[i]] = {
                    # 'price': each_ticket_id.price, 
                    # 'classes': ticket_type_list[i]+'-class', 
                    # 'category': each_ticket_id.name}
                    'price': each_ticket_id.price, 
                    'classes': ticket_type_list[i]+'-class', 
                    'category': each_ticket_id.dm_loaighe_id.id} # loai ghe id
                legend_items.append(
                    [ticket_type_list[i], 'available', each_ticket_id.dm_loaighe_id.name])
                    # [ticket_type_list[i], 'available', each_ticket_id.name])
                for row in each_ticket_id.seat_arrangement_ids.sorted(lambda m: m.row):

                    seat_arrangement = ''
                    j = 1
                    for col in range(max_cols):
                        if row.seat_selection_ids and row.seat_selection_ids.filtered(lambda y: y.name == str(j)):
                            seat_arrangement += ticket_type_list[i]
                        else:
                            seat_arrangement += '_'
                        j += 1
                    data.append(seat_arrangement)
                i += 1

        legend_items.append(['f', 'unavailable', 'Đã bán'])
        
        
        # donbanve_line_obj = request.env['dm.donbanve.line'].sudo().search([('dm_lichchieu_id','=',int(event_id))])
        booked_seat_list = []
        # if event_obj and event_obj.dm_donbanve_line_ids:
        #     for booked_seat in event_obj.dm_donbanve_line_ids:
        #         booked_seat_list.append(booked_seat.name)

        banggia = []
        for bg in banggia_obj.dm_banggia_line_ids:
            banggia.append({
                'name': bg.name,
                'dm_loaighe_name': bg.dm_loaighe_id.name,
                'dm_loaive_name': bg.dm_loaive_id.name,
                'dm_loaighe_id': bg.dm_loaighe_id.id,
                'dm_loaive_id': bg.dm_loaive_id.id,
                'dongia': bg.dongia,
                
            })
        
        columns_map = []
        if phong_obj.hangngang:
            for cl in range(phong_obj.hangngang):
                columns_map.append(cl)

        bigData = {
            'data': data,
            'seats': seats,
            'legend_items': legend_items,
            'booked_seat': booked_seat_list,
            'max_col_count': max_col_count,
            'banggia': banggia,
            'columns_map': columns_map
        }

        return json.dumps(bigData)
    # end def phong_get_json_data

    # so do ghe trong su kien
    @http.route(['''/lichchieu/get_json_data'''], type='http', auth="public", website=True, csrf=False)
    def lichchieu_get_json_data(self, event_id):
        # event_obj = request.env['event.event'].sudo().browse(int(event_id))
        lichchieu_obj = request.env['dm.lichchieu'].sudo().browse(int(event_id))
        phong_obj = request.env['dm.phong'].sudo().browse(int(lichchieu_obj.dm_phong_id.id))
        banggia_obj = request.env['dm.banggia'].sudo().browse(int(lichchieu_obj.dm_banggia_id.id))
        
        data = []
        seats = {}
        legend_items = []
        max_col_count = 0
        ticket_type_list = ['0', 'a', 'b', 'c', 'd', 'e',
                            'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o']
        # if event_obj and event_obj.event_ticket_ids:
        if phong_obj and phong_obj.dm_phong_line_ids:
            # max_col_ticket = event_obj.event_ticket_ids.sorted(
            max_col_ticket = phong_obj.dm_phong_line_ids.sorted(
                lambda x: x.col_count, reverse=True)[:1]
            max_cols = max_col_ticket.col_count
            if max_col_count < max_cols:
                max_col_count = max_cols
            i = 1
            # for each_ticket_id in event_obj.event_ticket_ids.sorted(lambda x: x.sequence):
            for each_ticket_id in phong_obj.dm_phong_line_ids.sorted(lambda x: x.sequence):
                if each_ticket_id.dm_loaighe_id.kieughe == 'doi':
                    seats[ticket_type_list[i]] = {
                        'price': each_ticket_id.price, 
                        'classes': 's'+'-class', 
                        'category': each_ticket_id.dm_loaighe_id.id} # loai ghe id
                else: 
                    seats[ticket_type_list[i]] = {
                        # 'price': each_ticket_id.price, 
                        # 'classes': ticket_type_list[i]+'-class', 
                        # 'category': each_ticket_id.name}
                        'price': each_ticket_id.price, 
                        'classes': ticket_type_list[i]+'-class', 
                        'category': each_ticket_id.dm_loaighe_id.id} # loai ghe id
                legend_items.append(
                    [ticket_type_list[i], 'available', each_ticket_id.dm_loaighe_id.name])
                    # [ticket_type_list[i], 'available', each_ticket_id.name])
                for row in each_ticket_id.seat_arrangement_ids.sorted(lambda m: m.row):

                    seat_arrangement = ''
                    j = 1
                    for col in range(max_cols):
                        if row.seat_selection_ids and row.seat_selection_ids.filtered(lambda y: y.name == str(j)):
                            seat_arrangement += ticket_type_list[i]
                        else:
                            seat_arrangement += '_'
                        j += 1
                    data.append(seat_arrangement)
                i += 1

        
        # legend_items.append(['s', 'ghedoi', 'Ghế đôi'])
        legend_items.append(['g', 'datvetruoc', 'Đặt trước'])
        legend_items.append(['f', 'unavailable', 'Đã bán '])
        
        # donbanve_line_obj = request.env['dm.donbanve.line'].sudo().search([('dm_lichchieu_id','=',int(event_id))])
        booked_seat_list = []
        datvetruoc_list = []
        if lichchieu_obj and lichchieu_obj.dm_donbanve_line_ids:
            for booked_seat in lichchieu_obj.dm_donbanve_line_ids:
                if booked_seat.state == 'done' :
                    booked_seat_list.append(booked_seat.vitrighe)
                if booked_seat.state == 'draft' :
                    datvetruoc_list.append(booked_seat.vitrighe)

        banggia = []
        for bg in banggia_obj.dm_banggia_line_ids:
            banggia.append({
                'name': bg.name,
                'dm_loaighe_name': bg.dm_loaighe_id.name,
                'dm_loaive_name': bg.dm_loaive_id.name,
                'dm_loaighe_id': bg.dm_loaighe_id.id,
                'dm_loaive_id': bg.dm_loaive_id.id,
                'dongia': bg.dongia,
                
            })

        # if phong_obj.hangngang > 0:
        #     columns_map = [i+1 for i in range(phong_obj.hangngang)]
        # else:
        #     columns_map = [i*(-1) for i in range(phong_obj.hangngang, 0)]
        columns_map = phong_obj.columns.strip().split(',')
        rows_map = phong_obj.rows.strip().split(',')

        bigData = {
            'data': data,
            'seats': seats,
            'legend_items': legend_items,
            'booked_seat': booked_seat_list,
            'max_col_count': max_col_count,
            'banggia': banggia,
            'datvetruoc_list': datvetruoc_list,
            'columns_map': columns_map,
            'rows_map': rows_map
        }

        return json.dumps(bigData)
    # end def lichchieu_get_json_data

    
    @http.route(['''/phong/<int:phong_id>/sodoghe'''], type='http', auth="public", website=True)
    def dm_sodoghe(self, **kwargs):
        event_obj = request.env['dm.phong']
        if kwargs.get('phong_id', False):
            phong_id = kwargs.get('phong_id')
            event = event_obj.sudo().browse(phong_id)

        return request.render("tht_cinema.dm_website_sodoghe_template", {'phong_id': phong_id, 'event': event})
    
    @http.route(['''/phim/'''], type='http', auth="public", website=True)
    def dm_phim(self, **kwargs):
        event_obj = request.env['dm.phim']
        if kwargs.get('phong_id', False):
            phong_id = kwargs.get('phong_id')
            event = event_obj.sudo().browse(phong_id)
        event = event_obj.sudo().search([])
        phong_id = 1
        return request.render("tht_cinema.dm_website_phim_template", { 'phong_id': phong_id, 'event': event})
    
    @http.route([
        # '/template_ticket_faq_view_all',
        #  '/ticket/category/<model("ticket.faq.category"):category>',
        #  '/ticket/category/',
         '/phim/filter',
        #  '/template_ticket_faq_view_all/page/<int:page>',
        # ], type='http', auth="user",  website=True)
        ], type='http', auth="public",  website=True)
    def phim_view_all(self,page=1, category=None,**post):
        domain = []
        if post.get('search', False):
            search = str(post['search'])
            domain += [
                # '|', '|','|','|',
                ('name', 'ilike', search),
                # ('answer', 'ilike', search),
                # ('question_url', 'ilike', search),
                # ('category_id', 'ilike', search),
                # ('tag_ids', 'ilike', search)
            ]
        if category:
            domain += [('category_id', '=', category.id)]
            
        faq_ids_count = request.env['dm.phim'].sudo().search_count(domain)
        # pager
        pager = request.website.pager(
            url= "/phim",
            total= faq_ids_count,
            page= page,
            step= 10
        )
        faq_ids = request.env['dm.phim'].sudo().search(domain, limit=10,  offset=pager['offset'])
        event = faq_ids

        # categories = request.env['ticket.faq.category'].sudo().search([])
        categories = ''
        values = {
            'faq_ids': faq_ids,
            'categories': categories,
            'pager': pager
        }
        # return request.render('tht_cinema.dm_website_phim_template',values)
        return request.render("tht_cinema.dm_website_phim_template", {'values': values, 'event': event})
        # end phim filter

    @http.route(['''/lichchieu/detail/<int:lichchieu_id>/<int:banggia_id>'''], type='http', auth="public", website=True)
    def lichchieu_detail(self, **kwargs):
        event_obj = request.env['dm.lichchieu']
        if kwargs.get('lichchieu_id', False):
            lichchieu_id = kwargs.get('lichchieu_id')
            banggia_id = kwargs.get('banggia_id')
            event = event_obj.sudo().browse(lichchieu_id)

        return request.render("tht_cinema.dm_website_lichchieu_detail_template", { 'lichchieu_id': lichchieu_id, 'banggia_id': banggia_id, 'event': event})

    # end lich chieu detail

    @http.route(['''/lichchieu/detail/<int:lichchieu_id>/'''], type='http', auth="public", website=True)
    def lichchieu_detail_one(self, **kwargs):
        event_obj = request.env['dm.lichchieu']
        if kwargs.get('lichchieu_id', False):
            lichchieu_id = kwargs.get('lichchieu_id')
            # banggia_id = kwargs.get('banggia_id')
            event = event_obj.sudo().browse(lichchieu_id)

        return request.render("tht_cinema.dm_website_lichchieu_detail_template", { 'lichchieu_id': lichchieu_id, 'event': event})

    # end lich chieu detail

    @http.route(['''/lichchieu/receipt/<int:lichchieu_id>/'''], type='http', auth="public", website=True)
    def lichchieu_receipt_one(self, **kwargs):
        event_obj = request.env['dm.lichchieu']
        if kwargs.get('lichchieu_id', False):
            lichchieu_id = kwargs.get('lichchieu_id')
            event = event_obj.sudo().browse(lichchieu_id)

        return request.render("tht_cinema.dm_website_lichchieu_receipt_template", { 'lichchieu_id': lichchieu_id, 'event': event})

    # end lich chieu detail

    @http.route(['''/cinema/pos/<int:rapphim_id>/<int:lichchieu_id>/'''], type='http', auth="user", website=True)
    def cinema_pos(self, rapphim_id ='', **kwargs):
        

        dm_session = request.env['dm.session'].search([('user_id','=',request.session.uid),('state','=','opened'), ('dm_diadiem_id','=',rapphim_id)],limit=1)
        if len(dm_session) < 1 :
            return "<div> Đăng nhập trước khi bán </div>"

        dm_lichchieu = request.env['dm.lichchieu'].search([('id','=',kwargs.get('lichchieu_id')), ('dm_diadiem_id','=',dm_session.dm_diadiem_id.id)])
        if len(dm_lichchieu) < 1 :
            return "<div> Đăng nhập trước khi bán </div>"


        event_obj = request.env['dm.lichchieu']
        if kwargs.get('lichchieu_id', False):
            lichchieu_id = kwargs.get('lichchieu_id')
            event = event_obj.sudo().browse(lichchieu_id)
        
        values = {
            'session_info': json.dumps(request.env['ir.http'].session_info()),
            'lichchieu_id': lichchieu_id, 
            'event': event ,
            # 'sv_socket_io': sv_socket_io
            }

        return request.render("tht_cinema.dm_website_cinema_pos_template", values )

    # end cinema_pos detail

    @http.route(['''/lichchieu/sudung/'''], type='http', auth="public", website=True)
    def lichchieu_sudung(self, **kwargs):
        event = []
        
        event_obj = request.env['dm.lichchieu']
        diadiem_obj = request.env['dm.diadiem'].search([])
        # if kwargs.get('lichchieu_id', False):
        #     lichchieu_id = kwargs.get('lichchieu_id')
        #     # banggia_id = kwargs.get('banggia_id')
        #     event = event_obj.sudo().browse(lichchieu_id)
        # event = event_obj.search([('sudung','=', True)],limit=500)
        phim_obj = event_obj.read_group([('sudung','=', True)], fields=['id', 'dm_phim_id'],groupby=['dm_phim_id']) 
        if phim_obj:
            for rec in phim_obj:
                event.append({
                    'dm_phim': request.env['dm.phim'].browse(rec['dm_phim_id'][0]),
                    'dm_lichchieu_obj' : event_obj.search([('sudung','=', True),('dm_phim_id','=',rec['dm_phim_id'][1] )],limit=500),
                })
        
        return request.render("tht_cinema.dm_website_lichchieu_sudung_template", { 'event': event, 'diadiem_obj': diadiem_obj})

    # end lich chieu sudung all

    @http.route(['''/cinema/datvetruoc/<int:lichchieu_id>/'''], type='http', auth="public", website=True)
    def cinema_datvetruoc(self, **kwargs):
        event_obj = request.env['dm.lichchieu']
        if kwargs.get('lichchieu_id', False):
            lichchieu_id = kwargs.get('lichchieu_id')
            event = event_obj.sudo().browse(lichchieu_id)

        return request.render("tht_cinema.cinema_datvetruoc", { 'lichchieu_id': lichchieu_id, 'event': event})

    # end cinema dat ve truoc - lich chieu

    def _donbanve_create_datvetruoc_from_registration_post(self, event, registration_data, makhachhang):
        donbanve_line_ids = []
        total_dongia = []
        for rec_arr in registration_data:
            for rec in rec_arr['seat_list']:
                giave = self._dongiave(event.dm_banggia_id, rec_arr['name'], rec[1])
                total_dongia.append(float(rec[1]))
                rec_one = {
                    'loaighe': int(rec_arr['name']),
                    'dm_lichchieu_id': event.id,
                    'name': rec[0],
                    'vitrighe': rec[0],
                    'dongia': rec[1],
                    'dm_lichchieu_id': event.id,
                    'soluong': 1,
                    'price_total': rec[1],
                    'loaive': rec[2],
                    'dm_session_line_id': donbanve_info['dm_session_line_id'],
                }
                donbanve_line_ids.append((0,0, rec_one))

        #     registrations_to_create.append(registration_values)

        donbanve_state = 'done'
        donbanve_source = 'posbanve'
        print_status = True
        if donbanve_info['datvetruoc'] == 'True':
            donbanve_state = 'draft'
            donbanve_source = 'posdatvetruoc'
            print_status = False
        
        registrations_to_create = {
            'dm_lichchieu_id' : event.id,
            'user_id': request.session.uid,
            # 'dm_diadiem_id': event.dm_diadiem_id.id,
            'marap': event.dm_diadiem_id.marap,
            'dm_phim_id' : event.dm_phim_id.id,
            'dm_phong_id' : event.dm_phong_id.id,
            'dm_banggia_id' : event.dm_banggia_id.id,
            'dm_donbanve_line_ids': donbanve_line_ids,
            'amount_total': sum(total_dongia),
            'state': donbanve_state,
            'source': donbanve_source,
            'print_status': print_status,
            'makhachhang': donbanve_info['makhachhang'],
            'sodienthoai': donbanve_info['sodienthoai'],
            'payment_method': donbanve_info['payment_method'],

            # 'ptthanhtoan_id' : post.get('ptthanhtoan_id', '') ,
            'ht_thanhtoan': 'cash', 
            
            'dm_session_line_id': donbanve_info['dm_session_line_id'],
        }
        try: 
            create_dbv = request.env['dm.donbanve'].sudo().create(registrations_to_create)
            return [create_dbv,create_dbv.name]
        except:
            return False
    # end def tao ve dat truoc

    @http.route(['/donbanve/<model("dm.lichchieu"):event>/datvetruoc/seat'], type='json', auth="public", methods=['POST'], website=True)
    def datvetruoc_seat(self, event, **post):
        # o11 khong co
        # if not event.can_access_from_current_website():
        #     raise werkzeug.exceptions.NotFound()
        
        tickets = self._process_tickets_form(event, post)

        makhachhang = post.get('makhachhang', '')
        
        availability_check = True
        
        if not tickets:
            return False

        donbanve_sudo = self._donbanve_create_datvetruoc_from_registration_post( event, tickets , makhachhang)
        vn_timezone = pytz.timezone('Asia/Ho_Chi_Minh')
        # return True
        if donbanve_sudo :
            madonbanve = donbanve_sudo[1]
            return request.env['ir.ui.view'].render_template("tht_cinema.dm_website_cinema_booking_result", 
            {'tickets': tickets, 'event': event, 'availability_check': availability_check, 'vn_timezone': vn_timezone, 'madonbanve': madonbanve  })
        else:
            return False
    # end def tao ve dat truoc


    @http.route(['''/cinema/datvetruoc/today/'''], type='http', auth="user", website=True)
    def cinema_datvetruoc_today(self, redirect='/cinema/datvetruoc/today', **kw):
        # if not request.session.uid:
        #     return werkzeug.utils.redirect('/web/login', 303)
        # if kw.get('redirect'):
        #     return werkzeug.utils.redirect(kw.get('redirect'), 303)
        values = {}
        return request.render("tht_cinema.cinema_datvetruoc_today", values)

    # end cinema dat ve truoc today


    # @http.route(['''/cinema/lichchieu/<string:today>/'''], type='http', auth="user", website=True)
    # def cinema_lichchieu_today(self, redirect='/cinema/lichchieu/', **kw):
    #     values = {}
    #     return request.render("tht_cinema.cinema_lichchieu_today", values)

    # end cinema dat ve truoc today

    @http.route(['''/cinema/lichchieu/<int:marap_id>/'''], type='http', auth="user", website=True)
    def cinema_lichchieu_marap(self, marap_id=1, **kwargs):
        dm_session = request.env['dm.session'].search([('user_id','=',request.session.uid),('state','=','opened')])
        if len(dm_session) < 1 :
            return "<div> Đăng nhập trước khi bán </div>"
        event = []
        date_list = []
        dm_diadiem_obj = request.env['dm.diadiem'].browse(int(marap_id))
        lichchieu_obj = request.env['dm.lichchieu']
        # today = datetime.datetime.now().strftime('%Y-%m-%d')
        today = datetime.date.today()
        for i in range(0,9): 
            date_list.append(today + relativedelta(days=i))

        
        if kwargs.get('ngaychieu', '') !='':
            ngaychieu = kwargs.get('ngaychieu')
        else: 
            ngaychieu = today
        list_phim_obj = lichchieu_obj.read_group([('dm_diadiem_id', '=', marap_id),('ngaychieu','=', ngaychieu),('sudung','=', True)], fields=['id', 'dm_phim_id'],groupby=['dm_phim_id']) 
        if list_phim_obj:
            for rec in list_phim_obj:
                event.append({
                    'dm_phim': request.env['dm.phim'].browse(rec['dm_phim_id'][0]),
                    'dm_lichchieu_obj' : lichchieu_obj.search([('ngaychieu','=', ngaychieu),('sudung','=', True),('dm_phim_id','=',rec['dm_phim_id'][1] )],limit=500),
                })
        
        values = {
            'dm_diadiem_obj': dm_diadiem_obj, 
            'date_list': date_list, 
            'event': event,
            'list_phim_obj': list_phim_obj
            }

        return request.render("tht_cinema.dm_website_cinema_diembanve", values)

    # end lich chieu sudung all

    # lich chieu theo pos id
    @http.route(['''/cinema/pos_id/<int:pos_id>/'''], type='http', auth="user", website=True)
    def cinema_pos_id(self, pos_id='', **kwargs):
        dm_session = request.env['dm.session'].search([('id','=',pos_id),('user_id','=',request.session.uid),('state','=','opened')])
        # dm_session = request.env['dm.session'].browse(pos_id)
        if len(dm_session) < 1 :
            return "<div> Đăng nhập trước khi bán </div>"
        event = []
        date_list = []
        dm_diadiem_obj = request.env['dm.diadiem'].browse(dm_session.dm_diadiem_id.id)
        lichchieu_obj = request.env['dm.lichchieu']
        # today = datetime.datetime.now().strftime('%Y-%m-%d')
        today = datetime.date.today()
        for i in range(0,9): 
            date_list.append(today + relativedelta(days=i))

        
        if kwargs.get('ngaychieu', '') !='':
            ngaychieu = kwargs.get('ngaychieu')
        else: 
            ngaychieu = today
        list_phim_obj = lichchieu_obj.read_group([('dm_diadiem_id', '=', dm_diadiem_obj.id),('ngaychieu','=', ngaychieu),('sudung','=', True)], fields=['id', 'dm_phim_id'],groupby=['dm_phim_id']) 
        if list_phim_obj:
            for rec in list_phim_obj:
                event.append({
                    'dm_phim': request.env['dm.phim'].browse(rec['dm_phim_id'][0]),
                    'dm_lichchieu_obj' : lichchieu_obj.search([('ngaychieu','=', ngaychieu),('sudung','=', True),('dm_phim_id','=',rec['dm_phim_id'][1] )],order='batdau',limit=500),
                })
        
        values = {
            'ngaychieu' : ngaychieu,
            'dm_session': dm_session,
            'current_session_line_id': dm_session.current_session_line_id,
            'pos_id': pos_id,
            'pos_line_id': dm_session.current_session_line_id.id,
            'dm_diadiem_obj': dm_diadiem_obj, 
            'date_list': date_list, 
            'event': event,
            'list_phim_obj': list_phim_obj
            }

        return request.render("tht_cinema.dm_website_cinema_diembanve", values)

    # end cinema/pos_id/

    # pos bán vé
    # /cinema/pos_line/58/2294/
    @http.route(['''/cinema/pos_line/<int:pos_line_id>/<int:lichchieu_id>/'''], type='http', auth="user", website=True)
    def cinema_pos_line_id(self, pos_line_id ='', lichchieu_id ='', **kwargs):
        sv_socket_io = tools.config.get('sv_socket_io')
        
        dm_session = request.env['dm.session'].search([('user_id','=',request.session.uid),('state','=','opened'), ('current_session_line_id','=',pos_line_id)],limit=1)
        if len(dm_session) < 1 :
            return "<div> Đăng nhập trước khi bán </div>"

        event = request.env['dm.lichchieu'].search([('id','=',lichchieu_id), ('dm_diadiem_id','=',dm_session.dm_diadiem_id.id)])
        if len(event) < 1 :
            return "<div> Đăng nhập trước khi bán </div>"

        ptthanhtoan = request.env['dm.ptthanhtoan'].sudo().search([('source','=','posbanve'), ('status','=','true')])
        
        values = {
            'ptthanhtoan': ptthanhtoan,
            'session_info': json.dumps(request.env['ir.http'].session_info()),
            'dm_session': dm_session,
            'lichchieu_id': lichchieu_id, 
            'event': event,
            'dm_lichchieu': event,
            'pos_session_line_id': pos_line_id,
            'sv_socket_io': sv_socket_io
            
        }

        return request.render("tht_cinema.dm_website_cinema_pos_template", values)

    # end cinema_pos_line_id / lich chieu _id

    # lich chieu theo pos id
    @http.route(['''/cinema/pos_id_datvetruoc/<int:pos_id>/'''], type='http', auth="user", website=True)
    def cinema_pos_id_datvetruoc(self, pos_id='', **kwargs):
        dm_session = request.env['dm.session'].search([('id','=',pos_id),('user_id','=',request.session.uid),('state','=','opened')])
        # dm_session = request.env['dm.session'].browse(pos_id)
        if len(dm_session) < 1 :
            return "<div> Đăng nhập trước khi bán </div>"
        event = []
        date_list = []
        dm_diadiem_obj = request.env['dm.diadiem'].browse(dm_session.dm_diadiem_id.id)
        lichchieu_obj = request.env['dm.lichchieu']
        # today = datetime.datetime.now().strftime('%Y-%m-%d')
        today = datetime.date.today()
        for i in range(0,9): 
            date_list.append(today + relativedelta(days=i))

        
        if kwargs.get('ngaychieu', '') !='':
            ngaychieu = kwargs.get('ngaychieu')
        else: 
            ngaychieu = today
        list_phim_obj = lichchieu_obj.read_group([('dm_diadiem_id', '=', dm_diadiem_obj.id),('ngaychieu','=', ngaychieu),('sudung','=', True)], fields=['id', 'dm_phim_id'],groupby=['dm_phim_id']) 
        if list_phim_obj:
            for rec in list_phim_obj:
                event.append({
                    'dm_phim': request.env['dm.phim'].browse(rec['dm_phim_id'][0]),
                    'dm_lichchieu_obj' : lichchieu_obj.search([('ngaychieu','=', ngaychieu),('sudung','=', True),('dm_phim_id','=',rec['dm_phim_id'][1] )],order='batdau', limit=500),
                })
        
        values = {
            'ngaychieu' : ngaychieu,
            'dm_session': dm_session,
            'current_session_line_id': dm_session.current_session_line_id,
            'dm_diadiem_obj': dm_diadiem_obj, 
            'date_list': date_list, 
            'event': event,
            'list_phim_obj': list_phim_obj,
            }

        return request.render("tht_cinema.dm_website_cinema_datvetruoc", values)

    # end cinema/pos_id_datvetruoc/

    @http.route(['''/cinema/pos_line_datvetruoc/<int:pos_line_id>/<int:lichchieu_id>/'''], type='http', auth="user", website=True)
    def cinema_pos_line_id_datvetruoc(self, pos_line_id ='', lichchieu_id ='', **kwargs):
        sv_socket_io = tools.config.get('sv_socket_io')
        dm_session = request.env['dm.session'].search([('user_id','=',request.session.uid),('state','=','opened'), ('current_session_line_id','=',pos_line_id)],limit=1)
        if len(dm_session) < 1 :
            return "<div> Đăng nhập trước khi bán </div>"

        event = request.env['dm.lichchieu'].search([('id','=',lichchieu_id), ('dm_diadiem_id','=',dm_session.dm_diadiem_id.id)])
        if len(event) < 1 :
            return "<div> Đăng nhập trước khi bán </div>"

        values = {
            'session_info': json.dumps(request.env['ir.http'].session_info()),
            'dm_session': dm_session,
            'lichchieu_id': lichchieu_id, 
            'event': event,
            'dm_lichchieu': event,
            'pos_session_line_id': pos_line_id,
            'sv_socket_io': sv_socket_io
        }


        return request.render("tht_cinema.dm_website_cinema_pos_datvetruoc_template", values)
    # end pos_line_datvetruoc

    @http.route(['/cinema/datvetruoc_order/<int:pos_id>/'], type='http', auth="user", website=True)
    def cinema_datvetruoc_order(self, pos_id='', **kw):
        dm_session = request.env['dm.session'].search([('id','=',pos_id),('user_id','=',request.session.uid),('state','=','opened')])
        # dm_session = request.env['dm.session'].browse(pos_id)
        if len(dm_session) < 1 :
            return "<div> Đăng nhập trước khi bán </div>"
        
        DonbanveOrder = request.env['dm.donbanve']
        domain = [
            ('state', '=', 'draft')
        ]

        if kw.get('madonhang', '') !='' :
            domain.append(('name','like',kw.get('madonhang')))
        
        if kw.get('sodienthoai', '') !='' :
            domain.append(('sodienthoai','like',kw.get('sodienthoai')))

        searchbar_sortings = {
            'date': {'label': _('Order Date'), 'order': 'date_order desc'},
            'name': {'label': _('Reference'), 'order': 'name'},
            'stage': {'label': _('Stage'), 'order': 'state'},
        }

        # default sortby order
        # if not sortby:
        #     sortby = 'date'
        # sort_order = searchbar_sortings[sortby]['order']

        # if date_begin and date_end:
        #     domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        
        # content according to pager and archive selected
        orders = DonbanveOrder.search(domain, order='name DESC', limit=1000, offset=0)
        values = {}
        values.update({
            'dm_session': dm_session,
            'orders': orders.sudo(),
        })
        return request.render("tht_cinema.donbanve_order", values)
        # end list datvetruoc
    
    # thanh toán vé đặt trước 2023/01/03
    @http.route(['/cinema/datvetruoc_line/<int:pos_id>/<int:order>'], type='http', auth="user", website=True)
    def cinema_datvetruoc_line(self, pos_id='', order=None, access_token=None, **kw):
        dm_session = request.env['dm.session'].search([('id','=',pos_id),('user_id','=',request.session.uid),('state','=','opened')])
        # dm_session = request.env['dm.session'].browse(pos_id)
        if len(dm_session) < 1 :
            return "<div> Đăng nhập trước khi bán </div>"

        try:
            order_sudo = self._order_check_access(order, access_token=access_token)
        except AccessError:
            return request.redirect('/cinema/datvetruoc_order')

        values = self._order_get_page_view_values(order_sudo, access_token, **kw)

        ptthanhtoan = request.env['dm.ptthanhtoan'].sudo().search([('source','=','posbanve'), ('status','=','true')])

        values.update({
            'ptthanhtoan': ptthanhtoan,
            'dm_session': dm_session,
        })
        return request.render("tht_cinema.donbanve_order_line", values)
    # end dondattruoc detail

    @http.route(['/cinema/datvetruoc_inve/<int:pos_id>/<int:order>/'], type='http', auth="user", website=True)
    def cinema_datvetruoc_inve(self, pos_id='', order=None, access_token=None, **kw):
        dm_session = request.env['dm.session'].search([('id','=',pos_id),('user_id','=',request.session.uid),('state','=','opened')])
        # dm_session = request.env['dm.session'].browse(pos_id)
        if len(dm_session) < 1 :
            return "<div> Đăng nhập trước khi bán </div>"

        try:
            order_sudo = self._order_check_access(order, access_token=access_token)
        except AccessError:
            return request.redirect('/cinema/datvetruoc_order')

        
        values = self._order_get_page_view_values(order_sudo, access_token, **kw)

        ptthanhtoan_id = kw.get('ptthanhtoan_id', '')
        if ptthanhtoan_id !="":
            ptthanhtoan = request.env['dm.ptthanhtoan'].sudo().browse(int(kw.get('ptthanhtoan_id', '')))
        
        # order_sudo.write({'state': 'done', 'payment_method': payment_method, 
        order_sudo.write(
            {'state': 'done', 
            'dm_ptthanhtoan_id': ptthanhtoan.id, 
            'ht_thanhtoan': ptthanhtoan.ht_thanhtoan, 
            'user_id': request.session.uid ,
            'dm_session_line_id': dm_session.current_session_line_id.id ,
            'date_hoadon': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            })
        
        dbv_line_obj = request.env['dm.donbanve.line'].search([('dm_donbanve_id','=',order)])
        dbv_line_obj.sudo().write({'dm_session_line_id': dm_session.current_session_line_id.id })
        order_sudo.donbanve_invoice_create()
        
        return request.render("tht_cinema.dm_website_cinema_datvetruoc_inve", 
            {'tickets': values['order'], 'dm_session': dm_session, 'availability_check': 1 })
    # end dondattruoc in ve


    @http.route('/cinema/customer_display/<int:pos_id>/', type='http', auth='user')
    def cinema_customer_display_pos_id(self, pos_id, **k):
        dm_session = request.env['dm.session'].search([('id','=',pos_id),('user_id','=',request.session.uid),('state','=','opened')])
        # dm_session = request.env['dm.session'].browse(pos_id)
        if len(dm_session) < 1 :
            return "<div> Đăng nhập trước khi bán </div>"

        config_id = False
        pos_sessions = request.env['dm.session'].search([
            ('state', '=', 'opened'),
            ('user_id', '=', request.session.uid),
            ('id', '=', pos_id)],limit=1)
        if pos_sessions:
            dm_session_line_id = pos_sessions.current_session_line_id.id
        context = {
            'dm_session': dm_session,
            'session_info': json.dumps(request.env['ir.http'].session_info()),
            'dm_session_line_id': dm_session_line_id,
        }
        return request.render('tht_cinema.customer_display_pos_id', qcontext=context)

    
    @http.route('/cinema/pos_index/<int:pos_id>/', type='http', auth='user')
    def cinema_customer_pos_index(self, pos_id, **k):
        dm_session = request.env['dm.session'].search([('id','=',pos_id),('user_id','=',request.session.uid),('state','=','opened')])
        # dm_session = request.env['dm.session'].browse(pos_id)
        if len(dm_session) < 1 :
            return "<div> Đăng nhập trước khi bán </div>"

        config_id = False
        pos_sessions = request.env['dm.session'].search([
            ('state', '=', 'opened'),
            ('user_id', '=', request.session.uid),
            ('id', '=', pos_id)],limit=1)
        if pos_sessions:
            dm_session_line_id = pos_sessions.current_session_line_id.id
        context = {
            'dm_session': dm_session,
            'session_info': json.dumps(request.env['ir.http'].session_info()),
            'dm_session_line_id': dm_session_line_id,
        }
        return request.render('tht_cinema.pos_index', qcontext=context)
    # end def

    @http.route('/cinema/rpc/datvetruoc_line/delete', type='json', auth='user')
    def cinema_rpc_datvetruoc_line_delete(self, **k):
        if k.get('id', '') :
            dm_donbanve_line = request.env['dm.donbanve.line'].sudo().browse(k.get('id'))
            dm_donbanve = request.env['dm.donbanve'].sudo().browse(dm_donbanve_line.dm_donbanve_id.id)._amount_all()
        return dm_donbanve_line.unlink()
    
    @http.route('/cinema/rpc/datvetruoc/delete', type='json', auth='user')
    def cinema_rpc_datvetruoc_delete(self, **k):
        if k.get('id', '') :
            dm_donbanve = request.env['dm.donbanve'].sudo().browse(k.get('id'))
        return dm_donbanve.unlink()
    
    @http.route('/cinema/rpc/datvetruoc/delete_draft', type='json', auth='user')
    def cinema_rpc_datvetruoc_delete_draft(self, **k):
        # self.env['res.users'].has_group('product_extended_ecom_ept.group_product_modify')
        cinema_manager = request.env['res.groups'].sudo().search([('name','=','Cinema Manager')])
        is_cinema_manager = request.env.user.id in cinema_manager.users.ids
        if is_cinema_manager:
            if k.get('id', '') :
                domain = [('dm_lichchieu_id','=',k.get('id')), ('state','=','draft')]
                dm_donbanve = request.env['dm.donbanve'].sudo().search(domain)
            return dm_donbanve.unlink()
        else:
            return False

    
    @http.route(['''/cinema/dangchieu/index/<int:limit>/<int:page>/<int:load_delay>/'''], type='http', auth="public", website=True)
    def cinema_dangchieu_index(self, limit=4, page=1, load_delay=15, **kw):
                
        values = {
            'limit': limit,
            'page': page,
            'load_delay' : int(load_delay) * 1000
            }

        return request.render("tht_cinema.dm_website_cinema_dangchieu_index", values)


    @http.route(['''/cinema/dangchieu/'''], type='http', auth="public", website=True)
    def cinema_dangchieu(self, **kw):
        limit = int(kw.get('limit', 4))
        page = int(kw.get('page', 1))
        offset = (page - 1) * limit
        page_next_load = int(kw.get('page_next_load', 1))
        
        event = []
        date_list = []
        dm_diadiem_obj = request.env['dm.diadiem'].sudo().search([],limit=1)
        lichchieu_obj = request.env['dm.lichchieu'].sudo()
        # today = datetime.datetime.now().strftime('%Y-%m-%d')
        today = datetime.date.today()
        for i in range(0,9): 
            date_list.append(today + relativedelta(days=i))

        
        if kw.get('ngaychieu', '') !='':
            ngaychieu = kw.get('ngaychieu')
            list_phim_obj = lichchieu_obj.read_group([('dm_diadiem_id', '=', dm_diadiem_obj.id),('ngaychieu','=', ngaychieu),('sudung','=', True)], fields=['id', 'dm_phim_id'],groupby=['dm_phim_id'],limit=limit, offset=offset) 
        else: 
            ngaychieu = today
            # ngaychieu = "2021-03-08"
            total_rows = lichchieu_obj.read_group([('dm_diadiem_id', '=', dm_diadiem_obj.id),('ngaychieu','=', ngaychieu),('sudung','=', True)], fields=['id', 'dm_phim_id'],groupby=['dm_phim_id'])
            page_count = int(math.ceil(float(len(total_rows)) / limit))
            if page_next_load > page_count :
                page = 1
                offset = (page - 1) * limit
            else :
                offset = (page - 1) * limit 

            list_phim_obj = lichchieu_obj.read_group([('dm_diadiem_id', '=', dm_diadiem_obj.id),('ngaychieu','=', ngaychieu),('sudung','=', True)], fields=['id', 'dm_phim_id'],groupby=['dm_phim_id'],limit=limit, offset=offset) 
        
        if list_phim_obj:
            for rec in list_phim_obj:
                event.append({
                    'dm_phim': request.env['dm.phim'].sudo().browse(rec['dm_phim_id'][0]),
                    'dm_lichchieu_obj' : lichchieu_obj.search([('ngaychieu','=', ngaychieu),('sudung','=', True),('dm_phim_id','=',rec['dm_phim_id'][1] )],order='batdau',limit=50),
                })
        
        values = {
            'limit':   limit,
            'page': page,
            'page_count': page_count,
            'ngaychieu' : ngaychieu,
            # 'dm_session': dm_session,
            # 'current_session_line_id': dm_session.current_session_line_id,
            'dm_diadiem_obj': dm_diadiem_obj, 
            'date_list': date_list, 
            'event': event,
            'list_phim_obj': list_phim_obj
            }

        return request.render("tht_cinema.dm_website_cinema_dangchieu", values)

    # end cinema/dangchieu/

    @http.route(['''/cinema/dangchieu/<int:lichchieu_id>'''], type='http', auth="public", website=True)
    def cinema_dangchieu_lichchieu_id(self, lichchieu_id='', **kwargs):
        dm_diadiem_obj = request.env['dm.diadiem'].search([],limit=1)
        event = request.env['dm.lichchieu'].sudo().browse(lichchieu_id)
        donbanve_line_ids = request.env['dm.donbanve.line'].sudo().search([('dm_lichchieu_id','=',lichchieu_id)])
        if len(event) < 1 :
            return "<div> Đăng nhập trước khi bán </div>"

        values = {
            'lichchieu_id': lichchieu_id, 
            'event': event,
            'dm_lichchieu': event,
            'dm_diadiem_obj': dm_diadiem_obj,
            'donbanve_line_ids': donbanve_line_ids, 
            'sovedaban' : len(donbanve_line_ids) , 
            'soveconlai' : event.dm_phong_id.tongsoghe - len(donbanve_line_ids), 
            # 'soveconlai' : 0, 
        }

        return request.render("tht_cinema.dm_website_cinema_dangchieu_lichieu_id", values)

    # end cinema/dangchieu/lichieu_id

    @http.route(['''/cinema/pos_line/huyve/<int:pos_line_id>/<int:lichchieu_id>/'''], type='http', auth="user", website=True)
    def cinema_pos_line_id_huyve(self, pos_line_id ='', lichchieu_id ='', **kwargs):
        dm_session = request.env['dm.session'].search([('user_id','=',request.session.uid),('state','=','opened'), ('current_session_line_id','=',pos_line_id)],limit=1)
        if len(dm_session) < 1 :
            return "<div> Đăng nhập trước khi bán </div>"

        event = request.env['dm.lichchieu'].search([('id','=',lichchieu_id), ('dm_diadiem_id','=',dm_session.dm_diadiem_id.id)])
        if len(event) < 1 :
            return "<div> Đăng nhập trước khi bán </div>"

        values = {
            'dm_session': dm_session,
            'lichchieu_id': lichchieu_id, 
            'event': event,
            'dm_lichchieu': event,
            'pos_session_line_id': pos_line_id
        }

        return request.render("tht_cinema.dm_website_huyve", values)

    # end cinema_pos_line_id_huyve


    
class CinemaCustomerDisplayController(BusController):
    def _poll(self, dbname, channels, last, options):
        """Add the relevant channels to the BusController polling."""
        if options.get('cinemacustomer.display'):
            channels = list(channels)
            ticket_channel = (
                request.db,
                'cinemacustomer.display',
                options.get('cinemacustomer.display')
            )
            channels.append(ticket_channel)
        return super(CinemaCustomerDisplayController, self)._poll(dbname, channels, last, options)
    


    

    

