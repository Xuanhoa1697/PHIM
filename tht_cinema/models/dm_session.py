# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons import decimal_precision as dp
import datetime


class DmDonbanve_ext(models.Model):
    _inherit = 'dm.donbanve'

    dm_session_id = fields.Many2one('dm.session', string='Điểm bán vé')
    dm_session_line_id = fields.Many2one(
        'dm.session.line', string='Phiên bán vé')


class DmDonbanveline_ext(models.Model):
    _inherit = 'dm.donbanve.line'

    dm_session_id = fields.Many2one('dm.session', string='Điểm bán vé')
    dm_session_line_id = fields.Many2one(
        'dm.session.line', string='Phiên bán vé')


class DMSession(models.Model):
    _name = 'dm.session'
    _order = 'id desc'
    _description = 'Diem ban ve'

    POS_SESSION_STATE = [
        # method action_pos_session_open
        ('opening_control', 'Opening Control'),
        # method action_pos_session_closing_control
        ('opened', 'Đang bán vé'),
        # method action_pos_session_close
        ('closing_control', 'Closing Control'),
        ('closed', 'Ngừng bán'),
        ('paused', 'Tạm dừng'),
    ]

    name = fields.Char(string='Session ID', required=True,)
    dm_session_line_ids = fields.One2many(
        'dm.session.line', 'dm_session_id', string='Sessions Lines')
    current_session_line_id = fields.Many2one(
        'dm.session.line', string="Current Session Line")
    user_id = fields.Many2one(
        'res.users', string='Nhân viên bán hàng',
        required=True,
        default=lambda self: self.env.uid)

    start_at = fields.Datetime(string='Opening Date', readonly=True)
    stop_at = fields.Datetime(string='Closing Date', readonly=True, copy=False)

    state = fields.Selection(
        POS_SESSION_STATE, string='Status',
        required=True, readonly=True,
        index=True, copy=False, default='closed')

    sequence_number = fields.Integer(
        string='Order Sequence Number', help='A sequence number that is incremented with each order', default=1)
    login_number = fields.Integer(string='Login Sequence Number',
                                  help='A sequence number that is incremented each time a user resumes the pos session', default=0)

    dm_donbanve_ids = fields.One2many(
        'dm.donbanve', 'dm_session_id',  string='Đơn bán vé')
    dm_diadiem_id = fields.Many2one('dm.diadiem',  string='Rạp phim')
    dm_ptthanhtoan_id = fields.Many2one(
        'dm.ptthanhtoan',  string='Phương thức thanh toán')
    datvetruoc = fields.Boolean(string='Đặt vé trước')

    naptienvao = fields.Float(string="Nạp tiền vào")
    ruttienra = fields.Float(string="Rút tiền ra")
    tientrongket = fields.Float(
        string="Tiền trong két", compute='_compute_tientrongket', store=False)

    @api.depends("naptienvao", "ruttienra")
    def _compute_tientrongket(self):
        # return ''
        for record in self:
            tienbanve = ''
            record.tientrongket = 0
            total = 0
            if record.current_session_line_id.id is not False:
               domain = [('dm_session_line_id', '=', record.current_session_line_id.id),
                          ("dm_ptthanhtoan_id", '=', record.dm_ptthanhtoan_id.id)]
               dbv_ids = self.env['dm.donbanve'].search(domain)
               if dbv_ids and len(dbv_ids) > 0:
                   for dbv in dbv_ids:
                       total += dbv.amount_total
                       record.tientrongket = record.naptienvao - record.ruttienra + total

                        
    
    # url_banve = fields.Char(related='dm_diadiem_id.url_banve', string='URL bán vé')
    url_banve = fields.Char('Link bán vé', compute='_url_banve')

    def _url_banve(self):
        for rec in self:
            if rec.datvetruoc is False :
                rec.url_banve = '/cinema/pos_id/' + str(rec.id) + '/'
            else: 
                rec.url_banve = '/cinema/pos_id_datvetruoc/' + str(rec.id) + '/'
    

    _sql_constraints = [('uniq_name', 'unique(name)', "Tên điểm bán vé không được trùng !")]

    def open_dm_session(self):
        for rec in self:
            if self.env.uid == self.user_id.id :
                values = {
                    'dm_session_id': rec.id ,
                    'name': rec.name ,
                    'start_at': fields.Datetime.now() ,
                    'user_id': rec.user_id.id,
                    'datvetruoc' : rec.datvetruoc,
                    'state' : 'opened',
                    }
                session_line = rec.env['dm.session.line'].sudo().create(values)
                rec.sudo().state = 'opened'
                rec.sudo().current_session_line_id = session_line.id
                return{
                    'name': 'ban ve',
                    'type': 'ir.actions.act_url',
                    'url': rec.url_banve,
                    'target': 'self'
                }
            else:
                return False
    
    def resume_dm_session(self):
        for rec in self:
            return{
                'name': 'ban ve',
                'type': 'ir.actions.act_url',
                'url': rec.url_banve,
                'target': 'self'
            }

    def close_dm_session(self):
        if self.env.uid == self.user_id.id :
            values = {
                    'end_at': fields.Datetime.now() ,
                    'state': 'closed' ,
                    }
            session_line = self.env['dm.session.line'].browse(self.current_session_line_id.id).sudo().write(values)
            self.sudo().state = 'closed'
            self.sudo().current_session_line_id = ''
        self.sudo().state = 'closed'
        return False
    
    

    

