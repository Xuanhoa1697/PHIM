# -*- coding: utf-8 -*-

import json
import base64
from werkzeug import redirect

from odoo import fields, http
from odoo.http import request
from odoo import tools
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import AccessError, UserError
from odoo.tools import html_escape

import pytz
import json
import datetime
from dateutil.relativedelta import relativedelta
from datetime import timedelta

from . import momo

def convert_utc_native_dt_to_gmt7(utc_datetime_inputs):
    local = pytz.timezone('Etc/GMT-7')
    utc_tz =pytz.utc
    gio_bat_dau_utc_native = utc_datetime_inputs#fields.Datetime.from_string(self.gio_bat_dau)
    gio_bat_dau_utc = utc_tz.localize(gio_bat_dau_utc_native, is_dst=None)
    gio_bat_dau_vn = gio_bat_dau_utc.astimezone (local)
    return gio_bat_dau_vn
def convert_odoo_datetime_to_vn_datetime(odoo_datetime):
    utc_datetime_inputs = fields.Datetime.from_string(odoo_datetime)
    vn_time = convert_utc_native_dt_to_gmt7(utc_datetime_inputs)
    return vn_time


class ThtCinemaApi(http.Controller):

    
    @http.route(['/api/momo/query'], type='json', auth='public')
    def api_momo_query(self):
        data_json = request.jsonrequest
        res = momo.momo_query('tgc_6125b962-720d-40d2-b176-4e08bdfcc9ae', 'tgc_8629b36c-8b43-470a-95ea-4359eaa2f072')
        return data_json
    @http.route(['/cnm/img_app/'], type='http', auth='public')
    def cnm_img_app(self, **kw):
        try :
            image_base64 = request.env['dm.diadiem'].sudo().search([],limit=1).img_app
            if image_base64:
                content = base64.b64decode(image_base64)
            # headers = http.set_safe_image_headers(headers, content)
            # response = request.make_response(content, headers)
                headers = [('Content-Type', '{}; charset=utf-8'.format('image/png'))]
                mimetype = 'image/png'

                # headers = http.set_safe_image_headers(headers, content)
                response = request.make_response(content, headers)
                return response
            else: 
                return ('')
        except:
            pass

    @http.route(['/cnm/phim/image/<int:id>'], type='http', auth='public')
    def cnm_phim_image(self, id):
        try :
            image_base64 = request.env['dm.phim'].sudo().browse(id).hinhanh
            if image_base64:
                content = base64.b64decode(image_base64)
            # headers = http.set_safe_image_headers(headers, content)
            # response = request.make_response(content, headers)
                headers = [('Content-Type', '{}; charset=utf-8'.format('image/png'))]
                mimetype = 'image/png'

                # headers = http.set_safe_image_headers(headers, content)
                response = request.make_response(content, headers)
                return response
            else: 
                return ('')
        except:
            pass
    
    #  api lich chieu theo phim_id - mot ngay co nhieu lich chieu
    @http.route(['''/cnm/api/serverstatus'''], type='http', auth="public", website=True)
    def cnm_api_serverstatus(self, **kwargs):
        values = {
            'status': '200'
            }
        return json.dumps(values, ensure_ascii=False)
        

    # same cnm/phim/sapchieu phim.py
    @http.route(['''/cnm/api/phimsapchieu'''], type='http', auth="public")
    def cnm_api_phimsapchieu(self, **kw):
        # today = datetime.date.today()
        today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        event = []
        values = []
        domain = [('status','=','sapchieu')]
        dm_phim_ids = request.env['dm.phim'].sudo().search(domain, limit=100)
        if dm_phim_ids :
            for r in dm_phim_ids:
                rec_obj = {
                    "id": r.id,
                    "title": r.name,
                    "original_language": "en",
                    "vote_average": 5.5,
                    "release_date": "2016-08-03",
                    "poster_path": r.id,
                    'title': r.name,
                    'thoiluong': r.thoiluong,
                    'nhaphathanh': r.nhaphathanh,
                    'namphathanh': r.namphathanh,
                    'status': r.status,
                    'gioihantuoi': r.gioihantuoi,
                    'noidung': r.noidung,
                }
                values.append(rec_obj)
            
        return json.dumps(values, ensure_ascii=False)

    # same cnm/phim/noibat phim.py
    @http.route(['''/cnm/api/phimnoibat'''], type='http', auth="public")
    def cnm_api_phimnoibat(self, **kw):
        # today = datetime.date.today()
        today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        event = []
        values = []
        domain = [('noibat','=',1),('sudung','=', 1),('status','=', 'dangchieu')]
        dm_phim_ids = request.env['dm.phim'].sudo().search(domain, limit=100)
        if dm_phim_ids :
            for r in dm_phim_ids:
                rec_obj = {
                    "id": r.id,
                    "title": r.name,
                    "original_language": "en",
                    "vote_average": 5.5,
                    "release_date": "2016-08-03",
                    "poster_path": r.id,
                    'title': r.name,
                    'thoiluong': r.thoiluong,
                    'nhaphathanh': r.nhaphathanh,
                    'namphathanh': r.namphathanh,
                    'status': r.status,
                    'gioihantuoi': r.gioihantuoi,
                    'noidung': r.noidung,
                }
                values.append(rec_obj)
            
        return json.dumps(values, ensure_ascii=False)

    @http.route(['''/cnm/api/blogpost'''], type='http', auth="public")
    def cnm_api_blogpost(self, **kw):
        # today = datetime.date.today()
        today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        event = []
        values = []
        domain = [('showinapp','=',1)]
        blog_ids = request.env['blog.post'].sudo().search(domain, limit=100, order="id desc")
        if blog_ids :
            for r in blog_ids:
                rec_obj = {
                    "id": r.id,
                    "title": r.name,                    
                    "poster_path": 'r.id',
                    'title': r.name,
                    'subtitle': r.subtitle,
                    'cover_properties': r.cover_properties,
                    'content': r.content,
                    
                }
                values.append(rec_obj)
            
        return json.dumps(values, ensure_ascii=False)

    # end api phimdangchieu list all
    # same cnm/phim/dangchieu phim.py
    @http.route(['''/cnm/api/phimdangchieu'''], type='http', auth="public")
    def cnm_api_phimdangchieu(self, **kw):
        # today = datetime.date.today()
        today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        event = []
        
        event_obj = request.env['dm.lichchieu'].sudo()
        diadiem_obj = request.env['dm.diadiem'].sudo().search([])
       
        dm_phim_obj = event_obj.read_group([('sudung','=', True), ('batdau','>=', today)], fields=['id', 'dm_phim_id'],groupby=['dm_phim_id']) 

        phim_ids = []
        if dm_phim_obj:
            for rec in dm_phim_obj:
                phim_ids.append(rec['dm_phim_id'][0])

        values = {
            'results': [],
            'info': {
                'count': len(phim_ids)
            }
        }
        
        dm_phim_ids = request.env['dm.phim'].sudo().browse(phim_ids)
        if dm_phim_ids :
            for r in dm_phim_ids:
                rec_obj = {
                    "id": r.id,
                    "title": r.name,
                    "original_language": "en",
                    "vote_average": 5.5,
                    "release_date": "2016-08-03",
                    "poster_path": r.id,
                    'title': r.name,
                    'thoiluong': r.thoiluong,
                    'nhaphathanh': r.nhaphathanh,
                    'namphathanh': r.namphathanh,
                    'status': r.status,
                    'gioihantuoi': r.gioihantuoi,
                    'noidung': r.noidung,
                }
                values['results'].append(rec_obj)
            

        return json.dumps(values, ensure_ascii=False)

    # end api phimdangchieu list all

    #  api lich chieu theo phim_id - mot ngay co nhieu lich chieu - them gioi han thoi gian dat ve truoc trên app 
    @http.route(['''/cnm/api/phimlichchieu/<int:phim_id>'''], type='http', auth="public", website=True)
    def cnm_api_phimlichchieu_phim_id(self, phim_id='', **kwargs):
        gioihanthoigian_lc = 0
        custom_styles = {}
        event = []
        date_list = []
        dm_diadiem_obj = request.env['dm.diadiem'].sudo().search([],limit=1)
        lichchieu_obj = request.env['dm.lichchieu'].sudo()
        # today = datetime.datetime.now().strftime('%Y-%m-%d')
        vn_timezone = pytz.timezone('Asia/Ho_Chi_Minh')
        # today = datetime.date.today()
        today = datetime.datetime.now(vn_timezone)
        for i in range(0,9): 
            date_list.append(str(today + relativedelta(days=i)))

        if dm_diadiem_obj.gioihanthoigian_lc and dm_diadiem_obj.gioihanthoigian_lc != '':
            gioihanthoigian_lc =  dm_diadiem_obj.gioihanthoigian_lc

        now_compute = datetime.datetime.now() + timedelta(minutes=gioihanthoigian_lc)

        now_val = now_compute.strftime("%Y-%m-%d %H:%M:%S")
        if kwargs.get('ngaychieu', '') !='':
            ngaychieu = kwargs.get('ngaychieu')
        else: 
            ngaychieu = today
        domain_val = [('dm_diadiem_id', '=', dm_diadiem_obj.id), ('ngaychieu','>=', ngaychieu),
                    ('sudung','=', True),('dm_phim_id','=', phim_id), ('batdau','>=', now_val)]
        list_phim_obj = lichchieu_obj.read_group(domain_val, fields=['id', 'dm_phim_id'],groupby=['dm_phim_id']) 
        if list_phim_obj:
            for rec in list_phim_obj:
                event.append({
                    'dm_phim': request.env['dm.phim'].sudo().browse(rec['dm_phim_id'][0]),
                    'dm_lichchieu_obj' : lichchieu_obj.search([('ngaychieu','>=', ngaychieu),('sudung','=', True),('dm_phim_id','=',rec['dm_phim_id'][1] ), ('batdau','>=', now_val)],order='batdau',limit=500),
                })
        
        lichchieu_list = []
        if event: 
            dm_lichchieu_ids = event[0]['dm_lichchieu_obj']
            for r in dm_lichchieu_ids:
                # yyyy-mm-dd
                # print(265, (r.ngaychieu))
                ngaychieu = f'{r.ngaychieu[8:10]}/{r.ngaychieu[5:7]}/{r.ngaychieu[0:4]}'
                lichchieu_list.append({
                    'id': r.id,
                    'batdau': str(convert_odoo_datetime_to_vn_datetime(r.batdau)),
                    'giobatdau': str(convert_odoo_datetime_to_vn_datetime(r.batdau).strftime('%H:%M')),
                    'ketthuc': r.ketthuc,
                    'ngaychieu': ngaychieu,
                    'phong': r.dm_phong_id.name,
                    'phim': r.dm_phim_id.name,
                    'rapphim': r.dm_diadiem_id.name,

                })

        dm_phim_obj = request.env['dm.phim'].sudo().browse(phim_id)
        values = {
            'phim': {
                'id': phim_id,
                'title': dm_phim_obj.name,
                'poster_path': phim_id,
                'thoiluong': dm_phim_obj.thoiluong,
                'nhaphathanh': dm_phim_obj.nhaphathanh,
                'namphathanh': dm_phim_obj.namphathanh,
                'status': dm_phim_obj.status,
                'gioihantuoi': dm_phim_obj.gioihantuoi,
                'noidung': dm_phim_obj.noidung,
                'trailer': dm_phim_obj.trailer,
            },
            'diadiem': {
                'id': dm_diadiem_obj.id, 
                'name': dm_diadiem_obj.name,
            },
            'lichchieu_list': lichchieu_list,
            
            'ngaychieu' : str(ngaychieu),
            'date_list': date_list, 
            
            # 'event': event,
            # 'list_phim_obj': list_phim_obj,
            }

        return json.dumps(values, ensure_ascii=False)
        # return request.render("tht_cinema_website.dangchieu_phim_id", values)

    # end ccnm_phim_dangchieu_phim_id

    # api so do ghe trong su kien
    @http.route(['''/cnm/api/lichchieu/seatmap/<int:lichchieu_id>'''], type='http', auth="public", csrf=False)
    def api_lichchieu_lichchieu_id(self, lichchieu_id):
        # event_obj = request.env['event.event'].sudo().browse(int(event_id))
        lichchieu_obj = request.env['dm.lichchieu'].sudo().browse(int(lichchieu_id))
        phong_obj = request.env['dm.phong'].sudo().browse(int(lichchieu_obj.dm_phong_id.id))
        banggia_obj = request.env['dm.banggia'].sudo().browse(int(lichchieu_obj.dm_banggia_id.id))

        # phuong thuc thanh toan
        ptthanhtoan = request.env['dm.ptthanhtoan'].sudo().search([('source','=','app_mobile')])

        ptthanhtoan_data = []
        if ptthanhtoan and len(ptthanhtoan) > 0 :
            for r in ptthanhtoan:
                ptthanhtoan_data.append(
                    {
                        'id': r.id,
                        'name': r.name
                    }
                )
        
        data = []
        seats = {}
        legend_items = []
        max_col_count = 0
        ticket_type_list = ['0', 'a', 'b', 'c', 'd', 'e',
                            'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o']
        # if event_obj and event_obj.event_ticket_ids:
        if phong_obj and phong_obj.dm_phong_line_ids:
            custom_styles = phong_obj.custom_styles
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
                        'classes': 'b'+'_class', 
                        'category': each_ticket_id.dm_loaighe_id.id, # loai ghe id
                        'dm_loaighe_id' : each_ticket_id.dm_loaighe_id.id }
                else: 
                    seats[ticket_type_list[i]] = {
                        # 'price': each_ticket_id.price, 
                        # 'classes': ticket_type_list[i]+'-class', 
                        # 'category': each_ticket_id.name}
                        'price': each_ticket_id.price, 
                        'classes': ticket_type_list[i]+'_class', 
                        'category': each_ticket_id.dm_loaighe_id.id, # loai ghe id
                        'dm_loaighe_id' : each_ticket_id.dm_loaighe_id.id }
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
        loaive = []
        loaive_distinct = []
        for bg in banggia_obj.dm_banggia_line_ids:
            banggia.append({
                'name': bg.name,
                'dm_loaighe_name': bg.dm_loaighe_id.name,
                'dm_loaive_name': bg.dm_loaive_id.name,
                'dm_loaighe_id': bg.dm_loaighe_id.id,
                'dm_loaive_id': bg.dm_loaive_id.id,
                'dongia': bg.dongia,                
            })
            if bg.dm_loaive_id.id not in loaive_distinct:
                loaive_distinct.append(bg.dm_loaive_id.id)
                loaive.append({'id': bg.dm_loaive_id.id, 
                                'name': bg.dm_loaive_id.name })


        # if phong_obj.hangngang > 0:
        #     columns_map = [i+1 for i in range(phong_obj.hangngang)]
        # else:
        #     columns_map = [i*(-1) for i in range(phong_obj.hangngang, 0)]
        columns_map = phong_obj.columns.strip().split(',')
        rows_map = phong_obj.rows.strip().split(',')
        # custom_styles = {
        #     'F1': {
        #         'paddingRight': 50
        #     },
        #     'F11': {
        #         'display': 'none'
        #     },
        #     'F12': {
        #         'display': 'none'
        #     }
        # }
        lc_detail = {
            'lc_id': lichchieu_obj.id,
            'phim_id': lichchieu_obj.dm_phim_id.id,
            'tenphim': lichchieu_obj.dm_phim_id.name,
            'ngaychieu': lichchieu_obj.ngaychieu,
            'batdau': lichchieu_obj.batdau,
            'ketthuc': lichchieu_obj.ketthuc,
        }
       
        bigData = {
            'lc_detail': lc_detail,
            'data': data,
            'seats': seats,
            'legend_items': legend_items,
            'booked_seat': booked_seat_list,
            'max_col_count': max_col_count,
            'banggia': banggia,
            'datvetruoc_list': datvetruoc_list,
            'columns_map': columns_map,
            'rows_map': rows_map,
            'custom_styles': custom_styles,
            'loaive': loaive,
            'ptthanhtoan': ptthanhtoan_data,
        }

        return json.dumps(bigData)
    # end def api lichchieu_get_json_data

    #  api lich chieu theo phim_id - mot ngay co nhieu lich chieu
    @http.route(['''/cnm/api/lichchieu/<int:lc_id>'''], type='http', auth="public", website=True)
    def cnm_api_lichchieu_id(self, phim_id='', **kwargs):
        event = []
        date_list = []
        dm_diadiem_obj = request.env['dm.diadiem'].sudo().search([],limit=1)
        lichchieu_obj = request.env['dm.lichchieu'].sudo()
        # today = datetime.datetime.now().strftime('%Y-%m-%d')
        vn_timezone = pytz.timezone('Asia/Ho_Chi_Minh')
        # today = datetime.date.today()
        today = datetime.datetime.now(vn_timezone)
        for i in range(0,9): 
            date_list.append(str(today + relativedelta(days=i)))

       
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
        
        lichchieu_list = []
        if event: 
            dm_lichchieu_ids = event[0]['dm_lichchieu_obj']
            for r in dm_lichchieu_ids:
                lichchieu_list.append({
                    'id': r.id,
                    'batdau': str(convert_odoo_datetime_to_vn_datetime(r.batdau)),
                    'giobatdau': str(convert_odoo_datetime_to_vn_datetime(r.batdau).strftime('%H:%M')),
                    'ketthuc': r.ketthuc,
                    'ngaychieu': r.ngaychieu,

                })

        dm_phim_obj = request.env['dm.phim'].sudo().browse(phim_id)
        values = {
            'phim': {
                'id': phim_id,
                'title': dm_phim_obj.name,
                'poster_path': phim_id,
            },
            'diadiem': {
                'id': dm_diadiem_obj.id, 
                'name': dm_diadiem_obj.name,
            },
            'lichchieu_list': lichchieu_list,
            
            'ngaychieu' : str(ngaychieu),
            'date_list': date_list, 
            
            # 'event': event,
            # 'list_phim_obj': list_phim_obj,
            }

        return json.dumps(values, ensure_ascii=False)
        # return request.render("tht_cinema_website.dangchieu_phim_id", values)

    # end cnm_api_lichchieu_id

    
    
    


