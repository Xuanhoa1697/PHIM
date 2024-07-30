# -*- coding: utf-8 -*-
from odoo import models, fields

class DmDiadiem(models.Model):
    _name = "dm.diadiem"
    _description = 'Rạp Phim'
    name = fields.Char('Tên rạp')
    marap = fields.Char('Mã rạp')
    tendiadiem = fields.Char('Tên rạp')
    diachi = fields.Char('Địa chỉ')
    logo = fields.Binary(string='logo')
    dm_phong_ids = fields.One2many('dm.phong', 'dm_diadiem_id' , 'Danh sách phòng chiếu')
    ghichu = fields.Char('Ghi chú')
    sudung = fields.Boolean('Sử  dụng')
    id_sync = fields.Char('ID SYNC')
    server_cn = fields.Char('SERVER CN')
    data_cn = fields.Char('DATA CN')
    thongtinchuyenkhoan = fields.Text('Thông tin chuyển khoản')
    url_banve = fields.Char('Link bán vé', compute='_url_banve')
    img_app = fields.Binary(string='Image App')
    gioihanthoigian_lc = fields.Integer("Giới hạn thời gian hiện lịch chiếu")

    def _url_banve(self):
        for rec in self:
            rec.url_banve = '/cinema/lichchieu/' + str(rec.id) + '/'

    



