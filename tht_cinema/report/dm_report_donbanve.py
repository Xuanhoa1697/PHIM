# -*- coding: utf-8 -*-
from odoo import fields, api, models, _
from odoo.exceptions import UserError, ValidationError
import time
from datetime import datetime, timedelta, date
from dateutil import relativedelta
from odoo.addons import decimal_precision as dp
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF, DEFAULT_SERVER_DATETIME_FORMAT as DTF

class ReportPosSale(models.Model):
    _name = 'dm.report.donbanve'
    _description = 'Report Đơn bán vé'
    
    @api.one
    @api.depends('general_lines', 'general_lines.qty', 'general_lines.total_amount')
    def _get_total(self):
        total_qty = total_amount = 0
        for line in self.general_lines:
            total_qty += line.qty
            total_amount += line.total_amount
        self.total_qty = total_qty
        self.total_amount = total_amount
        
    name = fields.Char(string='Tên báo cáo')
    date_from = fields.Date(string='Từ ngày', default=lambda *a: time.strftime('%Y-%m-01'))
    date_to = fields.Date(string='Đến ngày', default=str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10])
    # dm_session_id = fields.Many2one('stock.store', string='Cửa hàng', default=lambda self: self.env.user.dm_session_id)
    dm_diadiem_id = fields.Many2one('dm.diadiem', string='Rạp phim')
    dm_session_id = fields.Many2one('dm.session', string='Điểm bán vé')
    dm_session_line_id = fields.Many2one('dm.session.line', string='Phiên bán vé')
    total_qty = fields.Float(compute='_get_total', string='Tổng số lượng')
    total_amount = fields.Float(compute='_get_total', string='Tổng thành tiền', digits=dp.get_precision('VNG Currency'))
    detail_lines = fields.One2many('dm.report.donbanve.detail', 'report_id', string='Dữ liệu chi tiết')
    general_lines = fields.One2many('dm.report.donbanve.general', 'report_id', string='Dữ liệu tổng hợp')
    type = fields.Selection([('sale','Bán hàng'),('return','Trả lại')], string='Loại')
    yet_exported = fields.Boolean(string='Chưa xuất hóa đơn')
    # specification = fields.Many2one('account.invoice.specification','Mô tả mặt hàng kèm bảng kê')
    specification_number = fields.Char('Số bảng kê')
    date_export_specification = fields.Date(string='Ngày xuất bảng kê', default=lambda *a: time.strftime('%Y-%m-01'))
    user_id = fields.Many2one('res.users', string='Nhân viên bán vé')
    pos_session_id = fields.Many2one('pos.session', string='Mã phiên')
    config_id = fields.Many2one('pos.config', string='Điểm bán lẻ')

    payment_method = fields.Selection([
        ('cash', 'Tiền mặt'),
        ('bank', 'Thẻ')
    ], string='Hình thức thanh toán ')
    
    @api.onchange('user_id', 'dm_session_id', 'date_from', 'date_to', 'config_id')
    def _onchange_date_user(self):
        date_from = self.date_from and datetime.strptime(self.date_from, DF) or False
        date_to = self.date_to and datetime.strptime(self.date_to, DF) or False
        d_from = date_from and datetime.strftime(date_from, '%Y-%m-%d 00:00:00') or False
        d_to = date_to and datetime.strftime(date_to, '%Y-%m-%d 23:59:59') or False
        domain = [
            ('start_at', '>=', d_from),
            ('start_at', '<=', d_to),
        ]
        if self.dm_session_id:
            domain.extend([('config_id.dm_session_id', '=', self.dm_session_id.id)])
        if self.user_id:
            domain.extend([('user_id', '=', self.user_id.id)])
        if self.config_id:
            domain.extend([('config_id', '=', self.config_id.id)])   
            
        res = {}
        res['domain'] =  {'pos_session_id': domain}
        return res
    
    @api.model
    def create(self, vals):
        context = dict(self._context or {})
        if 'default_type' in context and context.get('default_type','') == 'sale':
            vals['name'] = u'Báo cáo bán hàng'
        else:
            vals['name'] = u'Báo cáo nhập đổi'
            
        if vals.get('specification_number'):
            check_exist = self.search([('specification_number', '=', vals.get('specification_number'))])
            if check_exist:
                raise UserError(_('Số bảng kê bị trùng, vui lòng kiểm tra lại!'))
        return super(ReportPosSale, self).create(vals)
    
    # @api.multi
    def write(self, vals):
        if vals.get('specification_number'):
            check_exist = self.search([('specification_number', '=', vals.get('specification_number'))])
            if check_exist:
                raise UserError(_('Số bảng kê bị trùng, vui lòng kiểm tra lại!'))
            
        return super(ReportPosSale, self).write(vals)
    
    @api.constrains('date_from', 'date_to')
    def check_date(self):
        if self.date_from > self.date_to:
            raise UserError(_(u'Đến ngày phải lớn hơn hoặc bằng Từ ngày'))
        
    # @api.multi
    def action_general(self):

        product_id = self.env['product.product'].search([("ticket", "=", True)],limit=1)
        data_detail = {}
        data_general = {}
        for data in self:
            if data.detail_lines:
                data.detail_lines.unlink()
            if data.general_lines:
                data.general_lines.unlink()
            date_from = data.date_from and datetime.strptime(data.date_from, DF) or False
            date_to = data.date_to and datetime.strptime(data.date_to, DF) or False
            d1 = date_from and datetime.strftime(date_from, '%Y-%m-%d 00:00:00') or False
            d2 = date_to and datetime.strftime(date_to, '%Y-%m-%d 23:59:59') or False
             
            domain = [('state','not in',('draft','cancel'))]
            # if data.yet_exported:
            #     domain = [('state','not in',[('invoiced')]),('is_has_ivnoice','!=',True)]
            if data.dm_session_id:
                domain += [('dm_session_id','=',data.dm_session_id.id)]
            # if data.type == 'sale':
            #     domain += [('is_return','!=',True)]
            # else:
            #     domain += [('is_return','=',True)]
            if data.user_id:
                domain += [('user_id','=',data.user_id.id)]
            # if d1:
            #     domain += [('date_order','>=',data.pos_session_id.id)]
            # if d2:
            
            orders = self.env['dm.donbanve'].search(domain)
            if d1 and d2:
                orders = orders.filtered(lambda x: (datetime.strptime(x.date_order, DTF) + timedelta(hours=7)) >= datetime.strptime(d1, DTF) and (datetime.strptime(x.date_order, DTF) + timedelta(hours=7)) <= datetime.strptime(d2, DTF))
            else:
                if d1:
                    orders = orders.filtered(lambda x: (datetime.strptime(x.date_order, DTF) + timedelta(hours=7)) >= datetime.strptime(d1, DTF) )
                if d2:
                    orders = orders.filtered(lambda x: (datetime.strptime(x.date_order, DTF) + timedelta(hours=7)) <= datetime.strptime(d2, DTF) )

            for order in orders:
                for line in order.dm_donbanve_line_ids:
                    # if data.type == 'sale' and line.qty < 0: continue
                    if 1 == 1 :
                        price_unit = line.dongia or 0
                        qty = abs(line.soluong)
                        total_amount = abs(price_unit * qty)
                        merger_code_detail = str(line.dm_lichchieu_id.id) + '_' + str(price_unit)
                        if merger_code_detail not in data_detail:
                            data_detail[merger_code_detail] = {
                                                               'categ_id': line.dm_lichchieu_id.dm_phim_id.id,
                                                               'product_id': product_id.id,
                                                               'qty': qty,
                                                               'price_unit': price_unit,
                                                               'total_amount': total_amount,
                                                               }
                        else:
                            data_detail[merger_code_detail]['qty'] += qty
                            data_detail[merger_code_detail]['total_amount'] += total_amount

                        #Line general
                        merger_code = str(line.dm_lichchieu_id.dm_phim_id.id)
                        if merger_code not in data_general:
                            data_general[merger_code] = {
                                                        'qty': qty,
                                                        'total_amount': total_amount,
                                                        'categ_id': line.dm_lichchieu_id.dm_phim_id.id and line.dm_lichchieu_id.dm_phim_id.id or False,
                                                        }
                        else:
                            data_general[merger_code]['qty'] += qty
                            data_general[merger_code]['total_amount'] += total_amount
            for k,v in data_detail.items():
                self.env['dm.report.donbanve.detail'].create({
                                                           'categ_id': v['categ_id'],
                                                           'product_id': v['product_id'],
                                                           'qty': v['qty'],
                                                           'price_unit': v['price_unit'],
                                                           'total_amount': v['total_amount'],
                                                           'report_id': data.id,
                                                           })
            for kg,vg in data_general.items():
                self.env['dm.report.donbanve.general'].create({
                                                            'categ_id': vg['categ_id'],
                                                            'qty': vg['qty'],
                                                            'total_amount': vg['total_amount'],
                                                            'report_id': data.id,
                                                            })
        return True
    
class ReportPosSaleDetail(models.Model):
    _name = 'dm.report.donbanve.detail'
    _description = 'Bao cao don ban ve chi tiet'
    
    date = fields.Datetime(string='Ngày bán')
    categ_id = fields.Many2one('dm.lichchieu', string='Nhóm Lịch chiếu')
    product_id = fields.Many2one('product.product', string='Sản phẩm')
    qty = fields.Float(string='SL')
    price_unit = fields.Float(string='Giá', digits=dp.get_precision('VNG Currency'))
    total_amount = fields.Float(string='Thành tiền', digits=dp.get_precision('VNG Currency'))
    report_id = fields.Many2one('dm.report.donbanve', string='Báo cáo bán vé', ondelete='cascade')
    
class ReportPosSaleGeneral(models.Model):
    _name = 'dm.report.donbanve.general'
    _description = 'Bao cao don ban ve tong hop'
    
    categ_id = fields.Many2one('product.category', string='Nhóm hàng')
    qty = fields.Float(string='SL')
    total_amount = fields.Float(string='Thành tiền', digits=dp.get_precision('VNG Currency'))
    report_id = fields.Many2one('dm.report.donbanve', string='Báo cáo bán vé', ondelete='cascade')
    
    