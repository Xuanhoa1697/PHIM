# -*- coding: utf-8 -*-

import json
import base64
from werkzeug import redirect

from odoo import fields, http, api
from odoo.http import request, Response
from odoo import tools
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import AccessError, UserError
from odoo.tools import html_escape
from werkzeug import exceptions

import pytz
import json
import datetime
from dateutil.relativedelta import relativedelta


def _check_token():
    try:
        http_authorization = request.httprequest.environ['HTTP_AUTHORIZATION']
    except:
        result = {
            'status': 'error',
            'code': 400,
            'message': 'The request failed because it contained an invalid value. The value could be a parameter value, a header value, or a property value.',
        }
        exceptions.abort(Response(json.dumps(result), content_type='application/json;charset=utf-8', status=401))
    access_token_prefix, access_token = http_authorization[:7], http_authorization[7:]
    if access_token_prefix.strip().lower() == 'bearer':
        token_id = request.env['res.user.token'].sudo().search([('access_token','=', access_token)], limit=1)
        if token_id:
            uid = token_id.user_id.id or False
            request._uid = uid
            request.session.context.update({'access_token':access_token})
#             request._env = api.Environment(request.cr, uid, request.session.context or {})
# #             token_id.write({'last_request':_get_last_login(uid)})
#             ICPSudo = request.env['ir.config_parameter'].sudo()
#             traceability = ICPSudo.get_param('hgp_base.api_access_history', False)
#             if traceability == '1.0':
#                 request.env['rest.api.access.history'].sudo().create({'user_id':uid,'origin':request.httprequest.environ['REMOTE_ADDR'],'api_path':request.context.get('api_path',False),'access_token':access_token,'accessed_on':_get_last_login(uid)})
        else:
            result = {
                'status': 'error',
                'code': 401,
                'message': 'The user is not authorized to make the request.',
            }
            exceptions.abort(Response(json.dumps(result), content_type='application/json;charset=utf-8', status=401))
    else:
        result = {
            'status': 'error',
            'code': 400,
            'message': 'The request failed because it contained an invalid value. The value could be a parameter value, a header value, or a property value.',
        }
        exceptions.abort(Response(json.dumps(result), content_type='application/json;charset=utf-8', status=401))