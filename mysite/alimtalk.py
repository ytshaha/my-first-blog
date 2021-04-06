import base64
import hashlib
import hmac
import time
import requests
import json
# from filters import *


NCLOUD_API_ACCESS_KEY_ID = '5qPLEqntCjWKDBE8IHOF'
NCLOUD_API_SECRET_KEY = '28iAXjOb5JmnCp9m0I42BgCnVoAhlAGsZlrzzLm3'

def send(booking):
    url = "https://sens.apigw.ntruss.com"
    uri = "/alimtalk/v2/services/" + NCLOUD_API_ACCESS_KEY_ID + "/messages"
    api_url = url + uri
    timestamp = str(int(time.time() * 1000))
    access_key = NCLOUD_API_ACCESS_KEY_ID
    string_to_sign = "POST " + uri + "\n" + timestamp + "\n" + access_key
    signature = make_signature(string_to_sign)

    # 예약내역 불러와서 변환
    # phone = booking['phone'].replace("-", "")
    # name = booking['name']
    # booking_date = format_datetime(booking['date'])

    message = "테스트 알림톡: {}".format('호호')

    headers = {
        'Content-Type': "application/json; charset=UTF-8",
        'x-ncp-apigw-timestamp': timestamp,
        'x-ncp-iam-access-key': access_key,
        'x-ncp-apigw-signature-v2': signature
    }

    # body = {
    #     "type": "SMS",
    #     "contentType": "COMM",
    #     "from": "발신자번호",
    #     "content": message,
    #     "messages": [{"to": phone}]
    }
    body = {
    "plusFriendId":"moum8",
    "templateCode":"register",
    "messages":[
        {
            # "countryCode":"string",
            "to":"01079299901", #  수신자번호
            # "title":"string", # 
            "content":message, #알림톡 메세지 내용
            # "buttons":[
            #     {
            #         "type":"string",
            #         "name":"string",
            #         "linkMobile":"string",
            #         "linkPc":"string",
            #         "schemeIos":"string",
            #         "schemeAndroid":"string"
            #     }
            # ],
            # "useSmsFailover": "boolean",
            # "failoverConfig": {
            #     "type": "string",
            #     "from": "string",
            #     "subject": "string",
            #     "content": "string"
            # }
        }
    ],
}

    body = json.dumps(body)

    response = requests.post(api_url, headers=headers, data=body)
    response.raise_for_status()


def make_signature(string):
    secret_key = bytes(NCLOUD_API_ACCESS_KEY_ID, 'UTF-8')
    string = bytes(string, 'UTF-8')
    string_hmac = hmac.new(secret_key, string, digestmod=hashlib.sha256).digest()
    string_base64 = base64.b64encode(string_hmac).decode('UTF-8')
    return string_base64