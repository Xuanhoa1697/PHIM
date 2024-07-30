# -*- coding: utf-8 -*-
# user login from web
import logging
from itertools import chain
from odoo.http import request
from odoo import models, fields, api

class DonbanveMomo(models.Model):
    _inherit = 'dm.donbanve'

    # momo_orderid = fields.Char(string='Momo Order ID')
    # momo_sign = fields.Char(string='Momo Sign')

class LoginUpdate(models.Model):
    _name = 'dm.momo.response'
    _order = 'create_date desc'
    
    momo_orderid = fields.Char(string='Momo order id')
    response_string = fields.Char('NotifyUrl Response String')