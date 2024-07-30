import datetime
import json
import jwt
import odoo
from odoo import http
from odoo.http import Response, request, content_disposition, dispatch_rpc, request, \
                      serialize_exception as _serialize_exception
from datetime import datetime
import pytz
import re
import logging
import werkzeug

from odoo.addons.auth_signup.models.res_users import SignupError

_logger = logging.getLogger(__name__)

# databases = http.db_list()
db = False
# if databases:
#     db = databases[0]

# req_env = http.request.env
def errcode(code, message=None):
    return Response(success=False, code=code, message=message)

def response_500(message='Internal Server Error', data=None):
        return Response(success=False, message=message, data=data, code=500)

regex = r"^[a-z0-9!#$%&'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+\/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$"

def is_valid_email(email):
    return re.search(regex, email)
class CnmUserController(http.Controller):

    @http.route('/cnm/api/register', type='json', auth='public', csrf=False, methods=['POST'], cors='*')
    def cnm_api_register(self, email=None, name=None, password=None, **kw):
        # if kw.get('email', '') == '':
        #     return errcode(code=422, message='Email address cannot be empty')
        # if not is_valid_email(email):
        #     return errcode(code=422, message='Invalid email address')
        # if not name:
        #     return errcode(code=422, message='Name cannot be empty')
        # if not password:
        #     return errcode(code=422, message='Password cannot be empty')

        # sign up
        # values2 = {'name': kw.get('name'),
        #           'login': kw.get('email'),
        #           'phone': kw.get('phone'),
        #           'password': kw.get('password'),
        #           }
        # print('values2======', values2)
        
        data = request.jsonrequest
        try:
            self._signup_with_values(login=data['email'], name=data['name'], password=data['password'], phone=data['phone'], email=data['email'] )
        except AttributeError:
            return "errcode(code=501, message='Signup is disabled')"
        except (SignupError, AssertionError) as e:
            if request.env["res.users"].sudo().search([("login", "=", data['email'])]):
                return "errcode(code=422, message='Email address already existed')"
            else:
                return "response_500()"
        except Exception as e:
            _logger.error(str(e))
            return "response_500()"
        # log the user in
        # return do_login(email, password)
        return True
        
    @http.route('/cnm/api/user_update', type='json', auth="none", methods=['POST'], csrf=False)
    def cnm_api_user_update(self, debug=False, **kw):
        result = {}
        # email = kw.get('email', False)
        # password = kw.get('password', False)
        data = request.jsonrequest
        email = data['email']
        # password = data['password']
        uid = data['user_id']
        phone = data['phone']
        name = data['name']
        
        try:
            if db and db != request.db:
                raise Exception(_("Could not select database '%s'", db))
            
            res_users_obj = request.env['res.users'].sudo().search([('id', '=', uid)], limit=1)
            # res_partner_obj = request.env['res.partner'].sudo().search([('id', '=', res_users_obj.partner_id.id)], limit=1)
            res_partner_obj = request.env['res.partner'].sudo().browse(res_users_obj.partner_id.id)
            if phone!='' or name !='' or email !='':
                res_partner_obj.write({
                    'phone': phone,
                    'name': name,
                    'display_name': name,
                    'email': email,
                })
            result = {
                    'phone': phone,
                    'name': name,
                    'display_name': name,
                    'email': email,
                    'user_name': name
                }

        except:
            result.update({
                'status': 'error',
                'code': 401,
                'message': 'The authorization credentials provided for the request are invalid.',
                })
        
        return result
    # end update user

    @http.route('/cnm/api/user_delete', type='json', auth="none", methods=['POST'], csrf=False)
    def cnm_api_user_delete(self, debug=False, **kw):
        result = {}
        # email = kw.get('email', False)
        # password = kw.get('password', False)
        data = request.jsonrequest
        # password = data['password']
        uid = data['user_id']
        access_token = data['access_token']
        
        try:
            if db and db != request.db:
                raise Exception(_("Could not select database '%s'", db))
            domain = [('id', '=', uid)]
            domain_token = [('user_id', '=', uid), ('access_token', '=', access_token)]
            res_users_token_obj = request.env['res.user.token'].sudo().search(domain_token, limit=1000)
            if res_users_token_obj and len(res_users_token_obj) > 0:
                res_users_obj = request.env['res.users'].sudo().search(domain, limit=1)
                res_users_obj.sudo().unlink()
                

        except:
            result.update({
                'status': 'error',
                'code': 401,
                'message': 'The authorization credentials provided for the request are invalid.',
                })
        
        return 'Đã xoá tài khoản'
    # end delete user
    
    def _signup_with_values(self, **values):
        request.env['res.users'].sudo().signup(values, None)
        request.env.cr.commit()     # as authenticate will use its own cursor we need to commit the current transaction
        self.signup_email(values)


    def signup_email(self, values):
        user_sudo = request.env['res.users'].sudo().search([('login', '=', values.get('login'))])
        template = request.env.ref('auth_signup.mail_template_user_signup_account_created', raise_if_not_found=False)
        if user_sudo and template:
            template.sudo().with_context(
                lang=user_sudo.lang,
                auth_login=werkzeug.url_encode({'auth_login': user_sudo.email}),
            ).send_mail(user_sudo.id, force_send=True)
    
    @http.route('/cnm/api/get_token', type='json', auth="none", methods=['POST'], csrf=False)
    def cnm_api_get_token(self, debug=False, **kw):
        result = {}
        # email = kw.get('email', False)
        # password = kw.get('password', False)
        data = request.jsonrequest
        email = data['email']
        password = data['password']
        
        try:
            if db and db != request.db:
                raise Exception(_("Could not select database '%s'", db))
            uid = request.session.authenticate(request.db, email, password)
            user_id = request.env['res.users'].sudo().search([('id', '=', uid)])
            tz = user_id.tz
            partner_id = user_id.partner_id

            if uid:
                # role_name = request.env['base64.imageurl'].user_role()
                # print('role_name', role_name)
                token = jwt.encode({'uid': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}, 'secret', algorithm='HS256', headers={'uid': uid})
                
                if token:
                    result.update({
                    'status': True,
                    'user_mail': email, 
                    'user_name': user_id.name,
                    'user': user_id.name,
                    'user_id': uid,
                    'uid':uid, 
                    'access_token': token, 
                    'phone': partner_id.phone,
                    'message':'Logged in Successfully'})
                    request.env['res.user.token'].sudo().create({'user_id':uid, 'access_token':token, 'last_request':datetime.now(pytz.timezone(tz)).strftime("%Y-%m-%d %H:%M:%S") if tz else datetime.now(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")})
                    # request.env['rest.api.access.history'].sudo().create({'user_id':uid, 'origin':req_env['REMOTE_ADDR'], 'access_token':token, 'accessed_on':datetime.now(pytz.timezone(tz)).strftime("%Y-%m-%d %H:%M:%S") if tz else datetime.now(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")})
                else:
                    result.update({'token': 'Invalid Token'})
        except:
            result.update({
                'status': 'error',
                'code': 401,
                'message': 'The authorization credentials provided for the request are invalid.',
                })
        return result
    
    @http.route('/api/user/delete_token', type='json', auth="none", methods=['GET'], csrf=False)
    def delete_token(self, debug=False, **kw):
        result = {}
        token = False
        headers = dict(request.httprequest.headers.items())
        header = headers.get('Authorization', False)
        if header:
            token = header[7:]
        else:
            result.update({'status':False, 'message':'Invalid Token'})
            return json.dumps(result)
        user_id = request.env['res.user.token'].sudo().search([('access_token', '=', token)], limit=1).user_id
        if token:
            record = request.env['res.user.token'].sudo().search([('access_token', '=', token)], limit=1)
            if record:
                request.env['rest.api.access.history'].sudo().create({'user_id':user_id.id, 'origin':req_env['REMOTE_ADDR'], 'access_token':token, 'accessed_on':datetime.now(pytz.timezone(user_id.tz)).strftime("%Y-%m-%d %H:%M:%S") if user_id.tz else datetime.now(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")})
                record = record.sudo().unlink()
                result.update({'status':record, 'message':"Logged out successfully"})
            else:
                result.update({'status':False, 'message':"Record Not Found!"})
        else:
            result.update({'status':False, 'message':"Token Not Found!"})
        return result

