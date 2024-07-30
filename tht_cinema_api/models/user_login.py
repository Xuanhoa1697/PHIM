# -*- coding: utf-8 -*-
# user login from web
import logging
from itertools import chain
from odoo.http import request
from odoo import models, fields, api

_logger = logging.getLogger(__name__)
USER_PRIVATE_FIELDS = ['password']
concat = chain.from_iterable

class LoginUpdate(models.Model):
    _name = 'dm.user.booking'

    name = fields.Char(string="User Name")
    user_id = fields.Many2one('res.users')
    date_time = fields.Datetime(string="Login Date And Time", default=lambda self: fields.datetime.now())
    ip_address = fields.Char(string="IP Address")
