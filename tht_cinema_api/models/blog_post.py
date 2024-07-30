# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
from datetime import datetime
from odoo.exceptions import UserError, ValidationError, RedirectWarning


class WebsiteBlog(models.Model):
    _inherit = "blog.post"

    showinapp = fields.Boolean('Hiện trên app')

