# -*- coding: utf-8 -*-

from odoo import models,fields, api, _
from datetime import datetime , timedelta
from odoo.exceptions import ValidationError

class DmLichchieu(models.Model):
    _name = "dm.lichchieu"
    _description = 'Danh sách Lịch chiếu'

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('dm.lichchieu') or _('New')
            result = super(DmLichchieu, self).create(vals)
            return result

    name = fields.Char(string='Lịch chiếu', required=True, copy=False, readonly=True,  index=True, default=lambda self: _('New'))
    dm_diadiem_id = fields.Many2one('dm.diadiem', 'Rạp phim')
    dm_phong_id = fields.Many2one('dm.phong', 'Phòng chiếu')
    dm_phim_id = fields.Many2one('dm.phim', 'Phim')
    tenphim = fields.Char(related='dm_phim_id.name', string='Tên phim', readonly=True, store='True')
    # tenphim = fields.Char(string='Tên phim' , )
    dm_banggia_id = fields.Many2one('dm.banggia', 'Bảng giá ')
    dm_donbanve_line_ids = fields.One2many('dm.donbanve.line', 'dm_lichchieu_id', 'Bảng giá ')
    price = fields.Float( 'Price ')
    # machatluongphim =
    
    ngaychieu = fields.Date('Ngày chiếu ' ,  store=True,)
    batdau = fields.Datetime('Bắt đầu ' , copy=False )
    ketthuc = fields.Datetime('Kết thúc ' , copy=False)

    thoiluong = fields.Integer( 'Thời lượng', related='dm_phim_id.thoiluong', readonly=True)

    hinhanh = fields.Char('Hình ảnh')
    danhgia = fields.Integer('Đánh giá ')
    ghichu = fields.Char('Ghi chú')
    sudung = fields.Boolean('Sử  dụng')
    xoa = fields.Boolean('Xoá ')
    ngayketthuc = fields.Date('Ngày kết thúc ')
    LastUpdate = fields.Date('Last update ')

    @api.onchange('batdau')
    def do_gio_ketthuc(self):
        for rec in self:
            if rec.dm_phim_id and rec.dm_phim_id.thoiluong != '' : 
                try:
                    batdau_obj = rec.batdau
                    duration = timedelta( minutes=rec.dm_phim_id.thoiluong)
                    rec.ketthuc = str(batdau_obj + timedelta( minutes=rec.dm_phim_id.thoiluong) )
                    rec.ngaychieu = batdau_obj.date()
                    # rec.tenphim = rec.dm_phim_id.name

                except ValueError:
                    print("Sai thời gian !!!")   
    # end gio ket thuc

    @api.onchange('dm_diadiem_id')
    def domain_dm_diadiem_id(self):
        for rec in self:
            return {'domain':{'dm_phong_id':[('dm_diadiem_id','=',rec.dm_diadiem_id.id)]}}
    
    @api.onchange('dm_phong_id')
    def domain_dm_phong_id(self):
        for rec in self:
            return {'domain':{'dm_phong_id':[('dm_diadiem_id','=',rec.dm_diadiem_id.id)]}}
    
    @api.constrains('batdau', 'ketthuc', 'dm_phong_id')
    def _check_dates(self):
        for fy in self:
            # Starting date must be prior to the ending date
            batdau = fy.batdau
            ketthuc = fy.ketthuc
            if ketthuc < batdau:
                raise ValidationError(_('The ending date must not be prior to the starting date.'))


            domain = [
                ('id', '!=', fy.id),
                ('dm_phong_id', '=', fy.dm_phong_id.id),
                '|', '|',
                '&', ('batdau', '<=', fy.batdau), ('ketthuc', '>=', fy.batdau),
                '&', ('batdau', '<=', fy.ketthuc), ('ketthuc', '>=', fy.ketthuc),
                '&', ('batdau', '<=', fy.batdau), ('ketthuc', '>=', fy.ketthuc),
            ]

            if self.search_count(domain) > 0:
                raise ValidationError(_('Lịch chiếu đã bị trùng lắp, vui lòng kiểm tra lại ' ))
    #end def

    @api.model
    def load_config(self, config_id):
        print('load_config dm.lichchieu')
        # if config_id:
        #     config_obj = self.env['pos.config'].search_read([('id','=',config_id)],['customer_display','image_interval','customer_display_details_ids'])
        #     if config_obj:
        #         return config_obj
        return False
    
    @api.model
    def broadcast_data(self, data):
        
        notifications = []
        vals = {
            'lichchieu_info':data.get('lichchieu_info'),
            'user_id':self._uid,
            'style_map':data.get('style_map'),
            'cart_data':data.get('cart_data'),
            'seat_map':data.get('seat_map'),
            'customer_name':data.get('client_name'),
            'order_total':data.get('order_total'),
            'change_amount':data.get('change_amount'),
            'payment_info':data.get('payment_info'),
        }
        notifications.append(((self._cr.dbname, 'cinemacustomer.display', self._uid), ('customer_display_data', vals)))
        self.env['bus.bus'].sendmany(notifications)
        return True
    
    @api.model
    def soveconlai(self,lichchieu_id):
        result = 0
        donbanve_line_obj = self.env['dm.donbanve.line'].search([('dm_lichchieu_id','=',lichchieu_id)])
        if donbanve_line_obj :
            result = self.dm_phong_id.tongsoghe - len(donbanve_line_obj)
        else:
            result = self.dm_phong_id.tongsoghe
        return result
    
    @api.model
    def tylebanve(self,lichchieu_id):
        result = 0
        donbanve_line_obj = self.env['dm.donbanve.line'].search([('dm_lichchieu_id','=',lichchieu_id)])
        if donbanve_line_obj :
            if self.dm_phong_id.tongsoghe > 0 :
                result = len(donbanve_line_obj) / self.dm_phong_id.tongsoghe * 100
        return result


