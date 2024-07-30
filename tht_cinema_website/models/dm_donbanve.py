# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
from datetime import datetime
from odoo.exceptions import UserError, ValidationError, RedirectWarning


class DMDonbanve(models.Model):
    _inherit = "dm.donbanve"

    @api.multi
    def donbanve_invoice_create(self):
        if self.state !='done':
            return False

        inv_obj = self.env['account.invoice']
        inv_line_obj = self.env['account.invoice.line']
        # if self.partner_id:
        #     supplier = self.partner_id
        supplier = self.env['res.partner'].search([("name", "=", 'Khách vãng lai')],limit=1)

        # product_id = self.env['product.product'].search([("ticket", "=", True)],limit=1)
        product_id = self.env['product.product'].with_context(force_company=self.env.user.company_id.id).search([("name", "=", 'Vé xem phim')],limit=1)
        if product_id:
            company_id = product_id.company_id
        else: 
            company_id = self.env['res.users'].browse(1).company_id
        currency_salon = company_id.currency_id.id

        journal_id = ''
        journal = self.env['account.journal'].sudo().search([('code','=', 'HD'),('company_id','=',company_id.id)], limit=1)
        if journal:
            journal_id = journal.id
        
        inv_data = {
            # 'name': ,
            # 'reference': supplier.name,
            'type': 'out_invoice',
            'account_id': product_id.property_account_income_id.id, 
            'partner_id': supplier.id,
            'currency_id': currency_salon,
            'journal_id': journal_id,
            'origin': self.name,
            'company_id': company_id.id,
            'state': 'draft',
            
            # 'date_invoice': dm_lichchieu_id.ngaychieu,
            # 'state': 'paid',
        }
        inv_id = inv_obj.sudo().create(inv_data)
        
        self.invoice_number = inv_id
        
        
        for records in self.dm_donbanve_line_ids:
            if product_id.property_account_income_id.id:
                income_account = product_id.property_account_income_id.id
            elif product_id.categ_id.property_account_income_categ_id.id:
                income_account = product_id.categ_id.property_account_income_categ_id.id
            else:
                raise UserError(_('Please define income account for this product: "%s" (id:%d).') % (product_id.name,
                                                                                                     product_id.id))
            inv_line_data = {
                'name': product_id.name,
                'account_id': income_account,
                'price_unit': records.dongia,
                'quantity': 1,
                'product_id': product_id.id,
                'invoice_id': inv_id.id,
                'invoice_line_tax_ids':([(6,0,[tax.id for tax in product_id.taxes_id])]),
                
                
            }
            inv_line_obj.sudo().create(inv_line_data)
        
        # inv_id.sudo().action_invoice_open()
        # import pdb; pdb.set_trace() 
        inv_id.sudo().invoice_validate()
        # inv_id.write({'state': 'open'})

        # account_payment = self.env['account.payment']
        # payment_method = self.env['account.payment.method'].sudo().search([('name','=','Manual')],limit=1)

        # if self.payment_method=='cash':
        #     journal_payment = self.env['account.journal'].sudo().search([('code','=', 'CSH1'),('company_id','=',company_id.id)], limit=1)
        
        # if self.payment_method=='bank':
        #     journal_payment = self.env['account.journal'].sudo().search([('code','=', 'BNK1'),('company_id','=',company_id.id)], limit=1)

        # if journal_payment:
        #     journal_payment_id = journal_payment.id

        # pay_vals = { 
            
        #     'journal_id': journal_payment_id, 
        #     'amount':inv_id.amount_total, 
        #     'currency_id': inv_id.currency_id.id, 
        #     'payment_date': datetime.now().date(), 
        #     'communication': inv_id.name, 
        #     'payment_type':'inbound', 
        #     'payment_method_id': 1, 
        #     'partner_type': 'customer', 
        #     'partner_id': inv_id.partner_id.id,
        #     'destination_account_id':inv_id.account_id.id }
        # payment_create = account_payment.sudo().create(pay_vals)
        # payment_create.invoice_ids = [(4, inv_id.id)]
        # validate = payment_create.with_context(destination_account_id=inv_id.account_id.id).sudo().post()
        # inv_id.state = 'paid'
        
        return True
    # end invoice create

    # trả vé hoàn tiền
    @api.multi
    def trave_hoantien(self):
        if self.state =='done':
            inv_obj = self.env['account.invoice']
            inv_line_obj = self.env['account.invoice.line']
            # if self.partner_id:
            #     supplier = self.partner_id
            supplier = self.env['res.partner'].search([("name", "=", 'Khách vãng lai')],limit=1)

            # product_id = self.env['product.product'].search([("ticket", "=", True)],limit=1)
            # product_id = self.env['product.product'].search([("name", "=", 'Vé xem phim')],limit=1)
            product_id = self.env['product.product'].with_context(force_company=self.env.user.company_id.id).search([("name", "=", 'Vé xem phim')],limit=1)
            if product_id:
                company_id = product_id.company_id
            else: 
                company_id = self.env['res.users'].browse(1).company_id
            currency_salon = company_id.currency_id.id

            journal_id = ''
            journal = self.env['account.journal'].sudo().search([('code','=', 'HD'),('company_id','=',company_id.id)], limit=1)
            if journal:
                journal_id = journal.id
            
            inv_data = {
                # 'name': ,
                # 'reference': supplier.name,
                'type': 'in_invoice',
                'account_id': supplier.property_account_payable_id.id,
                'partner_id': supplier.id,
                'currency_id': currency_salon,
                'journal_id': journal_id,
                'origin': self.name,
                'company_id': company_id.id,
                
                # 'date_invoice': dm_lichchieu_id.ngaychieu,
                # 'state': 'paid',
            }
            inv_id = inv_obj.sudo().create(inv_data)
            self.invoice_number = inv_id
            
            
            for records in self.dm_donbanve_line_ids:
                if product_id.property_account_income_id.id:
                    income_account = product_id.property_account_income_id.id
                elif product_id.categ_id.property_account_income_categ_id.id:
                    income_account = product_id.categ_id.property_account_income_categ_id.id
                else:
                    raise UserError(_('Please define income account for this product: "%s" (id:%d).') % (product_id.name,
                                                                                                        product_id.id))
                inv_line_data = {
                    'name': product_id.name,
                    'account_id': income_account,
                    'price_unit': records.dongia,
                    'quantity': 1,
                    'product_id': product_id.id,
                    'invoice_id': inv_id.id,
                    'invoice_line_tax_ids':([(6,0,[tax.id for tax in product_id.taxes_id])])
                    
                }
                inv_line_obj.sudo().create(inv_line_data)
            
            inv_id.sudo().action_invoice_open()
            inv_id.sudo().invoice_validate()

            account_payment = self.env['account.payment']
            payment_method = self.env['account.payment.method'].sudo().search([('name','=','Manual')],limit=1)

            if self.payment_method=='cash' or self.payment_method=='bank' :
                journal_payment = self.env['account.journal'].sudo().search([('code','=', 'CSH1'),('company_id','=',company_id.id)], limit=1)
            
            # if self.payment_method=='bank':
            #     journal_payment = self.env['account.journal'].sudo().search([('code','=', 'BNK1'),('company_id','=',company_id.id)], limit=1)

            if journal_payment:
                journal_payment_id = journal_payment.id

            pay_vals = { 
                # 'product_id': product_id.id,
                'journal_id': journal_payment_id, 
                'amount':inv_id.amount_total, 
                'currency_id': inv_id.currency_id.id, 
                'payment_date': datetime.now().date(), 
                'communication': inv_id.name, 
                'payment_type':'outbound', 
                'payment_method_id': 1, 
                'partner_type': 'customer', 
                'partner_id': inv_id.partner_id.id,
                'destination_account_id':inv_id.account_id.id }
            payment_create = account_payment.sudo().create(pay_vals)
            payment_create.invoice_ids = [(4, inv_id.id)]
            validate = payment_create.with_context(destination_account_id=inv_id.account_id.id).sudo().post()
            inv_id.state = 'paid'
            
            return True
        

    

