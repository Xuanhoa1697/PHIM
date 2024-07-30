# -*- coding: utf-8 -*-
from odoo import models, fields
from odoo.addons import decimal_precision as dp

class DmBanggia(models.Model):
    _name = "dm.banggia"
    _description = 'Bảng giá'
    name = fields.Char('Mã bảng giá')
    mabanggia = fields.Char('Mã bảng giá')
    ghichu = fields.Char('Ghi chú')
    sudung = fields.Boolean('Sử  dụng')
    mode = fields.Char('Mode')
    dm_banggia_line_ids = fields.One2many('dm.banggia.line', 'dm_banggia_id', string="Chi tiết bảng giá")
    

class Dmbanggialine(models.Model):
    _name = "dm.banggia.line"
    _description = 'Danh sách chi tiết bảng giá'
    name = fields.Char('Mã bảng giá')
    dm_banggia_id = fields.Many2one('dm.banggia', 'Bảng giá')
    dm_loaighe_id = fields.Many2one('dm.loaighe', 'Loại ghế ')
    dm_loaive_id = fields.Many2one('dm.loaive', 'Loại vé ')
    # dm_thoigian_id = 
    dongia = fields.Float(string='Đơn giá', digits=dp.get_precision('Product Price'))
    price = fields.Float(string='Price', digits=dp.get_precision('Product Price'))
    ngay = fields.Date("Ngày")
    macdinh = fields.Char("Mặc định")

    ghichu = fields.Char('Ghi chú')
    sudung = fields.Boolean('Sử  dụng')

