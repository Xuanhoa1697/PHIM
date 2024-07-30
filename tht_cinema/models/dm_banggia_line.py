# -*- coding: utf-8 -*-
from odoo import models, fields

class DmBanggia(models.Model):
    _name = "dm.banggia"
    _description = 'Bảng giá'
    name = fields.Char('Mã bảng giá')
    mabanggia = fields.Char('Mã bảng giá')
    ghichu = fields.Char('Ghi chú')
    sudung = fields.Boolean('Sử  dụng')
    mode = fields.Char('Mode')
    
