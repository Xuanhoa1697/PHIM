# -*- coding: utf-8 -*-
from odoo import models, fields

class DmDiadiem(models.Model):
    _name = "dm.ptthanhtoan"
    _description = 'Phương thức thanh toán'
    name = fields.Char('Tên')
    status = fields.Boolean('Trạng thái')

    source = fields.Selection([
            ('posbanve', 'Pos bán vé'),
            ('posdatvetruoc', 'Pos đặt vé trước'),
            ('website', 'Website'),
            ('app_mobile', 'App mobile'),
        ], string='Nguồn', default='pos')
    # mathanhtoan = fields.Char('Mã rạp')
    account_journal_id = fields.Many2one(
        'account.journal', string="Sổ nhật ký")
    ht_thanhtoan = fields.Selection([
            ('cash', 'TM'),
            ('bank', 'CK'),
            ('momo', 'MOMO'),
        ], string="Hình thức thanh toán")
    tt_chuyenkhoan = fields.Text('Thông tin chuyển khoản')
    

    



