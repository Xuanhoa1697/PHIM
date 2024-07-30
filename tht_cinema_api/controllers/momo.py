import json
import urllib
import uuid
import hmac
import hashlib
import requests

from odoo import tools

# partnerCode = "MOMONMDT20210318" #"MOMOEQ4F20201024"  # busssiness momo
# accessKey = "NstaKID2zXK7dlVK" #"6UJmuB7yc8rrMah4"  # busssiness momo
# secretKey = "5V1KJ8DMQyJ0HH6goeAhcdHAcv2Orl0Y" #"0S9J1b5u1eJtTUFEOVlYxOkIMmrQW70c"  # 

def CreateOrderByMomo(dbh_info, user_id):
    api_domain = 'https://'+tools.config.get('api_domain')
    endpoint = 'https://'+tools.config.get('momo_endpoint')
    partnerCode = tools.config.get('momo_partnercode')
    accessKey = tools.config.get('momo_accesskey')
    secretKey = tools.config.get('momo_secretkey')
    
    print(23, api_domain, endpoint, partnerCode, accessKey, secretKey )
    result = {'req_data': {}, 'res_data': {}} 
    endpoint += "/v2/gateway/api/create"
    

    # busssiness momo
    orderInfo = dbh_info['orderInfo']  # thông tin về order
    # redirectUrl = "https://test.tien.info:8080/cnm/web/momo/notify"
    redirectUrl = "thtcinema://home/resultpayment?orderName=" + dbh_info['orderInfo']
    # returnUrl = "thtcinema://home/resultpayment?orderName=" + dbh_info['orderInfo']  # redicrect sau đi hoàn tất thanh toán
    # notifyUrl = "https://ajin05.ddns.net/cnm/web/momo/notify"
    # ipnUrl = "https://ajin05.ddns.net/cnm/web/momo/result"
    ipnUrl = "https://thegoldcinema.com/cnm/app/momo/result"
    amount = str(dbh_info['amount'])  # Số tiền của hóa đơn
    orderId = 'tgc_' + str(uuid.uuid4())  # order id của momo chứ ko phải của chúng ta
    requestId = 'tgc_' + str(uuid.uuid4())  # như trên
    requestType = "captureWallet"
    extraData = "merchantName=;merchantId="

    # rawSignature = "accessKey=" + accessKey + "&amount=" + amount + "&extraData=" + extraData + "&ipnUrl=" + ipnUrl + "&orderId=" + orderId + "&orderInfo=" + orderInfo + "&partnerCode=" + partnerCode + "&redirectUrl=" + redirectUrl + "&requestId=" + requestId + "&requestType=" + requestType


    rawSignature = "accessKey=" + accessKey + "&amount=" + str(amount) + "&extraData=" + extraData + \
                   "&ipnUrl=" + ipnUrl + "&orderId=" + orderId + "&orderInfo=" + orderInfo + \
                   "&partnerCode=" + partnerCode + "&redirectUrl=" + redirectUrl + "&requestId=" + \
                   requestId + "&requestType=" + requestType
    
    h = hmac.new(bytes(secretKey, 'utf-8'), bytes(rawSignature, 'utf-8'), hashlib.sha256)
    signature = h.hexdigest()

    

    data = {
        "storeId" : "",
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
        "extraData": extraData,

        "ipnUrl": ipnUrl,
        "lang": "vi"
    }
    data = json.dumps(data)
    clen = len(data)
                            
    response = requests.post(endpoint, data=data, headers={'Content-Type': 'application/json', 'Content-Length': str(clen)})

    result = {
        'amount': amount,
        'user_id': user_id,
        'orderInfo': orderInfo,
        'orderId': orderId,
        'requestId': requestId,
        'signature': signature,
        'req_momo': data, 
        'res_momo': response.json()} 
    return result


def momo_query(order_id, request_id):
    api_domain = 'https://'+tools.config.get('api_domain')
    endpoint = 'https://'+tools.config.get('momo_endpoint')
    partnerCode = tools.config.get('momo_partnercode')
    accessKey = tools.config.get('momo_accesskey')
    secretKey = tools.config.get('momo_secretkey')

    endpoint += "/v2/gateway/api/query"
    orderId = order_id
    requestId = request_id

    rawSignature = "accessKey=" + accessKey + "&orderId=" + orderId + "&partnerCode=" + partnerCode + "&requestId=" + requestId
    h = hmac.new(bytes(secretKey, 'utf-8'), bytes(rawSignature, 'utf-8'), hashlib.sha256)
    signature = h.hexdigest()

    data = {
        'partnerCode': partnerCode,
        'requestId': requestId,
        'orderId': orderId,
        'lang': "vi",
        'signature': signature
    }

    loaded_data = json.dumps(data)
    clen = len(data)
    response = requests.post(endpoint, data=loaded_data,
                             headers={'Content-Type': 'application/json', 'Content-Length': str(clen)})
    return response.json()