class DMDonbanveline(models.Model):
    _name = "dm.donbanve.line"
    _description = 'Danh sách chi tiết Bảng đơn bán vé'

    _sql_constraints = [
                     ('donbanveline_field_unique', 
                      'unique(dm_lichchieu_id, vitrighe)',
                      'Vé (ghế) đã có người đặt ')
        ]
    name = fields.Char('Mã Bảng đơn bán vé')
    dm_donbanve_id = fields.Many2one('dm.donbanve', 'Bảng đơn bán vé', ondelete='cascade', index=True)
    # dm_loaighe_id = fields.Many2one('dm.loaighe', 'Loại ghế ')
    # dm_loaive_id = fields.Many2one('dm.loaive', 'Loại vé ')
    # dm_thoigian_id = 
    loaighe = fields.Many2one('dm.loaighe', string="Loại ghế ")
    loaive = fields.Char("Loại vé ")
    phongchieu = fields.Char("Phòng chiếu ")
    rapphim = fields.Char("Rạp phim")
    tenphim = fields.Char("Tên phim")
    lichchieu = fields.Char("Lịch chiếu ")
    dm_banggia_id = fields.Many2one('dm.banggia', string='Bảng giá ')
    dm_lichchieu_id = fields.Many2one('dm.lichchieu', "Lịch chiếu")
    lichchieu_start = fields.Char("Lịch chiếu Bắt đầu ")
    lichchieu_end = fields.Char("Lịch chiếu kết thúc ")
    thungan = fields.Char("Thu ngân ")
    date_order = fields.Datetime(string='Ngày đặt vé', )
    
    vitrighe = fields.Char("Vị trí ghế ")
    dongia = fields.Float(string='Đơn giá', digits=dp.get_precision('Product Price'))
    soluong = fields.Float(string='Số lượng ', digits=dp.get_precision('Product Price'))
    thanhtien = fields.Float(string='Thành tiền ', digits=dp.get_precision('Product Price'))

    price = fields.Float(string='Price', digits=dp.get_precision('Product Price'))
    ngay = fields.Date("Ngày")
    macdinh = fields.Char("Mặc định")
    state = fields.Selection(
        related='dm_donbanve_id.state', string='Trạng thái đơn hàng', readonly=True, copy=False, store=True, default='draft')
    
    payment_method = fields.Selection(
        related='dm_donbanve_id.payment_method', readonly=True, copy=False, store=True, default='cash')

    ghichu = fields.Char('Ghi chú')
    sudung = fields.Boolean('Sử  dụng')
    price_total = fields.Float(compute='_compute_amount', string='Total', readonly=True, store=True)

    @api.depends('dm_session_line_id')
    def _compute_sophienbanve(self):
        for rec in self:
            rec.so_phien_ban_ve = rec.dm_session_line_id.id

    so_phien_ban_ve=fields.Integer(string='Số phiên bán vé', compute='_compute_sophienbanve', store=True)



    @api.depends('dongia', 'soluong')
    def _compute_amount(self):
        for rec in self:
            if rec.soluong and rec.dongia:
                rec.price_total = float(rec.soluong) * float(rec.dongia)
    
    @api.model
    def check_seat_exists(self, data):
        domain = [('dm_lichchieu_id','=', data.get('dm_lichchieu_id')),
                  ('vitrighe','=', data.get('vitrighe')) ]
        result = self.sudo().search(domain,limit=1)
        if result:
            return True
        else:
            return False

    
    # trả vé hoàn tiền
    @api.multi
    def line_trave_hoantien(self):
        if self.dm_donbanve_id.state =='done':
            inv_obj = self.env['account.invoice']
            inv_line_obj = self.env['account.invoice.line']
            # if self.partner_id:
            #     supplier = self.partner_id
            supplier = self.env['res.partner'].search([("name", "=", 'Khách vãng lai')],limit=1)

            # product_id = self.env['product.product'].search([("ticket", "=", True)],limit=1)
            # product_id = self.env['product.product'].search([("name", "=", 'Vé xem phim')],limit=1)
            product_id = self.env['product.product'].with_context(force_company=self.env.user.company_id.id).search([("name", "=", 'Vé xem phim')],limit=1)
            if product_id:
                company_id = product_id.company_id
            else: 
                company_id = self.env['res.users'].browse(1).company_id
            currency_salon = company_id.currency_id.id

            journal_id = ''
            journal = self.env['account.journal'].sudo().search([('code','=', 'HD'),('company_id','=',company_id.id)], limit=1)
            if journal:
                journal_id = journal.id
            
            inv_data = {
                # 'name': ,
                # 'reference': supplier.name,
                'type': 'in_invoice',
                'account_id': supplier.property_account_payable_id.id,
                'partner_id': supplier.id,
                'currency_id': currency_salon,
                'journal_id': journal_id,
                'origin': self.name,
                'company_id': company_id.id,
                
                # 'date_invoice': dm_lichchieu_id.ngaychieu,
                # 'state': 'paid',
            }
            inv_id = inv_obj.sudo().create(inv_data)
            self.invoice_number = inv_id
            
            if product_id.property_account_income_id.id:
                income_account = product_id.property_account_income_id.id
            elif product_id.categ_id.property_account_income_categ_id.id:
                income_account = product_id.categ_id.property_account_income_categ_id.id
            else:
                raise UserError(_('Please define income account for this product: "%s" (id:%d).') % (product_id.name,
                                                                                                    product_id.id))
            inv_line_data = {
                'name': product_id.name,
                'account_id': income_account,
                'price_unit': self.dongia,
                'quantity': 1,
                'product_id': product_id.id,
                'invoice_id': inv_id.id,
                'invoice_line_tax_ids':([(6,0,[tax.id for tax in product_id.taxes_id])])
                
            }
            inv_line_obj.sudo().create(inv_line_data)
            
            inv_id.sudo().action_invoice_open()
            inv_id.sudo().invoice_validate()

            account_payment = self.env['account.payment']
            payment_method = self.env['account.payment.method'].sudo().search([('name','=','Manual')],limit=1)

            # if self.payment_method=='cash' or if self.payment_method=='bank' :
            journal_payment = self.env['account.journal'].sudo().search([('code','=', 'CSH1'),('company_id','=',company_id.id)], limit=1)
            
            # if self.payment_method=='bank':
            #     journal_payment = self.env['account.journal'].sudo().search([('code','=', 'BNK1'),('company_id','=',company_id.id)], limit=1)

            if journal_payment:
                journal_payment_id = journal_payment.id

            pay_vals = { 
                # 'product_id': product_id.id,
                'journal_id': journal_payment_id, 
                'amount':inv_id.amount_total, 
                'currency_id': inv_id.currency_id.id, 
                'payment_date': datetime.now().date(), 
                'communication': inv_id.name, 
                'payment_type':'outbound', 
                'payment_method_id': 1, 
                'partner_type': 'customer', 
                'partner_id': inv_id.partner_id.id,
                'destination_account_id':inv_id.account_id.id }
            payment_create = account_payment.sudo().create(pay_vals)
            payment_create.invoice_ids = [(4, inv_id.id)]
            validate = payment_create.with_context(destination_account_id=inv_id.account_id.id).sudo().post()
            inv_id.state = 'paid'
            
            return True

