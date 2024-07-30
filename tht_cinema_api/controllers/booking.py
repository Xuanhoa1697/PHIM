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

from . import momo

def check_sv_socket_io(ip_addr):
    if ip_addr == '':
        print('vui lòng cài đặt ')
    return ip_addr

def strToTimeGmt7(string_date):
    res = ''
    if string_date:
        res = datetime.datetime.strptime(string_date, '%Y-%m-%d %H:%M:%S') + datetime.timedelta(hours=7)
    return res

def convert_odoo_datetime_to_vn_datetime(odoo_datetime):
    utc_datetime_inputs = fields.Datetime.from_string(odoo_datetime)
    vn_time = convert_utc_native_dt_to_gmt7(utc_datetime_inputs)
    return vn_time

class ThtCinemaAppBooking(http.Controller):

    def _order_check_access(self, order_id, access_token=None):
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

 
    # fn tạo đơn bán vé từ web, chưa in vé, chưa thanh toán
    def _donbanve_create_web_momo_from_registration_post(self, event, registration_data, donbanve_info):
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
                    'dm_session_line_id': donbanve_info['dm_session_line_id'],
                }
                donbanve_line_ids.append((0,0, rec_one))


        #     registrations_to_create.append(registration_values)

        list_seat = []
        list_seat.append({
            'name': 'seat1'
        })

        donbanve_state = 'draft'
        donbanve_source = 'app_mobile'
        print_status = False
        if donbanve_info['datvetruoc'] == 'True':
            donbanve_state = 'draft'
            donbanve_source = 'app_mobile'
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
            
            'dm_session_line_id': '',
            'date_hoadon': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
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
    # end fn

    # don gia ve
    def _dongiave(self, dm_banggia_id, dm_loaighe_id, dm_loaive_id):
        dongia_obj = request.env['dm.banggia.line'].sudo().search(
                [('dm_banggia_id', '=', dm_banggia_id), 
                    ('dm_loaighe_id', '=', int(dm_loaighe_id)),
                    ('dm_loaive_id', '=', int(dm_loaive_id)),
                ], limit=1)
        return dongia_obj.dongia
    
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
    
    def paymomo(self, order, user_id, access_token=None):
        # def cnm_web_momo_payment(self, order=None, access_token=None, **post):
        #     order= post.get('order_id') or ''
        vn_timezone = pytz.timezone('Asia/Ho_Chi_Minh')
        # today = datetime.date.today()
        today = datetime.datetime.now(vn_timezone)
        # return True
        if order:
            try:
                order_sudo = self._order_check_access(int(order), access_token=access_token)
            except AccessError:
                return request.redirect('/cinema/inlaive_order')
            
            dbh_info = {
                    'orderInfo': order_sudo.name,
                    'amount': int(order_sudo.amount_total),
                }
            momo_data = momo.CreateOrderByMomo(dbh_info, user_id)
            req_momo = json.loads(momo_data['req_momo'])
            res_momo = momo_data['res_momo']
            
            momo_obj = request.env['dm.momo'].sudo().create({
                'name': req_momo['orderInfo'] ,
                'user_id': momo_data['user_id'] ,
                'source': 'app_mobile' ,
                'amount': momo_data['amount'] ,
                'ngaygiaodich': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') ,
                'momo_orderid': req_momo['orderId'] ,
                'momo_requestid' : req_momo['requestId'],
                'req_data' : req_momo,
                'res_data' :res_momo
            })
            if res_momo.get('resultCode') == 0: 
                dbv_momo_update = order_sudo.write({
                    'momo_orderid': momo_data['orderId'] ,
                    'momo_requestid' : momo_data['requestId'], 
                    'momo_signature' : momo_data['signature'], 
                    # 'momo_sign' : result['signature'], 
                    # 'state' : 'done',
                    # 'date_hoadon': datetime.datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                })
                
                return res_momo['deeplink']
            else :
                return {}
    
    def app_datvetruoc(self, order, access_token=None):
        # def cnm_web_momo_payment(self, order=None, access_token=None, **post):
        #     order= post.get('order_id') or ''
        vn_timezone = pytz.timezone('Asia/Ho_Chi_Minh')
        # today = datetime.date.today()
        today = datetime.datetime.now(vn_timezone)
        # return True
        result = {}  
        if order:
            try:
                order_sudo = self._order_check_access(int(order), access_token=access_token)
            except AccessError:
                pass
                # return request.redirect('/cinema/inlaive_order')
            
            dbh_info = {
                    'orderInfo': order_sudo.name,
                    'amount': int(order_sudo.amount_total),
                }
              
            result['deeplink'] = "thtcinema://home/resultpayment?orderName=" + dbh_info['orderInfo']
        
        return result['deeplink']     
            
    # end def datvetruoc trên app

    # thanh toán = chuyển khoản ngân hàng
    def app_chuyenkhoan(self, order, access_token=None):
        # def cnm_web_momo_payment(self, order=None, access_token=None, **post):
        #     order= post.get('order_id') or ''
        vn_timezone = pytz.timezone('Asia/Ho_Chi_Minh')
        # today = datetime.date.today()
        today = datetime.datetime.now(vn_timezone)
        # return True
        result = {}  
        if order:
            try:
                order_sudo = self._order_check_access(int(order), access_token=access_token)
            except AccessError:
                pass
                # return request.redirect('/cinema/inlaive_order')
            
            dbh_info = {
                    'orderInfo': order_sudo.name,
                    'amount': int(order_sudo.amount_total),
                }
              
            result['deeplink'] = "thtcinema://home/dbvbank?orderName=" + dbh_info['orderInfo']
        
        return result['deeplink']     
    # end def app chuyển khoản trên app

    # tạo đơn bán vé từ app
    @http.route(['/cnm/api/booking'], type='json', auth="public", methods=['POST'], csrf=False, website=True, cors='*')
    def cnm_api_booking(self, order=None, access_token=None, **kw):
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

    # END FN
    

    # 01 tạo đơn hàng từ app
    @http.route(['/cnm/app/checkout/<int:event_id>'], type='json', auth="public", methods=['POST'], csrf=False, website=True)
    def cnm_app_checkout_lc_id(self, event_id, order=None, access_token=None, **post):
        dbvData = self._process_donbanve_form(event_id, post)

        if post.get('payment_method', '') == 'momo' :
            result = self.paymomo(dbvData.id)
            values = {
                'deeplink': result
            }
            return json.dumps(values, ensure_ascii=False)
        
        
        
        # availability_check = True
        
        # if not tickets:
        #     return False

        # donbanve_sudo = self._donbanve_create_web_momo_from_registration_post( event, tickets , donbanve_info)
        # vn_timezone = pytz.timezone('Asia/Ho_Chi_Minh')
        # # return True
        # if donbanve_sudo :
        #     madonbanve = donbanve_sudo[1]
        #     if donbanve_info['payment_method'] == 'momo':   
        #         order = donbanve_sudo[0].id
        #         try:
        #             order_sudo = self._order_check_access(order, access_token=access_token)
        #         except AccessError:
        #             return request.redirect('/cinema/inlaive_order')

        #         values = self._order_get_page_view_values(order_sudo, access_token, **post)
        #         # return request.render("tht_cinema.inlaive_order_line", values)                           
        #         # response = http.Response(template='tht_cinema_website.momo', qcontext={'tickets': tickets, 'event': event, 'availability_check': availability_check, 'vn_timezone': vn_timezone, 'madonbanve': madonbanve  })
        #         response = http.Response(template='tht_cinema_website.momo_dbv', qcontext= values)
        #         return response.render()

        #     # thanh toán tiền mặt
        #     if donbanve_info['payment_method'] == 'cash':   
        #         order = donbanve_sudo[0].id
        #         try:
        #             order_sudo = self._order_check_access(order, access_token=access_token)
        #         except AccessError:
        #             return request.redirect('/cinema/inlaive_order')

        #         values = self._order_get_page_view_values(order_sudo, access_token, **post)
        #         # return request.render("tht_cinema.inlaive_order_line", values)
                            
        #         # response = http.Response(template='tht_cinema_website.momo', qcontext={'tickets': tickets, 'event': event, 'availability_check': availability_check, 'vn_timezone': vn_timezone, 'madonbanve': madonbanve  })
        #         response = http.Response(template='tht_cinema_website.cash_dbv', qcontext= values)
        #         return response.render()
        # else:
        #     return False

    # thanh toán momo
    @http.route(['/cnm/app/momo/payment'], type='http', auth="user", methods=['POST'], csrf=False, website=True)
    def cnm_web_momo_payment(self, order=None, access_token=None, **post):
        order= post.get('order_id') or ''
        vn_timezone = pytz.timezone('Asia/Ho_Chi_Minh')
        # return True
        if order:
            try:
                order_sudo = self._order_check_access(int(order), access_token=access_token)
            except AccessError:
                return request.redirect('/cinema/inlaive_order')
            values = self._order_get_page_view_values(order_sudo, access_token, **post)
            dbh_info = {
                    'orderInfo': order_sudo.name,
                    'amount': int(order_sudo.amount_total),
                }
            result = momo.CreateOrderByMomo(dbh_info)
            
            dbv_momo_update = order_sudo.write({
                'momo_orderid': result['orderId'] ,
                'momo_requestid' : result['requestId']
            })
            return request.redirect(result['payUrl'])
        
        # return request.render("tht_cinema.inlaive_order_line", values)
                    
        # response = http.Response(template='tht_cinema_website.momo', qcontext={'tickets': tickets, 'event': event, 'availability_check': availability_check, 'vn_timezone': vn_timezone, 'madonbanve': madonbanve  })
        # response = http.Response(template='tht_cinema_website.momo_dbv', qcontext= values)
        # return response.render()    
    
    # end fn 

    # kết quả thanh toán momo trả về 
    @http.route(['/cnm/app/momo/result'], type='json', auth="public", methods=['POST'], csrf=False, website=True)
    def cnm_app_momo_result(self, order=None, access_token=None, **kw):
        #thanh toán thành công returnUrl
        data_json = request.jsonrequest
        momo_obj = request.env['dm.momo'].sudo().search([('momo_requestid','=',data_json.get('requestId'))], limit=1)
        momo_obj.write({
            'momo_resultcode': data_json.get('resultCode'),
            'momo_message': data_json.get('message'),
            'momo_transid': data_json.get('transId'),
            'result_data': dict(data_json)})
            
        if data_json and data_json.get('resultCode') == 0 :
            dbv_obj = request.env['dm.donbanve'].sudo().search([('name','=',data_json.get('orderInfo')),('momo_requestid','=',data_json.get('requestId'))], limit=1)
            dbv_obj.write({
                'momo_transid': data_json.get('transId'),
                'state': 'done', 
                'ht_thanhtoan': 'momo', 
                'date_hoadon': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                })
            # dbv_obj.donbanve_invoice_create()
            # return 0
            # return request.redirect('thtcinema://home/resultpayment?orderName=' + kw.get('orderInfo'))
            # return request.redirect('/cnm/user/dbv/' + kw.get('orderInfo'))
        else : 
            dbv_obj = request.env['dm.donbanve'].sudo().search([('name','=',data_json.get('orderInfo')),('momo_requestid','=',data_json.get('requestId'))], limit=1)
            if dbv_obj:
                dbv_obj.unlink()
            
        # return request.redirect('/cnm/phim/dangchieu')
        return data_json
        # return request.make_response(json.dumps(kw))
    
    
    @http.route(['/cnm/app/momo/notify'], type='http', auth="public", methods=['POST'], csrf=False, website=True, cors='*')
    def cnm_web_momo_notify(self, order=None, access_token=None, **kw):
        #thanh toán thành công
        if kw.get('errorCode', '') == "0" :
            pass
        else : 
            dbv_obj = request.env['dm.donbanve'].sudo().search([('name','=',kw.get('orderInfo'))], limit=1)
            if dbv_obj:               
                dbv_obj.unlink()
        return ''
    # END FN

    # api danh sach đơn bán vé của user từ app
    @http.route(['/cnm/api/user/dbv/'], type='json', auth="public", methods=['POST'], csrf=False, website=True, cors='*')
    def cnm_api_user_dbv(self, user_id=None, access_token=None, **kw):
        data = request.jsonrequest
        if data: 
            user_id = data['user_id']
            access_token = data['access_token']
        dbv = []
        if user_id != '':
            # [1,5,3,4,...]
            # dbv_obj = request.env['dm.donbanve'].sudo().search([('user_id','=',user_id)], order='id desc', limit=10)
            dbv_obj = request.env['dm.donbanve'].sudo().search([('makhachhang','=',user_id)], order='id desc', limit=1000)
            if dbv_obj: 
                for i in dbv_obj:
                    for j in i:
                        lines = []
                        for r in j.dm_donbanve_line_ids: 
                            lines.append({
                                'name': r.name,
                                'loaive': r.loaive,
                                'dongia': r.dongia,
                            })

                        if not j.dm_lichchieu_id.id:
                            continue
                        dbv_info = {
                            'id': j.id, 
                            'name': j.name,
                            'sodienthoai': j.sodienthoai,
                            'amount_total': j.amount_total,
                            'tenphim': j.dm_phim_id.name,
                            'phong': j.dm_phong_id.name,
                            # 'batdau': j.dm_lichchieu_id.batdau,
                            # 'ketthuc': j.dm_lichchieu_id.ketthuc,
                            'batdau': strToTimeGmt7(j.dm_lichchieu_id.batdau).strftime("%d/%m/%Y %H:%M:%S"),
                            'ketthuc': strToTimeGmt7(j.dm_lichchieu_id.ketthuc).strftime("%d/%m/%Y %H:%M:%S"),
                            
                            'lines': lines,
                            'rapphim': j.dm_lichchieu_id.dm_diadiem_id.name,
                            # 'thanhtoan': j.payment_method,
                            'thanhtoan': j.dm_ptthanhtoan_id.name,
                            'state': j.state,
                            'ht_thanhtoan':j.ht_thanhtoan,
                            'date_order':strToTimeGmt7(j.date_order).strftime("%d/%m/%Y %H:%M:%S") ,
                            'tt_chuyenkhoan': j.dm_ptthanhtoan_id.tt_chuyenkhoan,

                        }
                        dbv.append(dbv_info)
        else: 
            dbv = {}
        return json.dumps(dbv, ensure_ascii=False)

    # api chi tiet 1 đơn bán vé của user 
    @http.route(['/cnm/api/user/dbv/<string:order_name>'], type='json', auth="public", methods=['POST'], csrf=False, website=True, cors='*')
    def cnm_api_user_dbv_detail(self, order_name=None, access_token=None, **kw):
        dbv_info = {}
        data = request.jsonrequest
        if data: 
            order_name = data['orderName']
            user_id = data['user_id']
            access_token = data['access_token']

        if order_name != '':
            # dbv_obj = request.env['dm.donbanve'].sudo().search([('name','=',order_name), ('user_id','=',user_id)], limit=1)
            dbv_obj = request.env['dm.donbanve'].sudo().search([('name','=',order_name), ('makhachhang','=',user_id)], limit=1)
            if dbv_obj: 
                lines = []
                for r in dbv_obj.dm_donbanve_line_ids: 
                    lines.append({
                        'name': r.name,
                        'loaive': r.loaive,
                        'dongia': r.dongia,
                    })
                dbv_info = {
                    'name': dbv_obj.name,
                    'amount_total': dbv_obj.amount_total,
                    'tenphim': dbv_obj.dm_phim_id.name,
                    'phong': dbv_obj.dm_phong_id.name,
                    # 'batdau': dbv_obj.dm_lichchieu_id.batdau,
                    # 'ketthuc': dbv_obj.dm_lichchieu_id.ketthuc,
                    # strToTimeGmt7(j.date_order).strftime("%d/%m/%Y %H:%M:%S")
                    'batdau': strToTimeGmt7(dbv_obj.dm_lichchieu_id.batdau).strftime("%d/%m/%Y %H:%M:%S"),
                    'ketthuc': strToTimeGmt7(dbv_obj.dm_lichchieu_id.ketthuc).strftime("%d/%m/%Y %H:%M:%S"),
                    'lines': lines,
                    'rapphim': dbv_obj.dm_lichchieu_id.dm_diadiem_id.name,
                    'thanhtoan': dbv_obj.dm_ptthanhtoan_id.name,
                    'tt_chuyenkhoan': dbv_obj.dm_ptthanhtoan_id.tt_chuyenkhoan,
                    'ht_thanhtoan': dbv_obj.ht_thanhtoan,
                    'qrcode': 'mã qrcode',

                }
                return json.dumps(dbv_info)
        else: 
            dbv_info = {}
        
        return json.dumps(dbv_info)

    
    # api danh sach đơn bán vé chuyển khoản của user từ app
    @http.route(['/cnm/api/user/dbv_bank/'], type='json', auth="public", methods=['POST'], csrf=False, website=True, cors='*')
    def cnm_api_user_dbv_bank(self, user_id=None, access_token=None, **kw):
        data = request.jsonrequest
        if data: 
            user_id = data['user_id']
            access_token = data['access_token']

        dbv = []
        if user_id != '':
            # [1,5,3,4,...]
            # dbv_obj = request.env['dm.donbanve'].sudo().search([('user_id','=',user_id), ('ht_thanhtoan','=','bank')], order='id desc', limit=1)
            dbv_obj = request.env['dm.donbanve'].sudo().search([('makhachhang','=',user_id), ('ht_thanhtoan','=','bank')], order='id desc', limit=1)
            if dbv_obj: 
                for i in dbv_obj:
                    for j in i:
                        lines = []
                        for r in j.dm_donbanve_line_ids: 
                            lines.append({
                                'name': r.name,
                                'loaive': r.loaive,
                                'dongia': r.dongia,
                            })
                        dbv_info = {
                            'id': j.id, 
                            'name': j.name,
                            'sodienthoai': j.sodienthoai,
                            'amount_total': j.amount_total,
                            'tenphim': j.dm_phim_id.name,
                            'phong': j.dm_phong_id.name,
                            # 'batdau': j.dm_lichchieu_id.batdau,
                            # 'ketthuc': j.dm_lichchieu_id.ketthuc,
                            'batdau': strToTimeGmt7(j.dm_lichchieu_id.batdau).strftime("%d/%m/%Y %H:%M:%S"),
                            'ketthuc': strToTimeGmt7(j.dm_lichchieu_id.ketthuc).strftime("%d/%m/%Y %H:%M:%S"),
                            'lines': lines,
                            'rapphim': j.dm_lichchieu_id.dm_diadiem_id.name,
                            # 'thanhtoan': j.payment_method,
                            'thanhtoan': j.dm_ptthanhtoan_id.name,
                            'state': j.state,
                            'ht_thanhtoan':j.ht_thanhtoan,
                            'date_order':strToTimeGmt7(j.date_order).strftime("%d/%m/%Y %H:%M:%S") ,
                            'tt_chuyenkhoan': j.dm_ptthanhtoan_id.tt_chuyenkhoan,

                        }
                        dbv.append(dbv_info)
        else: 
            dbv = {}
        
        return json.dumps(dbv, ensure_ascii=False)
        # end def

    # api đơn bán vé của user
    @http.route(['/cnm/test'], type='http', auth="public", csrf=False, website=True, cors='*')
    def cnm_test(self, order_name=None, access_token=None, **kw):
        dbv_obj = request.env['dm.donbanve'].sudo().search([('name','=','TGC-2022000825'), ('user_id','=',176)], limit=1)
        if dbv_obj: 
            lines = []
            for r in dbv_obj.dm_donbanve_line_ids: 
                lines.append({
                    'name': r.name,
                    'loaive': r.loaive,
                })
            dbv_info = {
                'name': dbv_obj.name,
                'amount_total': dbv_obj.amount_total,
                'tenphim': dbv_obj.dm_phim_id.name,
                'phong': dbv_obj.dm_phong_id.name,
                'batdau': dbv_obj.dm_lichchieu_id.batdau,
                'ketthuc': dbv_obj.dm_lichchieu_id.ketthuc,
                'lines': lines,

            }
        else: 
            dbv_info = {}
        
        return json.dumps(dbv_info)
    

