# -*- coding: utf-8 -*-
from odoo import api, models
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
import locale

from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime, timedelta, date

class DmReportbcnbDetailXlsx(models.AbstractModel):
    _name = 'report.tht_cinema.dm_report_bcnb_detail_xlsx'   
    _inherit = 'report.report_xlsx.abstract'
    
    def generate_xlsx_report(self, workbook, data, details):
        for obj in details:
            
            report_name = "RpSheet"+str(obj.id)
            # sheet = workbook.add_worksheet(report_name[:31])
            sheet = workbook.add_worksheet(report_name)
            title_style = workbook.add_format({'font_name': 'Times New Roman', 'bold': True, 'color': '#274675', 'align': 'center', 'font_size': 26, 'valign':'vcenter'})
            title_date_style = workbook.add_format({'font_name': 'Times New Roman', 'bold': True, 'color': '#274675', 'font_size': 12, 'valign':'vcenter'})
            title_table_style = workbook.add_format({'font_name': 'Times New Roman', 'bold': True, 'color': '#274675', 'font_size': 12, 'align': 'center', 'valign':'vcenter'})
            body_style = workbook.add_format({'font_name': 'Times New Roman', 'font_size': 12})
            dvt_style = workbook.add_format({'font_name': 'Times New Roman', 'font_size': 12, 'align': 'right'})
            body_center_style = workbook.add_format({'font_name': 'Times New Roman', 'font_size': 12, 'align': 'center'})
            categ_style = workbook.add_format({'font_name': 'Times New Roman', 'font_size': 13, 'bold': True, 'underline': True})
            body_categ_style = workbook.add_format({'font_name': 'Times New Roman', 'font_size': 12, 'color': 'red', 'align': 'left', 'underline': True})
            sheet.set_column(0,0,17)
            sheet.set_column(1,1,50)
            sheet.set_column(2,3,12)
            sheet.set_column(4,4,15)
            sheet.set_row(0, 20)
            dm_diadiem_id = obj.dm_diadiem_id and obj.dm_diadiem_id.name or ''
            title_str = obj.type == 'sale' and  u'Báo Cáo Bán Vé ' + dm_diadiem_id or u'Báo Cáo Nhập Đổi ' + dm_diadiem_id
            sheet.merge_range(0, 0, 1, 4, title_str, title_style)
            sheet.write(2, 1, u'Từ ngày', title_date_style)
            sheet.write(2, 2, self.get_vietnam_date(obj.date_from), body_style)
            sheet.write(2, 3, u'Đến ngày', title_date_style)
            sheet.write(2, 4, self.get_vietnam_date(obj.date_to), body_style)
            sheet.write(3, 1, u'Tổng TT', title_date_style)
            # sheet.write(3, 2, self.convert_to_money(obj.total_amount/1000, 'VND'), body_style)
            sheet.write(3, 2, self.convert_to_money(obj.total_amount, 'VND'), body_style)
            sheet.write(3, 3, u'Tổng SL', title_date_style)
            sheet.write(4, 1, u'Nhân viên bán vé', title_date_style)
            sheet.write(4, 2, obj.user_id.name, dvt_style )
            sheet.write(5, 1, u'Phiên bán vé', title_date_style)
            sheet.write(5, 2, obj.phienbanve, dvt_style )
            # sheet.write(4, 2, '', dvt_style )
            sheet.write(3, 4, str(int(obj.total_qty)), body_style)
            sheet.write(5, 4, u'ĐVT: đ', dvt_style)
            y_offset = 6
            x = 0
            columns = self.get_columns_name()
            number_colum = len(columns)
            for column in columns:
                sheet.write(y_offset, x, column, title_table_style)
                x += 1
            y_offset += 1

            line_categories = self.get_category(obj)
            for line_c in line_categories:
                for x in range(0, number_colum):
                    if x == 0:
                        pass
                        # sheet.merge_range(y_offset, x, y_offset, x + 1, line_c['category_name'], categ_style)
                    elif x == 3:
                        pass
                        # p_val = f'Phim: {line_c.tenphim} ( Suất: 14, Ghế: 1758 Vé: 887, DT: 68.235.000)'
                        # sheet.write(y_offset, x, line_c['qty'], body_categ_style)
                    # elif x == 4:
                    #     sheet.write(y_offset, x, self.convert_to_money(line_c['total_amount'], 'VND'), body_categ_style)
                n_row_tonghop = y_offset
                sheet.set_row(y_offset, 22)
                
                y_offset += 1
                lines = self.get_line(line_c['dm_phim_id'], obj)
                
                
                lc_tongsoghe = 0
                lc_tongsoveban = 0
                for k, v in lines.items():
                    line = v['lc_info']
                    dongia_list = v['dongia_list']
                    lc_tongsoghe = lc_tongsoghe + line[5]
                    for x in range(0, len(v['lc_info'])):
                        if x != 8:
                            sheet.write(y_offset, x, line[x], body_center_style)
                        if x == 8:
                            pass
                            # sheet.write(y_offset, 16, line[x], body_center_style)

                    # columns_price = [0, 45000,50000,55000,60000,70000,80000,85000,95000]
                    columns_price = [0,45000,50000,55000,60000,65000,70000,75000,80000,85000,90000,95000,105000]

                    for price_index in range(0, len(columns_price)):
                        sheet.write(y_offset, 8 + price_index , 0 , body_center_style)

                    thanhtien = 0
                    tongsoveban = 0
                    for dg_index in range(0, len(dongia_list)) :
                        # chen đơn giá
                        column_num = 8
                        cell_qty = dongia_list[dg_index]['qty']
                        cell_price_unit = dongia_list[dg_index]['price_unit']

                        if cell_price_unit in columns_price :
                            column_num = column_num + columns_price.index(cell_price_unit)
                            sheet.write(y_offset, column_num, cell_qty or 0, body_center_style)
                            thanhtien = thanhtien + cell_qty * cell_price_unit
                            tongsoveban = tongsoveban + cell_qty
                    sheet.write(y_offset, 6, tongsoveban, body_center_style)
                    soghetrongphong = v['soghe']
                    occ_val = "{:.2f}".format(tongsoveban/soghetrongphong*100) 
                    sheet.write(y_offset, 7, occ_val, body_center_style)
                    sheet.write(y_offset, 21, thanhtien, body_center_style)

                    lc_tongsoveban = lc_tongsoveban + tongsoveban
                    
                    y_offset += 1
                
                
                tongthu = line_c['total_amount']
                p_tenphim = line_c['tenphim']
                if lc_tongsoghe > 0:
                    p_occ_val = "{:.2f}".format(lc_tongsoveban/lc_tongsoghe*100) 
                else: 
                    p_occ_val = 0
                p_val = f'Phim: {p_tenphim} ( Suất: {len(lines)}, Ghế: {lc_tongsoghe} Vé: {lc_tongsoveban}, OCC: {p_occ_val}, DT: {tongthu} )'
                
                sheet.write(n_row_tonghop, 1, p_val, body_categ_style)
               
            sheet.write(y_offset, 3, u'Tổng cộng: ', title_date_style)
            # sheet.write(y_offset, 4, self.convert_to_money(obj.total_amount/1000, 'VND'), body_center_style)      
            sheet.write(y_offset, 4, self.convert_to_money(obj.total_amount, 'VND'), body_center_style)      
            
    
    def get_columns_name(self):
        # 65k 75k 90k 105k
        giave = ['Giá vé 0 (Miễn phí)', "Giá vé 45,000", "Giá vé 50,000", "Giá vé 55,000", "Giá vé 60,000", "Giá vé 65,000", "Giá vé 70,000", "Giá vé 75,000", 'Giá vé 80,000', 'Giá vé 85,000', "Giá vé 90,000" , "Giá vé 95,000" , "Giá vé 105,000" , u'Thành tiền']
        return [u'Ngày', u'Tên phim','Nhà phát hành', 'Suất chiếu', u'Phòng', 'Số ghế',  'Tổng số vé', u'OCC(%)' ] + giave
    def get_vietnam_date(self, date):
        if date:
            try:
                date_tmp = datetime.strptime(date, DEFAULT_SERVER_DATETIME_FORMAT) + timedelta(hours=7)
            except:
                date_tmp = datetime.strptime(date, DEFAULT_SERVER_DATE_FORMAT)
            day = str(date_tmp.day).zfill(2)
            month = str(date_tmp.month).zfill(2)
            year = str(date_tmp.year).zfill(4)
            return '%s/%s/%s' % (day, month, year)
        return ''
    

    
    def get_category(self, o):
        # import pdb; pdb.set_trace()
        category_list = []
        category_data = {}
        for line in o.detail_lines:
            # if not line.product_id.bag_ok:
            if 1==1:
                dm_phim_id = line.dm_phim_id.id or ''
                if dm_phim_id not in category_data: 
                    category_data[dm_phim_id] = {
                                            'qty': line.qty,
                                            'tenphim': line.tenphim,
                                            'total_amount': line.total_amount,
                                            }
                else:
                    category_data[dm_phim_id]['qty'] += line.qty
                    category_data[dm_phim_id]['total_amount'] += line.total_amount
        for k,v in category_data.items():
            v.update({'dm_phim_id': k})
            category_list.append(v)
        return category_list
    
    def get_line(self, category, o):
        lc_group_list = []
        lc_group = {}
        list_c = []
        ii = 0
        for line in o.detail_lines:
            # dm_phim_id = line.dm_phim_id or ''
            if line.dm_phim_id.id != category: continue
            # ngay = (datetime.strptime(line.ngay, DEFAULT_SERVER_DATETIME_FORMAT) + timedelta(hours=7)).strftime('%d/%m/%Y %H:%M:%S')
            ngay = (datetime.strptime(line.ngay, DEFAULT_SERVER_DATETIME_FORMAT) + timedelta(hours=7)).strftime('%d/%m/%Y')
            suatchieu = (datetime.strptime(line.suatchieu, DEFAULT_SERVER_DATETIME_FORMAT) + timedelta(hours=7)).strftime('%H:%M:%S')
            lc_info = [
                ngay, 
                line.tenphim, 
                line.nhaphathanh,
                suatchieu,
                line.phong,
                line.soghe,
                line.tongsove, 
                'occ',
                # self.convert_to_money(line.price_unit, 'VND'), 
                self.convert_to_money(line.total_amount, 'VND') 
                ]


            lc_id = line.dm_lichchieu_id.id
            if lc_id not in lc_group:
                lc_group[lc_id] = {
                    'soghe': line.soghe,
                    'lc_info': lc_info,
                    'dongia_list': [{ 
                        'dm_lichchieu_id': line.dm_lichchieu_id.id,
                        'price_unit': line.price_unit,
                        'qty': line.qty,
                        # 'tenphim': line.tenphim,
                        }]
                }
                
            else:
                lc_group[lc_id]['dongia_list'].append({
                    'dm_lichchieu_id': line.dm_lichchieu_id.id,
                    'price_unit': line.price_unit,
                    'qty': line.qty,
                    # 'tenphim': line.tenphim,
                })

            # if not line.product_id.bag_ok:
            # dm_phim_id = line.dm_phim_id and line.dm_phim_id.id or ''
            # if dm_phim_id != category: continue
            # ngay = (datetime.strptime(line.ngay, DEFAULT_SERVER_DATETIME_FORMAT) + timedelta(hours=7)).strftime('%d/%m/%Y %H:%M:%S')
            # list_c.append({'colums':[line.product_id.barcode or '', line.product_id.name, line.qty, self.convert_to_money(line.price_unit/1000, 'VND'), self.convert_to_money(line.total_amount/1000, 'VND')]})
            # list_c.append({
            #     'colums':[line.product_id.barcode or '', 
            #     ngay, 
            #     line.tenphim, 
            #     line.phong,
            #     line.qty, 
            #     self.convert_to_money(line.price_unit, 'VND'), 
            #     self.convert_to_money(line.total_amount, 'VND')]})
        
        
        return lc_group
    
    def convert_to_money(self, number, currency):
        if currency == 'USD':
            locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        elif currency == 'VND':
            str = '{:20,.2f}'.format(number)
            str_list = str.split('.')
            if str_list and int(str_list[1]) == 0:
                str = str_list[0]
            return u'%s'%str.strip()
        else:
            locale.setlocale(locale.LC_ALL, '')
        return locale.currency( number, grouping=True )
    

    def convert_datetime_field(datetime_field, user=None):
        dt = datetime.strptime(datetime_field, '%Y-%m-%d %H:%M:%S')
        if user and user.tz:
            user_tz = user.tz
            if user_tz in pytz.all_timezones:
                old_tz = pytz.timezone('UTC')
                new_tz = pytz.timezone(user_tz)
                dt = old_tz.localize(dt).astimezone(new_tz)
            else:
                _logger.info("Unknown timezone {}".format(user_tz))

        return datetime.strftime(dt, '%d/%m/%Y %H:%M:%S')
    