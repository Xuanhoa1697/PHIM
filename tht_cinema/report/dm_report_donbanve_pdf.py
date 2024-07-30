# -*- coding: utf-8 -*-
import locale
import time
from odoo import api, models
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT

class ReportPosSale(models.AbstractModel):
    _name = 'report.tht_cinema.dm_report_donbanve_pdf'

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
    
    def get_date_order(self, date):
        if date:
            date_tmp = datetime.strptime(date, DEFAULT_SERVER_DATETIME_FORMAT) + timedelta(hours=7)
            date_str = datetime.strftime(date_tmp, '%d/%m/%Y %I:%M:%S')
            date_p = datetime.strftime(date_tmp, '%p')
            pm = date_p == 'PM' and 'CH' or 'SA'
            return '%s %s'%(date_str, pm)
        return ''
    
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

    def get_category(self, o):
        category_list = []
        category_data = {}
        for line in o.detail_lines:
            # if not line.product_id:
            categ_id = line.categ_id and line.categ_id.name or ''
            if categ_id not in category_data: 
                category_data[categ_id] = {
                                        'qty': line.qty,
                                        'total_amount': line.total_amount,
                                        }
            else:
                category_data[categ_id]['qty'] += line.qty
                category_data[categ_id]['total_amount'] += line.total_amount
        for k,v in category_data.items():
            v.update({'category_name': k})
            category_list.append(v)
        return category_list
    
    def get_line(self, category, o):
        list_c = []
        for line in o.detail_lines:
            # if not line.product_id.bag_ok:
            categ_id = line.categ_id and line.categ_id.name or ''
            if categ_id != category: continue
            list_c.append({
                            'date': self.get_vietnam_date(line.date),
                            'product_id': line.product_id.name,
                            'product_barcode': line.product_id.barcode,
                            'price_unit': line.price_unit,
                            'total_amount': line.total_amount,
                            'qty': line.qty,
                            })
        return list_c
    
    @api.model
    def get_report_values(self, docids, data=None):
        docs = self.env['dm.report.donbanve'].browse(docids)
        return {
            'doc_ids': self.ids,
            'doc_model': 'dm.report.donbanve',
            'docs': docs,
            'time': time,
            'get_vietnam_date': self.get_vietnam_date,
            'get_date_order': self.get_date_order,
            'get_category': self.get_category,
            'get_line': self.get_line,
            'convert_to_money': self.convert_to_money,
        }
        