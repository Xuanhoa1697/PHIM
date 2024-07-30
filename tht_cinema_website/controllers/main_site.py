# -*- coding: utf-8 -*-

import json

from werkzeug import redirect
from odoo import fields, http
from odoo.http import request
from odoo import tools
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import AccessError, UserError
from odoo.tools import html_escape, config




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

api_domain = tools.config.get('api_domain')


class ThtCinemaWebsiteBooking(http.Controller):

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
                    
                    'dm_session_id': donbanve_info['dm_session_id'],
                    'dm_session_line_id': donbanve_info['dm_session_line_id'],
                }
                donbanve_line_ids.append((0,0, rec_one))


        #     registrations_to_create.append(registration_values)

        list_seat = []
        list_seat.append({
            'name': 'seat1'
        })

        donbanve_state = 'draft'
        donbanve_source = 'website'
        print_status = False
        if donbanve_info['datvetruoc'] == 'True':
            donbanve_state = 'draft'
            donbanve_source = 'website'
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
            # 'payment_method': donbanve_info['payment_method'],
            'ht_thanhtoan': donbanve_info['ht_thanhtoan'],
            # self._ptthanhtoan(donbanve_info['ptthanhtoan_id']).hinhthucthanhtoan
            # 'dm_ptthanhtoan_id': donbanve_info['payment_method'],
            'dm_ptthanhtoan_id': donbanve_info['ptthanhtoan_id'],
            
            'dm_session_id': donbanve_info['dm_session_id'],
            
            'dm_session_line_id': donbanve_info['dm_session_line_id'],
            'date_hoadon': '',
            'date_order': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            # 'date_order': datetime.datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
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
                [('dm_banggia_id', '=', dm_banggia_id.id), 
                    ('dm_loaighe_id', '=', int(dm_loaighe_id)),
                    ('dm_loaive_id', '=', int(dm_loaive_id)),
                ], limit=1)
        return dongia_obj.dongia
    
    http.route(['''/cinema/phimdangchieu/'''], type='http', auth="public", website=True)
    def cinema_phimdangchieu(self, **kw):
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
    def cinema_pos_line_id(self, pos_line_id ='', lichchieu_id ='', **kwargs):
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

    # phim --> lichchieu --> all --> dang chieu
    # /cinema/phim/lichchieu_all/11
    @http.route(['''/cinema/phim/lichchieu_all/<int:dm_phim_id>'''], type='http', auth="public", website=True)
    def cinema_phim_lichchieu_all(self, dm_phim_id ='', lichchieu_id ='', **kwargs):
        lichchieu = []
        date_list = []
        if request.env.user.id == request.env.ref('base.public_user').id:
            return request.render('web.login', {})
        lichchieu_obj = request.env['dm.lichchieu']
        # today = datetime.datetime.now().strftime('%Y-%m-%d')
        today = datetime.date.today()
        for i in range(0,9): 
            date_list.append(today + relativedelta(days=i))

        
        if kwargs.get('ngaychieu', '') !='':
            ngaychieu = kwargs.get('ngaychieu')
        else: 
            ngaychieu = today
        group_lichchieu_obj = lichchieu_obj.read_group([('sudung','=', True),('dm_phim_id','=',dm_phim_id)], fields=['id', 'ngaychieu','batdau', 'ketthuc'],groupby=['ngaychieu:day']) 
        if group_lichchieu_obj:
            for rec in group_lichchieu_obj:
                lichchieu.append({
                    # 'dm_phim': request.env['dm.phim'].browse(rec['dm_phim_id'][0]),
                    'ngaychieu': rec['ngaychieu:day'],
                    'dm_lichchieu_obj' : lichchieu_obj.search([('ngaychieu','=', rec['ngaychieu:day']),('sudung','=', True)],limit=500),
                })
        
        values = {
            # 'dm_diadiem_obj': dm_diadiem_obj, 
            'date_list': date_list, 
            'lichchieu': lichchieu,
            'group_lichchieu_obj': group_lichchieu_obj
            }

        return request.render("tht_cinema_website.phim_lichchieu_all", values)
        # end cinema_phim_lichchieu_all
    
    # /cinema/datve/lichchieu/545
    @http.route(['''/cinema/datve/lichchieu/<int:dm_lichchieu_id>'''], type='http', auth="public", website=True)
    def cinema_datve_dm_lichchieu_id(self, dm_phim_id ='', dm_lichchieu_id ='', **kwargs):
        sv_socket_io = check_sv_socket_io(tools.config.get('sv_socket_io'))
        if request.env.user.id == request.env.ref('base.public_user').id:
            return request.render('web.login', {})

        event = request.env['dm.lichchieu'].sudo().search([('id','=',dm_lichchieu_id)])
        if len(event) < 1 :
            return "<div> Đăng nhập trước khi bán </div>"

        # ptthanhtoan = request.env['dm.ptthanhtoan'].search([('source','=','Website'), ('status','=','true')])
        ptthanhtoan = request.env['dm.ptthanhtoan'].search([('source','=','website'), ('status','=','true')])
        values = {
            'session_info': json.dumps(request.env['ir.http'].session_info()),
            'lichchieu_id': dm_lichchieu_id, 
            'event': event,
            'dm_lichchieu': event,
            'sv_socket_io': sv_socket_io,
            'ptthanhtoan': ptthanhtoan,
           
        }
        return request.render("tht_cinema_website.datve", values)
        # end cinema_phim_lichchieu_datve

    @http.route(['/cnm/web/momo/checkout/<model("dm.lichchieu"):event>'], type='json', auth="user", methods=['POST'], csrf=False, website=True)
    def cnm_web_momo_checkout_lc_id(self, event, order=None, access_token=None, **post):
        tickets = self._process_tickets_form(event, post)

        ptthanhtoan = request.env['dm.ptthanhtoan'].sudo().browse(int(post.get('ptthanhtoan_id', '')))

        donbanve_info = {
            'makhachhang' : post.get('makhachhang', '') ,
            'sodienthoai' : post.get('sodienthoai', '') ,

            'ptthanhtoan_id' : post.get('ptthanhtoan_id', '') ,
            'ht_thanhtoan': ptthanhtoan.ht_thanhtoan, 
            
            'dm_session_id' : post.get('dm_session_id', '') ,
            'dm_session_line_id' : post.get('dm_session_line_id', '') ,
            'datvetruoc' : post.get('datvetruoc', '') ,
        }
        
        availability_check = True
        
        if not tickets:
            return False

        donbanve_sudo = self._donbanve_create_web_momo_from_registration_post( event, tickets , donbanve_info)
        vn_timezone = pytz.timezone('Asia/Ho_Chi_Minh')
        # return True
        if donbanve_sudo :
            madonbanve = donbanve_sudo[1]
            if ptthanhtoan.ht_thanhtoan == 'momo':   
                order = donbanve_sudo[0].id
                try:
                    order_sudo = self._order_check_access(order, access_token=access_token)
                except AccessError:
                    return request.redirect('/cinema/inlaive_order')

                values = self._order_get_page_view_values(order_sudo, access_token, **post)
                # return request.render("tht_cinema.inlaive_order_line", values)                           
                # response = http.Response(template='tht_cinema_website.momo', qcontext={'tickets': tickets, 'event': event, 'availability_check': availability_check, 'vn_timezone': vn_timezone, 'madonbanve': madonbanve  })
                response = http.Response(template='tht_cinema_website.momo_dbv', qcontext= values)
                return response.render()

            # thanh toán tiền mặt
            if ptthanhtoan.ht_thanhtoan == 'cash':   
                order = donbanve_sudo[0].id
                try:
                    order_sudo = self._order_check_access(order, access_token=access_token)
                except AccessError:
                    return request.redirect('/cinema/inlaive_order')

                values = self._order_get_page_view_values(order_sudo, access_token, **post)
                # return request.render("tht_cinema.inlaive_order_line", values)
                            
                # response = http.Response(template='tht_cinema_website.momo', qcontext={'tickets': tickets, 'event': event, 'availability_check': availability_check, 'vn_timezone': vn_timezone, 'madonbanve': madonbanve  })
                response = http.Response(template='tht_cinema_website.cash_dbv', qcontext= values)
                return response.render()
        else:
            return False
        
    
    # /cmn/huy-giao-dich-momo
    @http.route(['''/cnm/huy-giao-dich-momo'''], type='http', auth="user", website=True)
    def cnm_huy_giao_dich_momo(self, **kwargs):
        values = {
        }
        return request.render("tht_cinema_website.huygiaodichmomo", values)
        # end cmm/huy-giao-dich-momo

    # thanh toán momo
    @http.route(['/cnm/web/momo/payment'], type='http', auth="user", methods=['POST'], csrf=False, website=True)
    def cnm_web_momo_payment(self, order=None, access_token=None, **post):
        order= post.get('order_id') or ''
        vn_timezone = pytz.timezone('Asia/Ho_Chi_Minh')
        # return True
        if order:
            try:
                order_sudo = self._order_check_access(int(order), access_token=access_token)
            except AccessError:
                return request.redirect('/cinema/inlaive_order')
            # values = self._order_get_page_view_values(order_sudo, access_token, **post)
            dbh_info = {
                    'orderInfo': order_sudo.name,
                    'amount': int(order_sudo.amount_total),
                }
            # result = momo.CreateOrderByMomo(dbh_info)
            momo_data = momo.CreateOrderByMomo(dbh_info, request.session.uid)
            if momo_data == '':
                return False

            req_momo = json.loads(momo_data['req_momo'])
            res_momo = momo_data['res_momo']
            
            momo_obj = request.env['dm.momo'].sudo().create({
                'name': req_momo['orderInfo'] ,
                'user_id': momo_data['user_id'] ,
                'source': 'website' ,
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
                
                return request.redirect(res_momo['payUrl'])
                
            else :
                return {}
        
        # return request.render("tht_cinema.inlaive_order_line", values)
                    
        # response = http.Response(template='tht_cinema_website.momo', qcontext={'tickets': tickets, 'event': event, 'availability_check': availability_check, 'vn_timezone': vn_timezone, 'madonbanve': madonbanve  })
        # response = http.Response(template='tht_cinema_website.momo_dbv', qcontext= values)
        # return response.render()    
    
    # end fn 

    # kết quả thanh toán momo trả về 
    @http.route(['/cnm/web/momo/result'], type='http', auth="user", methods=['GET'], csrf=False, website=True)
    def cnm_web_momo_result(self, order=None, access_token=None, **kw):
        momo_obj = request.env['dm.momo'].sudo().search([('momo_requestid','=',kw.get('requestId'))], limit=1)
        momo_obj.write({
            'momo_resultcode': kw.get('resultCode'),
            'momo_message': kw.get('message'),
            'momo_transid': kw.get('transId'),
            'result_data': dict(kw)})

        #thanh toán thành công returnUrl
        # if kw.get('resultCode', '') == "0" :
        if kw.get('resultCode', '') == "0" :
            dbv_obj = request.env['dm.donbanve'].sudo().search([('name','=',kw.get('orderInfo'))], limit=1)
            dbv_obj.write({
                'momo_resultcode': kw.get('resultCode'),
                'momo_message': kw.get('message'),
                'momo_transid': kw.get('transId'),
                'state': 'done', 
                'user_id': request.session.uid ,
                'date_hoadon': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                })
            # dbv_obj.donbanve_invoice_create()
            return request.redirect('https://'+api_domain+'/cnm/user/dbv/' + kw.get('orderInfo'))
        else : 
            dbv_obj = request.env['dm.donbanve'].sudo().search([('name','=',kw.get('orderInfo'))], limit=1)
            if dbv_obj:
                dbv_obj.unlink()
            # huỷ giao dịch
            return request.redirect('https://'+api_domain+'/cnm/huy-giao-dich-momo')
            
        return request.redirect('https://thegoldcinema.com/cnm/phim/dangchieu')
        # return request.make_response(json.dumps(kw))
    
    @http.route(['/cnm/user/dbv/<string:order_name>'], type='http', auth="user", methods=['GET'], csrf=False, website=True)
    def cnm_user_dbv(self, order_name=None, access_token=None, **kw):
        if order_name != '':
            dbv_obj = request.env['dm.donbanve'].sudo().search([('name','=',order_name), ('user_id','=',request.env.uid)], limit=1)
            if dbv_obj: 
                values = {
                    'dbv_obj': dbv_obj
                }
            else: 
                values = {}
        return request.render('tht_cinema_website.user_dbv', values)
    
    
    @http.route(['/cnm/soatve/'], type='http', auth="user", methods=['GET'], csrf=False, website=True)
    def cnm_soatve(self, order_name=None, access_token=None, **kw):
        if order_name != '':
            dbv_obj = request.env['dm.donbanve'].sudo().search([('name','=',order_name),('state','=','done')], limit=1)
            if dbv_obj: 
                values = {
                    'dbv_obj': dbv_obj
                }
            else: 
                values = {}
        return request.render('tht_cinema_website.soatve', values)
    
    # Soát vé, chỉ hiện đơn đã thanh toán 
    @http.route(['/cnm/soatve/result'], type='json', auth="user", methods=['POST'], csrf=False, website=True)
    def cnm_soatve_result(self, **kw):
        order_name = kw.get('order_name', '') ,
        if order_name != '':
            dbv_obj = request.env['dm.donbanve'].sudo().search([('name','=',order_name),('state','=','done')], limit=1)
            if dbv_obj: 
                values = {
                    'dbv_obj': dbv_obj
                }
                  
            else: 
                values = {}                
        response = http.Response(template='tht_cinema_website.soatve_result', qcontext= values)
        return response.render()  

    @http.route(['/cnm/web/momo/notify'], type='http', auth="public", methods=['GET','POST'], csrf=False, website=True, cors='*')
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

    @http.route(['''/cinema/phimsapchieu'''], type='http', auth="public", website=True)
    def cinema_phimsapchieu(self, **kw):
        dm_phim = request.env['dm.phim'].sudo()
        dm_phim_obj = dm_phim.search([('status','=', 'sapchieu'),('sudung','=', True)])        
        values = {
            'dm_phim_obj': dm_phim_obj
            }
        return request.render("tht_cinema_website.sapchieu", values)

    # end phimsapchieu




    