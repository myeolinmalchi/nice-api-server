from pydantic import BaseModel

import urllib.parse as urlparse
from urllib.parse import urlencode

from requests.models import PreparedRequest

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse

import traceback

from app import utils
from app.config import *

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY, https_only=True, same_site="none")

app.add_middleware(
    CORSMiddleware,
    allow_origins = CLIENTS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "HEAD"],
    allow_headers=["Access-Control-Allow-Headers", "Content-Type", "Authorization", "Access-Control-Allow-Origin","Set-Cookie"],)

class EncryptResponse(BaseModel):
    token_version_id: str
    enc_data: str
    integrity_value: str

class DecryptRequest(BaseModel):
    token_version_id: str
    enc_data: str
    integrity_value: str

@app.middleware("https")
async def session(req: Request, call_next):
    response = await call_next(req)
    session = req.cookies.get('session')
    if session:
        response.set_cookie(key='session', value=req.cookies.get('session'), httponly=True)
    return response

@app.get('/nice/encrypt/data')
async def nice_encrypt(req: Request, returnUrl: str, redirectUrl: str):

    try:
        result = utils.encrypt_request_data(returnUrl)

        req.session["redirectUrl"] = redirectUrl

        # 복호화를 위해, 암호화 키를 세션에 저장
        req.session["_nice_key"] = result["key"]
        req.session["_nice_iv"] = result["iv"]
        req.session["_nice_req_no"] = result["req_no"]
        req.session["_nice_period"] = result["period"]
        req.session["_nice_time"] = result["timestamp"]

    except Exception as e:
        err_msg = traceback.format_exc()
        print(err_msg)
        raise HTTPException(400, str(e))

    return EncryptResponse(**result["request_data"])


@app.post('/nice/decrypt/data')
async def nice_decrypt_post(req: Request, body: DecryptRequest):

    try:
        key = req.session.get("_nice_key")
        iv = req.session.get("_nice_iv")
        req_no = req.session.get("_nice_req_no")
        period = req.session.get("_nice_period")
        timestamp = req.session.get("_nice_time")

        if key is None or iv is None or req_no is None or period is None or timestamp is None:
            raise HTTPException(400)

        redirectUrl = req.session.get("redirectUrl")

        if redirectUrl is None:
            raise HTTPException(400)

        enc_data = body.enc_data

        result = utils.decrypt_response_data(enc_data, key, iv)

    except Exception as e:
        err_msg = traceback.format_exc()
        print(err_msg)
        raise HTTPException(400, str(e))

    if result['requestno'] != req_no:
        raise HTTPException(400, '요청 번호가 일치하지 않습니다.')

    if not utils.is_token_valid(period, timestamp):
        raise HTTPException(401, '토큰이 만료되었습니다. 다시 시도하세요.')


    temp = PreparedRequest()
    temp.prepare_url(redirectUrl, result)
    url = temp.url

    res = RedirectResponse(url=url if url else redirectUrl)

    return res

@app.get('/nice/decrypt/data')
async def nice_decrypt_get(
        req: Request,
        token_version_id: str,
        enc_data: str,
        integrity_value: str
    ):

    try:
        key = req.session.get("_nice_key")
        iv = req.session.get("_nice_iv")
        req_no = req.session.get("_nice_req_no")
        period = req.session.get("_nice_period")
        timestamp = req.session.get("_nice_time")

        if key is None or iv is None or req_no is None or period is None or timestamp is None:
            raise HTTPException(400)

        redirectUrl = req.session.get("redirectUrl")

        if redirectUrl is None:
            raise HTTPException(400)

        result = utils.decrypt_response_data(enc_data, key, iv)

    except Exception as e:
        err_msg = traceback.format_exc()
        print(err_msg)
        raise HTTPException(400, str(e))

    if result['requestno'] != req_no:
        raise HTTPException(400, '요청 번호가 일치하지 않습니다.')

    if not utils.is_token_valid(period, timestamp):
        raise HTTPException(401, '토큰이 만료되었습니다. 다시 시도하세요.')

    temp = PreparedRequest()
    temp.prepare_url(redirectUrl, result)
    url = temp.url

    res = RedirectResponse(url=url if url else redirectUrl)

    return res
