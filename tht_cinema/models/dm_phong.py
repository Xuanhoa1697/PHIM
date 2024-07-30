# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons import decimal_precision as dp

class DmPhong(models.Model):
    _name = "dm.phong"
    _description = 'Danh sách Phòng chiếu '
    _sql_constraints = [
                     ('field_unique', 
                      'unique(name, dm_diadiem_id)',
                      'Phòng đã tồn tại')]
    name = fields.Char('Tên phòng')
    # tenphong = fields.Char('Tên phòng')
    dm_diadiem_id = fields.Many2one('dm.diadiem', string='Rạp phim')
    thietbiphongchieu = fields.Text('Thiết bị phòng chiếu')
    ghichu = fields.Char('Ghi chú')
    hangngang = fields.Integer('Hàng ngang', help='>0 đánh dấu từ trái qua phải, <0 ngược lại ', require=True)
    sudung = fields.Boolean('Sử  dụng')
    dm_phong_line_ids = fields.One2many('dm.phong.line', 'dm_phong_id', string="Phong")
    columns = fields.Char( string='Cột') 
    rows = fields.Char( string='Dòng', default='A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P') 
    css_custom = fields.Text('Mã phát triển' , help='css')
    custom_styles = fields.Text('Mã phát triển App' , help='Mã phát triển App')
    tongsoghe = fields.Integer('Tổng số ghế ' )


class DmPhongLine(models.Model):
    _name = "dm.phong.line"
    _description = 'Danh sách chi tiết phòng'
    name = fields.Char('Loại ghế ')
    dm_phong_id = fields.Many2one('dm.phong', 'Tên phòng')
    dm_loaighe_id = fields.Many2one("dm.loaighe", "Loại ghế ")
    price = fields.Float(string='Price', digits=dp.get_precision('Product Price'))
    x = fields.Integer('x')
    y = fields.Integer('y')
    soluong = fields.Integer('Số lượng ')
    columns = fields.Char( string='Cột')
    columns_map = fields.Char( string='Sơ đồ cột ') 
    ghichu = fields.Char('Ghi chú')
    sudung = fields.Boolean('Sử  dụng')
    

    @api.onchange('dm_loaighe_id')
    def do_ten_loai_ghe(self):
        for rec in self:
            rec.name = rec.dm_loaighe_id.name

    



