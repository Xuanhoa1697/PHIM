#-*- coding: utf-8 -*-
from odoo import http
from odoo.http import request, Response, JsonRequest
# import os
# import json
import qrcode
import io
import time
import base64

# with open(BASE_DIR+'MyQRCode2.png', "wb") as f:
#     f.write(buffer.getvalue())

class ApiQrcode(http.Controller):
    
    # /api/qrcode?text=abc
    # /api/qrcode?text=abc&type=png
    @http.route('/api/qrcode', auth='public', website=True)
    def query(self, **kw):
        img_base64 = ''
        text = kw.get('text', '')
        type = kw.get('type', '')
        if text == '':
            return 'none text '
        
        img = qrcode.make(text)
        begin = time.time()
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        
        end = time.time()
        seconds = end - begin
        img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        if text !='' and type == 'png':
            headers = {'Content-Type': 'application/json'}
            filename = f'inline; filename={text[0:50]}.png'
            return request.make_response(buffer.getvalue(),
                [('Content-Type', 'application/png'),
                ('Content-Disposition', filename)])
            
        return 'data:image/png;base64,'+ img_base64

