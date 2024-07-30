import json
import urllib
import uuid
import hmac
import hashlib
import requests

from odoo import tools



def CreateOrderByMomo(dbh_info, user_id):
    api_domain = 'https://'+tools.config.get('api_domain')
    endpoint = 'https://'+tools.config.get('momo_endpoint')
    partnerCode = tools.config.get('momo_partnercode')
    accessKey = tools.config.get('momo_accesskey')
    secretKey = tools.config.get('momo_secretkey')
    # https://test-payment.momo.vn/gw_payment/transactionProcessor
    # endpoint = "https://test-payment.momo.vn/gw_payment/transactionProcessor"
    redirectUrl = api_domain+"/cnm/web/momo/result" 
    # redirectUrl = "https://ajin05.ddns.net/cnm/web/momo/notify" 
    # + dbh_info['orderInfo']
    ipnUrl = api_domain+"cnm/web/momo/result"

    endpoint +="/v2/gateway/api/create"
    partnerCode = partnerCode #"MOMOEQ4F20201024"  # busssiness momo
    accessKey = accessKey #"6UJmuB7yc8rrMah4"  # busssiness momo
    secretKey = secretKey
    
    orderInfo = dbh_info['orderInfo']  # thông tin về order
    # returnUrl = "https://test.tien.info:8080/cnm/web/momo/result"  # redicrect sau đi hoàn tất thanh toán
    # notifyUrl = "https://test.tien.info:8080/cnm/web/momo/notify"
    amount = str(dbh_info['amount'])  # Số tiền của hóa đơn
    orderId = 'tgc_' + str(uuid.uuid4())  # order id của momo chứ ko phải của chúng ta
    requestId = 'tgc_' + str(uuid.uuid4())  # như trên
    requestType = "captureWallet"
    extraData = "merchantName=;merchantId="

    rawSignature = "accessKey=" + accessKey + "&amount=" + str(amount) + "&extraData=" + extraData + \
                   "&ipnUrl=" + ipnUrl + "&orderId=" + orderId + "&orderInfo=" + orderInfo + \
                   "&partnerCode=" + partnerCode + "&redirectUrl=" + redirectUrl + "&requestId=" + \
                   requestId + "&requestType=" + requestType
    
    h = hmac.new(bytes(secretKey, 'utf-8'), bytes(rawSignature, 'utf-8'), hashlib.sha256)
    
    signature = h.hexdigest()

    data = {
        
        'storeId': "MomoTestStore",
        'partnerCode': partnerCode,
        'accessKey': accessKey,
        'requestId': requestId,
        'amount': amount,
        'orderId': orderId,
        'orderInfo': orderInfo,
        # 'returnUrl': returnUrl,
        # 'notifyUrl': notifyUrl,
        'extraData': extraData,
        'requestType': requestType,
        'signature': signature,
        'redirectUrl': redirectUrl,

        
        "ipnUrl": ipnUrl,
        "lang": "vi",
        "userInfo": {
            "name": "Nguyen Van A",
            "phoneNumber": "0999888999",
            "email": "email_add@domain.com",
        }
    }
    data = json.dumps(data)
    clen = len(data)
    
    # f = urllib.request.urlopen(req)
    # response = f.read()
    response = requests.post(endpoint, data=data, headers={'Content-Type': 'application/json', 'Content-Length': str(clen)})
    if response.json()['resultCode'] != 0:
        return ''
    
    result = {
        'user_id': user_id,
        'amount': amount,
        'orderInfo': orderInfo,
        'orderId': orderId,
        'requestId': requestId,
        'signature': signature,
        'req_momo': data, 
        'res_momo': response.json()} 
    return result

    # return response.json()

    



