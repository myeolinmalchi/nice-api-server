import json
import requests
import hmac

import random
import hashlib

from datetime import datetime, timedelta
import time

import hashlib
import base64

from app.AESCipher import AESCipher
from app.config import *

def get_req_no() -> str:
    '''요청 고유번호 생성'''
    random_number = random.randint(0, 0xFFFFFFFF)  # Equivalent to PHP's mt_rand()
    md5_hash = hashlib.md5(str(random_number).encode()).hexdigest().upper()
    req_no = ("pc" + md5_hash)[:12]
    return req_no

def hmac256(key: bytes, message: bytes) -> bytes:
    try:
        hmac_object = hmac.new(key, message, digestmod='SHA256')
        hmac256 = hmac_object.digest()
        return hmac256
    except Exception as e:
        raise RuntimeError("Failed to generate HMACSHA256 encrypt") from e

def encrypt_request_data(returnurl: str) -> dict[str, dict]:
    '''요청 데이터를 암호화하여 키와 함께 반환한다.'''

    now = datetime.now()
    timestamp = int(time.mktime(now.timetuple()))
    _auth = f"{ACCESS_TOKEN}:{timestamp}:{NICE_CLIENT_ID}"

    auth = base64.b64encode(_auth.encode('utf-8')).decode('utf-8')

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"bearer {auth}",
        "client_id": NICE_CLIENT_ID,
        "ProductID": NICE_PRODUCT_ID
    }

    x = datetime.now()
    req_dtim = f"{x.year}{x.month:02d}{x.day:02d}{x.hour:02d}{x.minute:02d}{x.second:02d}"
    req_no = get_req_no()
    enc_mode = "1"

    # 암호화 토큰 발급 요청
    res = requests.post(
        f"{NICE_API_URL}/digital/niceid/api/v1.0/common/crypto/token",
        headers=headers,
        json={
            "dataHeader": {"CNTY_CD": "ko"},
            "dataBody": {
                "req_dtim": req_dtim,
                "req_no": req_no,
                "enc_mode": enc_mode
            }
        }
    )

    res.raise_for_status()

    body = res.json()

    dataHeader = body['dataHeader']

    if dataHeader['GW_RSLT_CD'] != '1200':
        raise Exception(dataHeader['GW_RSLT_MSG'])


    dataBody = body['dataBody']

    if dataBody['rsp_cd'] != 'P000':
        raise Exception('정상적으로 처리하지 못했습니다.')

    if dataBody['result_cd'] != '0000':
        raise Exception('토큰 발급에 실패했습니다.')

    now = datetime.now()
    timestamp = int(time.mktime(now.timetuple()))

    token_val: str = dataBody['token_val']

    value = (req_dtim.strip() + req_no.strip() + token_val.strip()).encode('utf-8')
    md = hashlib.sha256()
    md.update(value)
    arrHashValue = md.digest()
    resultVal = base64.b64encode(arrHashValue).decode("utf-8")


    key = resultVal[:16]
    iv = resultVal[-16:]
    hmac_key = resultVal[:32]

    # 요청 데이터 암호화
    # 암호화된 데이터는 클라이언트단에 전달된다.
    # 전달된 데이터는 PASS 창을 띄울 때 사용된다.
    _data = {
        "requestno": req_no,
        "returnurl": returnurl,
        "sitecode": dataBody['site_code'],
        "methodtype": "post",
        "popupyn": 'Y'
    }

    data = json.dumps(_data)

    encoder = AESCipher(key, iv)
    enc_data: str = base64.b64encode(encoder.encrypt(data)).decode('utf-8')

    hmacSha256 = hmac256(hmac_key.encode('utf-8'), enc_data.encode('utf-8'))
    integrity_value = base64.b64encode(hmacSha256).decode('utf-8')

    result = {
        "key": key,
        "iv": iv,
        "hmac_key": hmac_key,
        "req_no": req_no,
        "period": dataBody['period'],
        "timestamp": timestamp,
        "request_data": {
            "token_version_id": dataBody['token_version_id'],
            "enc_data": enc_data,
            "integrity_value": integrity_value
        }
    }

    return result

def is_token_valid(period: int, timestamp: int) -> bool:
    '''토큰의 유효성 검사'''
    time = datetime.fromtimestamp(timestamp)
    expiration_time = time + timedelta(seconds = period)
    now = datetime.now()

    return now < expiration_time


def decrypt_response_data(enc_data: str, key: str, iv: str) -> dict:
    '''암호화된 인증 정보를 복호화 하여 반환한다.'''
    encoder = AESCipher(key, iv)
    dec_data = encoder.decrypt(base64.b64decode(enc_data.encode())).decode('euc-kr')

    result = json.loads(dec_data)

    return result
