# -*- coding: utf-8 -*-
from odoo import api, models
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
import locale

from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime, timedelta, date

class DmReportKqcpDetailXlsx(models.AbstractModel):
    _name = 'report.tht_cinema.dm_report_kqcp_detail_xlsx'   
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
            sheet.write(4, 1, u'', title_date_style)
            # sheet.write(4, 2, obj.user_id.name, dvt_style )
            sheet.write(4, 2, '', dvt_style )
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
                        sheet.write(y_offset, x, line_c['qty'], body_categ_style)
                    elif x == 4:
                        sheet.write(y_offset, x, self.convert_to_money(line_c['total_amount'], 'VND'), body_categ_style)
                sheet.set_row(y_offset, 18)
                y_offset += 1
                lines = self.get_line(line_c['category_name'], obj)
                for y in range(0, len(lines)):
                    line = lines[y].get('colums', [])
                    for x in range(0, len(line)):
                        sheet.write(y_offset, x, line[x], body_center_style)
                    y_offset += 1
            sheet.write(y_offset, 3, u'Tổng cộng: ', title_date_style)
            # sheet.write(y_offset, 4, self.convert_to_money(obj.total_amount/1000, 'VND'), body_center_style)      
            sheet.write(y_offset, 4, self.convert_to_money(obj.total_amount, 'VND'), body_center_style)      
            
    
    def get_columns_name(self):
        return [u'', u'Ngày', u'Tên phim', u'Phòng', u'SL', u'Giá', u'Thành tiền']
            
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
        category_list = []
        category_data = {}
        for line in o.detail_lines:
            # if not line.product_id.bag_ok:
            if 1==1:
                dm_lichchieu_id = line.dm_lichchieu_id and line.dm_lichchieu_id.name or ''
                if dm_lichchieu_id not in category_data: 
                    category_data[dm_lichchieu_id] = {
                                            'qty': line.qty,
                                            'total_amount': line.total_amount,
                                            }
                else:
                    category_data[dm_lichchieu_id]['qty'] += line.qty
                    category_data[dm_lichchieu_id]['total_amount'] += line.total_amount
        for k,v in category_data.items():
            v.update({'category_name': k})
            category_list.append(v)
        return category_list
    
    def get_line(self, category, o):
        list_c = []
        for line in o.detail_lines:
            # if not line.product_id.bag_ok:
            dm_lichchieu_id = line.dm_lichchieu_id and line.dm_lichchieu_id.name or ''
            if dm_lichchieu_id != category: continue
            ngay = (datetime.strptime(line.ngay, DEFAULT_SERVER_DATETIME_FORMAT) + timedelta(hours=7)).strftime('%d/%m/%Y %H:%M:%S')
            # list_c.append({'colums':[line.product_id.barcode or '', line.product_id.name, line.qty, self.convert_to_money(line.price_unit/1000, 'VND'), self.convert_to_money(line.total_amount/1000, 'VND')]})
            list_c.append({
                'colums':[line.product_id.barcode or '', 
                ngay, 
                line.tenphim, 
                line.phong,
                line.qty, 
                self.convert_to_money(line.price_unit, 'VND'), 
                self.convert_to_money(line.total_amount, 'VND')]})
        return list_c
    
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
    