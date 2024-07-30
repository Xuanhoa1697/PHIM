# -*- coding: utf-8 -*-

from odoo import models,fields

class DmProduct(models.Model):
    _inherit = "product.product"

    ticket = fields.Boolean(string = "Vé xem phim")

class DmLoaive(models.Model):
    _name = "dm.loaive"
    _description = 'Danh sách Loại vé'

    name = fields.Char('Loại vé')
    ghichu = fields.Char('Ghi chú')
    sudung = fields.Boolean('Sử  dụng')
    macdinh = fields.Boolean('Mặc định ')
    thanhvien = fields.Boolean('Thành viên')



