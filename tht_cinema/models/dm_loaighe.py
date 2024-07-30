# -*- coding: utf-8 -*-
from odoo import models, fields


class DmLoaighe(models.Model):
    _name = "dm.loaighe"
    _description = 'Loại ghế '
    name = fields.Char('Loại ghế')
    # tenloaighe = fields.Char('Loại ghế ')
    donvitinh = fields.Char('ĐVT ')
    mau = fields.Char('Màu')
    kieughe = fields.Selection([
        ('don', 'Ghế đơn'),
        ('doi', 'Ghế đôi'),] ,
         string='Kiểu ghế ', default='don')
    ghichu = fields.Char('Ghi chú')
    hanghoa = fields.Char('Hàng hóa')
    sudung = fields.Boolean('Sử  dụng')
    # dm_phong_id = fields.Many2one('dm.phong', string="Phòng chiếu ")
    
    