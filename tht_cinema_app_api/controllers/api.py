# -*- coding: utf-8 -*-

import json
import base64
import werkzeug
import jwt

from odoo import fields, http
import requests
import pytz
import json
import datetime
from dateutil.relativedelta import relativedelta
from datetime import timedelta
from odoo.http import content_disposition, dispatch_rpc, request, \
    serialize_exception as _serialize_exception, Response
import requests
from urllib.parse import unquote
from odoo.tools.image import image_data_uri, base64_to_image

databases = http.db_list()
db = False
if databases:
    db = databases[0]

def convert_utc_native_dt_to_gmt7(utc_datetime_inputs):
    local = pytz.timezone('Etc/GMT-7')
    utc_tz =pytz.utc
    gio_bat_dau_utc_native = utc_datetime_inputs
    gio_bat_dau_utc = utc_tz.localize(gio_bat_dau_utc_native, is_dst=None)
    gio_bat_dau_vn = gio_bat_dau_utc.astimezone (local)
    return gio_bat_dau_vn
def convert_odoo_datetime_to_vn_datetime(odoo_datetime):
    utc_datetime_inputs = fields.Datetime.from_string(odoo_datetime)
    vn_time = convert_utc_native_dt_to_gmt7(utc_datetime_inputs)
    return vn_time

