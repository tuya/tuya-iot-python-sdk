#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import hmac
import hashlib
import time
import json
import requests

class TuyaTokenInfo:

    accessToken = ""
    expireTime = 0
    uid = ""
    refreshToken = ""

    def __init__(self, tokenResponse={}):
        result = tokenResponse.get('result', {})

        self.expireTime = tokenResponse.get(
            't', 0) + result.get('expire', result.get('expire_time', 0)) * 1000
        self.accessToken = result.get('access_token', '')
        self.refreshToken = result.get('refresh_token', '')
        self.uid = result.get('uid', '')


class TuyaOpenAPI():
    session = requests.session()
    endpoint = ''
    accessID = ''
    accessKey = ''
    lang = ''
    tokenInfo = TuyaTokenInfo()

    def __init__(self, endpoint, accessID, accessKey, lang='en'):
        self.session = requests.session()

        self.endpoint = endpoint
        self.accessID = accessID
        self.accessKey = accessKey
        self.lang = lang

        self.tokenInfo = TuyaTokenInfo()

    # https://developer.tuya.com/docs/iot/open-api/api-reference/singnature?id=Ka43a5mtx1gsc
    def _calculate_sign(self, client_id, secret, access_token='', t=0):
        if (t == 0):
            t = int(time.time() * 1000)
        message = client_id + access_token + str(t)
        sign = hmac.new(secret.encode('utf8'), msg=message.encode(
            'utf8'), digestmod=hashlib.sha256).hexdigest().upper()
        return sign, t

    def _refresh_access_token_if_need(self, path):
        if self.isLogin() == False:
            return

        if path in ['/v1.0/token']:
            return

        # should use refresh token?
        now = int(time.time() * 1000)
        expired_time = self.tokenInfo.expireTime

        if expired_time - now > 60 * 1000:  # 1min
            return

        response = self.get('/v1.0/token',  {'grant_type': 1})
        self.tokenInfo = TuyaTokenInfo(response)

    def login(self, username, password):
        response = self.post('/v1.0/iot-03/users/login', {
            'username': username,
            'password': hashlib.sha256(password.encode('utf8')).hexdigest().lower(),
        })
        self.tokenInfo = TuyaTokenInfo(response)
        return response

    def isLogin(self):
        return len(self.tokenInfo.accessToken) > 0

    def request(self, method, path, params=None, body=None):

        self._refresh_access_token_if_need(path)

        accessToken = self.tokenInfo.accessToken

        sign, t = self._calculate_sign(
            self.accessID, self.accessKey, accessToken)
        headers = {
            'client_id': self.accessID,
            'sign': sign,
            'sign_method': 'HMAC-SHA256',
            'access_token': accessToken,
            't': str(t),
            'lang': self.lang,
        }

        print('[tuya-openapi] Request: method = {}, url = {}, params = {}, body = {}, headers = {}'.format(
            method, self.endpoint + path, params, body, headers))
        response = self.session.request(
            method, self.endpoint + path, params=params, json=body, headers=headers)

        if response.ok == False:
            print('[tuya-openapi] Response error: code={}, body={}'.format(
                response.status_code, response.body))
            return None

        result = response.json()
        print('[tuya-openapi] Response: {}'.format(json.dumps(result,
                                                              ensure_ascii=False, indent=2)))
        return result

    def get(self, path, params=None):
        return self.request('GET', path, params, None)

    def post(self, path, params=None):
        return self.request('POST', path, None, params)

    def put(self, path, params=None):
        return self.request('PUT', path, None, params)

    def delete(self, path, params=None):
        return self.request('DELETE', path, params, None)
