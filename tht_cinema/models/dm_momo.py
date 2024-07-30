# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons import decimal_precision as dp

class DmMomo(models.Model):
    _name = "dm.momo"
    _description = 'Danh sách giao dịch momo '
    # _sql_constraints = [
    #                  ('field_unique', 
    #                   'unique(requestid, dm_diadiem_id)',
    #                   'Phòng đã tồn tại')]
    name = fields.Char('Tên giao dịch')
    user_id = fields.Many2one('res.users')
    source = fields.Selection([
            ('posbanve', 'Pos bán vé'),
            ('posdatvetruoc', 'Pos đặt vé trước'),
            ('website', 'website'),
            ('app_mobile', 'App mobile'),
        ], string='Nguồn')
    amount = fields.Float('Số tiền')
    ngaygiaodich = fields.Datetime('Ngày giao dịch')
    momo_resultcode = fields.Char('Result code')
    momo_message = fields.Char('message')
    momo_orderid = fields.Char('Momo orderid')
    momo_requestid = fields.Char('Momo requestid')

    req_data = fields.Char('Request')
    res_data = fields.Char('Response')
    result_data = fields.Char('Result')
    ghichu = fields.Char('Ghi Chú')

    