class ThtCinemaAppApi(http.Controller):

    @http.route('/web/api/v1/get_background_app', type='http', auth="public")
    def get_background_app(self, image_type='', model='', res_id=False):
        print(image_type)
        try:
            domain = [(image_type, '!=', False)]
            if res_id:
                domain += [('id', '=', res_id)]
            image_base64 = getattr(request.env[model].sudo().search(domain, order="id asc", limit=1), image_type)
            if image_base64:
                content = base64.b64decode(image_base64)
                headers = [('Content-Type', '{}; charset=utf-8'.format('image/png'))]
                response = request.make_response(content, headers)
                return response
            else:
                return request.not_found()
        except ValueError as e:
            pass

    @http.route('/web/api/v1/get_list_cinema', type='json', auth="none")
    def get_cinema_now_playing(self, using=False, outstanding=[False], status=['cancel']):
        try:
            domain = [('sudung', '=', using),
                      ('status', 'in', status),
                      ('noibat', 'in', outstanding)]
            list_cinema_outstanding = request.env['dm.phim'].sudo().search(domain)
            data = [{
                'id': cinema.id,
                'name': cinema.name,
                'image': '/web/api/v1/get_background_app?image_type=hinhanh&model=dm.phim&res_id=' + str(cinema.id),
                'rate': cinema.ratephim,
                'type': cinema.dm_phim_theloai_id.name,
                'old_limit': cinema.gioihantuoi,
                'content': cinema.noidung,
                'creator': cinema.nhaphathanh,
                'time': cinema.thoiluong,
                'trailer': cinema.trailer,
                'daodien': cinema.daodien,
                'dienvien': cinema.dienvien,
                'lang': cinema.ngonngu,
                'date_start': cinema.ngaykhoichieu

            } for cinema in list_cinema_outstanding]
            return {
                'status': 200,
                'result': data
            }
        except ValueError as e:
            return {
                'status': 500,
            }
    
    @http.route('/web/api/v1/get_list_cinema_home', type='json', auth="none")
    def get_list_cinema_home(self):
        a = 1
        return {
            'status': 200,
            'result': [ {
                'name': cinema.name,
                'address': cinema.diachi
            } for cinema in request.env['dm.diadiem'].sudo().search([]) ]
        }
    
    @http.route('/web/api/v1/get_list_cinema_with_date', type='json', auth="none")
    def get_list_cinema_with_date(self, phim_id, time):
        gioihanthoigian_lc = 0
        custom_styles = {}
        event = []
        date_list = []
        dm_diadiem_obj = request.env['dm.diadiem'].sudo().search([])
        lichchieu_obj = request.env['dm.lichchieu'].sudo()
        # today = datetime.datetime.now().strftime('%Y-%m-%d')
        vn_timezone = pytz.timezone('Asia/Ho_Chi_Minh')
        # today = datetime.date.today()
        today = datetime.datetime.now(vn_timezone)

        # if dm_diadiem_obj.gioihanthoigian_lc and dm_diadiem_obj.gioihanthoigian_lc != '':
        #     gioihanthoigian_lc =  dm_diadiem_obj.gioihanthoigian_lc

        # now_compute = datetime.datetime.now(vn_timezone) + timedelta(minutes=gioihanthoigian_lc)

        # now_val = now_compute.strftime("%Y-%m-%d %H:%M:%S")
        # ('batdau','>=', now_val)
        ngaychieu = str(time)
        data = {}
        for rapphim_id in dm_diadiem_obj:
            if rapphim_id.gioihanthoigian_lc and rapphim_id.gioihanthoigian_lc != '':
                gioihanthoigian_lc =  rapphim_id.gioihanthoigian_lc

            now_compute = datetime.datetime.now(vn_timezone) + timedelta(minutes=gioihanthoigian_lc)
            now_val = now_compute.strftime("%Y-%m-%d %H:%M:%S")
            domain_val = [('dm_diadiem_id', '=', rapphim_id.id), ('ngaychieu','>=', ngaychieu),
                        ('sudung','=', True),('dm_phim_id','=', phim_id), ('batdau','>=', now_val)]
            list_phim_obj = lichchieu_obj.search(domain_val,
                                                order='batdau', limit=500)
            if not list_phim_obj:
                continue
            for phim in list_phim_obj:
                ngaychieuphim = f'{str(phim.ngaychieu)[0:4]}-{str(phim.ngaychieu)[5:7]}-{str(phim.ngaychieu)[8:10]}'
                if  ngaychieuphim not in data:
                    data[ngaychieuphim] = {}
            
                if rapphim_id.name not in data[ngaychieuphim]:
                    data[ngaychieuphim][rapphim_id.name] = {
                        'diachi': rapphim_id.diachi,
                        'marap': rapphim_id.marap,
                        'danhsachphim': []
                    }

                data[ngaychieuphim][rapphim_id.name]['danhsachphim'].append({
                    'id': phim.id,
                    'batdau': str(convert_odoo_datetime_to_vn_datetime(phim.batdau)),
                    'giobatdau': str(convert_odoo_datetime_to_vn_datetime(phim.batdau).strftime('%H:%M')),
                    'ketthuc': str(convert_odoo_datetime_to_vn_datetime(phim.ketthuc).strftime('%H:%M')),
                    'ngaychieu': ngaychieuphim,
                    'phong': phim.dm_phong_id.name,
                    'phong_id': phim.dm_phong_id.id,
                    'phim': phim.dm_phim_id.name,
                    'rapphim': phim.dm_diadiem_id.name,
                    'marap': phim.dm_diadiem_id.marap,
                })

        return {
            'status': 200,
            'result': data
        }
    
    @http.route('/web/api/v1/lichchieu/seatmap', type='json', auth="public", csrf=False)
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

        return {
            'status': 200,
            'result': bigData
        }
    
    @http.route('/web/api/v1/register', type='json', auth='public', csrf=False, methods=['POST'], cors='*')
    def cnm_api_register(self, email=None, name=None, password=None, phone=None, **kw):        
        data = request.jsonrequest
        try:
            self._signup_with_values(login=email, name=name, password=password, phone=phone, email=email )
        except AttributeError:
            return {
                    'status': 500,
                    'msg': 'Đã xảy ra lỗi.'
                }
        except ValueError as e:
            if request.env["res.users"].sudo().search([("login", "=", data['email'])]):
                return {
                'status': 500,
                'msg': 'Email đã được sử dụng. Vui lòng kiểm tra lại.'
            }
            else:
                return {
                    'status': 500,
                    'msg': 'Đã xảy ra lỗi.'
                }
        except Exception as e:
            return {
                'status': 500,
                'msg': 'Đã xảy ra lỗi.'
            }
        # log the user in
        # return do_login(email, password)
        return {
            'status': 200,
            'msg': 'Đăng ký thành công.'
        }

    def _signup_with_values(self, **values):
        # request.env['res.users'].sudo().signup(values, None)
        request.env.cr.commit()     # as authenticate will use its own cursor we need to commit the current transaction
        self.signup_email(values)

    def signup_email(self, values):
        user_sudo = request.env['res.users'].sudo().search([('login', '=', values.get('login'))])
        template = request.env.ref('auth_signup.mail_template_user_signup_account_created', raise_if_not_found=False)
        if user_sudo and template:
            template.sudo().with_context(
                lang=user_sudo.lang,
                auth_login=werkzeug.url_encode({'auth_login': user_sudo.email}),
            ).send_mail(user_sudo.id, force_send=True)

    @http.route('/web/api/v1/login', type='json', auth="none", methods=['POST'], csrf=False)
    def app_api_get_token(self, email=False, password=False):
        result = {}
        # email = kw.get('email', False)
        # password = kw.get('password', False)
        data = request.jsonrequest
        
        try:
            if db and db != request.db:
                raise Exception(_("Could not select database '%s'", db))
            uid = request.session.authenticate(request.db, email, password)
            user_id = request.env['res.users'].sudo().search([('id', '=', uid)])
            tz = user_id.tz
            partner_id = user_id.partner_id

            if uid:
                # role_name = request.env['base64.imageurl'].user_role()
                # print('role_name', role_name)
                token = jwt.encode({'uid': fields.datetime.today().strftime("%Y-%m-%d %H:%M:%S")}, 'secret', algorithm='HS256', headers={'uid': uid})
                
                if token:
                    result.update({
                    'status': 200,
                    'user_mail': email, 
                    'user_name': user_id.name,
                    'user': user_id.name,
                    'user_id': uid,
                    'uid':uid, 
                    'access_token': token, 
                    'phone': partner_id.phone,
                    'msg':'Logged in Successfully'})
                    # request.env['res.user.token'].sudo().create({'user_id':uid, 'access_token':token, 'last_request':fields.datetime.today(pytz.timezone(tz)).strftime("%Y-%m-%d %H:%M:%S") if tz else fields.datetime.today(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")})
                    # request.env['rest.api.access.history'].sudo().create({'user_id':uid, 'origin':req_env['REMOTE_ADDR'], 'access_token':token, 'accessed_on':datetime.now(pytz.timezone(tz)).strftime("%Y-%m-%d %H:%M:%S") if tz else datetime.now(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")})
                else:
                    result.update({'token': 'Invalid Token'})
        except:
            result.update({
                'status': 500,
                'msg': 'The authorization credentials provided for the request are invalid.',
                })
        return result
    
    @http.route('/web/api/v1/user_delete', type='json', auth="none", methods=['POST'], csrf=False)
    def app_api_user_delete(self, debug=False, **kw):
        result = {
            'status': 200,
            'msg': 'Success'
        }
        data = request.jsonrequest.get('params')
        uid = data['user_id']
        access_token = data['access_token']
        
        try:
            if db and db != request.db:
                raise Exception(_("Could not select database '%s'", db))
            domain = [('id', '=', uid)]
            domain_token = [('user_id', '=', uid), ('access_token', '=', access_token)]
            res_users_token_obj = request.env['res.user.token'].sudo().search(domain_token, limit=1000)
            if res_users_token_obj and len(res_users_token_obj) > 0:
                res_users_obj = request.env['res.users'].sudo().search(domain, limit=1)
                res_users_obj.sudo().unlink()
                

        except:
            result.update({
                'status': '500',
                'msg': 'The authorization credentials provided for the request are invalid.',
            })
        
        return result

    @http.route('/web/api/v1/user_update', type='json', auth="none", methods=['POST'], csrf=False)
    def app_api_user_update(self, debug=False, **kw):
        result = {}
        # email = kw.get('email', False)
        # password = kw.get('password', False)
        data = request.jsonrequest.get('params')
        email = data['email']
        # password = data['password']
        uid = data['user_id']
        phone = data['phone']
        name = data['name']
        
        try:
            if db and db != request.db:
                raise Exception(_("Could not select database '%s'", db))
            
            res_users_obj = request.env['res.users'].sudo().search([('id', '=', uid)], limit=1)
            # res_partner_obj = request.env['res.partner'].sudo().search([('id', '=', res_users_obj.partner_id.id)], limit=1)
            res_partner_obj = request.env['res.partner'].sudo().browse(res_users_obj.partner_id.id)
            if phone!='' or name !='' or email !='':
                res_partner_obj.write({
                    'phone': phone,
                    'name': name,
                    'display_name': name,
                    'email': email,
                })
            result = {
                    'status': 200,
                    'result': {
                        'phone': phone,
                        'name': name,
                        'display_name': name,
                        'email': email,
                        'user_name': name
                    }
                    
                }

        except:
            result.update({
                'status': 500,
                'message': 'The authorization credentials provided for the request are invalid.',
            })
        
        return result

    @http.route('/web/api/v1/booking/', type='json', auth="public", methods=['POST'], csrf=False, cors='*')
    def cnm_api_app_booking(self, order=None, access_token=None, **kw):
        data = request.jsonrequest
        
        user_id = data['user_id']
        lc_id = data['cartRedu']['lcInfo']['lc_detail']['lc_id']
        dbv_items = data['cartRedu']['items']
        ptthanhtoan_id = data['ptthanhtoan_id']
        amount_total = data['cartRedu']['totals']

        result = ''

        if ptthanhtoan_id and ptthanhtoan_id != "":
            ptthanhtoan = request.env['dm.ptthanhtoan'].sudo().browse(ptthanhtoan_id)
            dbv_obj = self._app_process_donbanve(user_id, lc_id, dbv_items, ptthanhtoan, amount_total )
            if ptthanhtoan.ht_thanhtoan and "momo" in ptthanhtoan.ht_thanhtoan:
                result = self.paymomo(dbv_obj.id, user_id)
            if ptthanhtoan.ht_thanhtoan and "cash" in ptthanhtoan.ht_thanhtoan:
                result = self.app_datvetruoc(dbv_obj.id)
            if ptthanhtoan.ht_thanhtoan and "bank" in ptthanhtoan.ht_thanhtoan:
                result = self.app_chuyenkhoan(dbv_obj.id)
        values = {
            'deeplink': result,
            'dbv_id': dbv_obj.id,
            'dbv_name': dbv_obj.name,
        }
        
        return json.dumps(values, ensure_ascii=False)

    def _app_process_donbanve(self, user_id, lc_id, dbv_lines, ptthanhtoan, amount_total):
        dm_donbanve_line_ids = []
        event_obj = request.env['dm.lichchieu'].sudo().browse(lc_id)
        # tickets = self._process_tickets_form(event, post)
        partner_id = request.env['res.users'].sudo().browse(user_id).partner_id

        banggia_id = event_obj.dm_banggia_id.id

        for i in dbv_lines:
            dm_loaighe_id = i['dm_loaighe_id']['dm_loaighe_id']
            dm_loaive_id = i['dm_loaive_id']
            
            dbv_line = {
                'loaighe': dm_loaighe_id,
                'dm_lichchieu_id': lc_id,
                'name': i['id'],
                'vitrighe': i['id'],
                'dongia': self._dongiave(banggia_id, dm_loaighe_id, dm_loaive_id),
                'soluong': 1,
                # 'price_total': rec[1],
                'loaive': i['loaiveLabel'],

            }
            dm_donbanve_line_ids.append((0,0, dbv_line))
        donbanve_info = {
            'makhachhang' : user_id ,
            # 'makhachhang' : post.get('makhachhang', '') ,
            'sodienthoai' : partner_id.phone ,
            'payment_method' : '',
            # 'dm_session_line_id' : post.get('dm_session_line_id', '') ,
            'datvetruoc' : 'datvetruoc' ,
            'partner_id': partner_id.id,
            'user_id': user_id ,
            'source': 'app_mobile',
            'totals': '',
            'amount_total': amount_total
            # 'dbv_lines': post.get('dbv_lines')
        }
        # dm_donbanve_line_ids
        dbv_to_create = {
            'dm_lichchieu_id' : event_obj.id,
            'user_id': user_id,
            'partner_id': partner_id.id,
            # 'dm_diadiem_id': event.dm_diadiem_id.id,
            'marap': event_obj.dm_diadiem_id.marap,
            'dm_phim_id' : event_obj.dm_phim_id.id,
            'dm_phong_id' : event_obj.dm_phong_id.id,
            'dm_banggia_id' : event_obj.dm_banggia_id.id,
            'dm_donbanve_line_ids': dm_donbanve_line_ids,
            'amount_total': donbanve_info['amount_total'],
            'state': 'draft',
            'source': 'app_mobile',
            'print_status': 'f',
            'makhachhang': donbanve_info['makhachhang'],
            'sodienthoai': donbanve_info['sodienthoai'],
            # 'payment_method': donbanve_info['payment_method'],
            # 'payment_method': '',
            'dm_ptthanhtoan_id': ptthanhtoan.id,
            'ht_thanhtoan': ptthanhtoan.ht_thanhtoan, 
            
            # 'dm_session_line_id': donbanve_info['dm_session_line_id'],
            'date_order': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            # 'date_hoadon': datetime.datetime.now(vn_timezone).strftime('%d/%m/%Y %H:%M:%S'),
        }

        create_dbv = request.env['dm.donbanve'].sudo().create(dbv_to_create)
        return create_dbv

        

    
    
    


