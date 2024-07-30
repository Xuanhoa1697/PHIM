# -*- coding: utf-8 -*-
from odoo import models, fields

class Dmghe(models.Model):
    _name = "dm.ghe"
    _description = 'Danh sách ghế '
    name = fields.Char('Tên ghế ')
    tenghe = fields.Char('Tên ghế ')
    maghe = fields.Char('Mã ghế ')
    x = fields.Char('x')
    y = fields.Char('y')
    w = fields.Char('w')
    h = fields.Char('h')
    maunen = fields.Char('Màu nền ')
    maphong = fields.Many2one('dm.phong', string = 'Mã phòng ')
    maloaighe = fields.Many2one('dm.loaighe', string='Mã loại ghế  ')
    ghichu = fields.Char('Ghi chú')
    sudung = fields.Boolean('Sử  dụng')
    