class DMSessionLine(models.Model):
    _name = 'dm.session.line'
    _order = 'id desc'
    _description = 'Phiên bán vé'

    POS_SESSION_LINE_STATE = [
        ('opened', 'Đang bán vé'),               # method action_pos_session_closing_control
        ('closed', 'Ngừng bán'),
    ]

    name = fields.Char(string='Tên')
    dm_session_id = fields.Many2one('dm.session', 'Điểm bán vé')
    start_at = fields.Datetime(string='Bắt đầu ')
    end_at = fields.Datetime(string='Kết thúc ')
    user_id = fields.Many2one(
        'res.users', string='Responsible',
        required=True,
        default=lambda self: self.env.uid)
    dm_donbanve_ids = fields.One2many('dm.donbanve', 'dm_session_line_id', string='Đơn bán vé')
    datvetruoc = fields.Boolean(string='Đặt vé trước')

    state = fields.Selection(POS_SESSION_LINE_STATE, string='Trạng thái', copy=False )

    # @api.multi
    def open_in_ket_ca(self, context):
        return {
                'type': 'ir.actions.act_url',
                'url': '/cinema/open_in_ket_ca/%s' % (self.id),
                'target': 'new',
                'res_id': self.id,
            }



class DMSessionLineReport(models.Model):
    _name = 'dm.session.line.report'
    _order = 'id desc'
    _description = 'Báo cáo Phiên bán vé'

    categ_id = fields.Many2one('product.category', string='Chủng loại hàng')
    product_id = fields.Many2one('product.product', string='Sản phẩm')
    qty = fields.Float(string='SL')
    price_unit = fields.Float(string='Giá', digits=dp.get_precision('VNG Currency'))
    total_amount = fields.Float(string='Thành tiền', digits=dp.get_precision('VNG Currency'))
    dm_session_line_id = fields.Many2one('dm.session.line', string='Báo cáo phiên bán vé')

    loaighe = fields.Char("Loại ghế ")
    loaive = fields.Char("Loại vé ")
    phongchieu = fields.Char("Phòng chiếu ")
    rapphim = fields.Char("Rạp phim")
    tenphim = fields.Char("Tên phim")
    lichchieu = fields.Char("Lịch chiếu ")
    dm_banggia_id = fields.Many2one('dm.banggia', string='Bảng giá ')
    dm_lichchieu_id = fields.Many2one('dm.lichchieu', "Lịch chiếu")
