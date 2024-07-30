# -*- coding: utf-8 -*-

from odoo import models,fields

class DmPhim(models.Model):
    _name = "dm.phim"
    _description = 'Danh sách Phim'

    name = fields.Char('Tên phim')
    daodien = fields.Char('Đạo diễn')
    dienvien = fields.Char('diễn viên')
    dm_phim_theloai_id = fields.Many2one('dm.phim.theloai', "Thể loại phim ")
    nsx = fields.Char('NSX')
    nam = fields.Char('Năm')
    nhaphathanh = fields.Char('Nhà phát hành')
    namphathanh = fields.Char('Năm phát hành')
    thoiluong = fields.Integer('Thời lượng', required=True, )
    ngonngu = fields.Char('Ngôn ngữ')
    ngaykhoichieu = fields.Date('Ngày khởi chiếu')
    noidung = fields.Html('Nội dung')
    tyle = fields.Float(string='Tỷ lệ')
    hinhanh = fields.Binary(string='Hình ảnh')
    trailer = fields.Char(string='Trailer')
    gioihantuoi = fields.Char(string='Giới hạn tuổi ')
    ratephim=fields.Char(string='Rate Phim')
    status = fields.Selection([
        ('dangchieu', 'Đang chiếu'),
        ('sapchieu', 'Sắp chiếu'),
        ('cancel', 'Huỷ'),
        ], string='Trạng thái')

    state = fields.Selection([
        ('draft', 'Nháp'),
        ('done', 'Duyệt'),
        ('cancel', 'Huỷ'),
        ], string='state', readonly=True, copy=False, index=True, default='draft')
    date_order = fields.Datetime(string='Ngày mua')
    danhgia = fields.Integer('Đánh giá ')
    ghichu = fields.Char('Ghi chú')
    sudung = fields.Boolean('Sử  dụng')
    noibat = fields.Boolean('Nổi bật')
    id_sync = fields.Char('ID SYNC')
    user_id = fields.Many2one(
        'res.users', string='Người mua', default=lambda self: self.env.user)
    partner_id = fields.Many2one(
        'res.partner', string='Nhà cung cấp ', )

    dm_lichchieu_ids = fields.One2many('dm.lichchieu', 'dm_phim_id', string ='Lich chieu')
    
class DmTheLoaiPhim(models.Model):
    _name = "dm.phim.theloai"
    _description = 'Thể loại phim '

    name = fields.Char('Thể loại')
    sodangky = fields.Char('Số đăng ký')
  
    ghichu = fields.Char('Ghi chú')
    sudung = fields.Boolean('Sử  dụng')



