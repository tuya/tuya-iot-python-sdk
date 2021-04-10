#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import hmac
import hashlib
import time
import json
import requests

from typing import Any, Dict, Optional

TUYA_ERROR_CODE_TOKEN_INVALID = 1010

class TuyaTokenInfo:
    """
    Tuya token info

    Attributes:
        accessToken: Access token.
        expireTime: Valid period in seconds.
        refreshToken: Refresh token.
        uid: Tuya user ID.
    """
    accessToken: str = ""
    expireTime: int = 0
    uid: str = ""
    refreshToken: str = ""

    def __init__(self, tokenResponse: Dict[str, Any] = {}):
        result = tokenResponse.get('result', {})

        self.expireTime = tokenResponse.get(
            't', 0) + result.get('expire', result.get('expire_time', 0)) * 1000
        self.accessToken = result.get('access_token', '')
        self.refreshToken = result.get('refresh_token', '')
        self.uid = result.get('uid', '')


class TuyaOpenAPI():
    """
    Open Api

    Typical usage example:

    openapi = TuyaOpenAPI(ENDPOINT, ACCESS_ID, ACCESS_KEY)
    """
    session: requests.Session = requests.session()
    endpoint: str = ''
    accessID: str = ''
    accessKey: str = ''
    lang: str = ''
    tokenInfo: TuyaTokenInfo = None

    def __init__(self, endpoint: str, accessID: str, accessKey: str, lang: str = 'en'):
        self.session = requests.session()

        self.endpoint = endpoint
        self.accessID = accessID
        self.accessKey = accessKey
        self.lang = lang


    # https://developer.tuya.com/docs/iot/open-api/api-reference/singnature?id=Ka43a5mtx1gsc
    def _calculate_sign(self, client_id: str, secret: str, access_token: str ='', t: int = 0) -> (str, int):
        if (t == 0):
            t = int(time.time() * 1000)
        message = client_id + access_token + str(t)
        sign = hmac.new(secret.encode('utf8'), msg=message.encode(
            'utf8'), digestmod=hashlib.sha256).hexdigest().upper()
        return sign, t

    def _refresh_access_token_if_need(self, path: str):
        if self.isLogin() == False:
            return

        if path.startswith('/v1.0/token'):
            return

        # should use refresh token?
        now = int(time.time() * 1000)
        expired_time = self.tokenInfo.expireTime

        if expired_time - 60 * 1000 > now: # 1min
            return

        self.tokenInfo.accessToken = ''
        response = self.get('/v1.0/token/{}'.format(self.tokenInfo.refreshToken))
        self.tokenInfo = TuyaTokenInfo(response)

    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        user login

        Args:
            username (str): user name
            password (str): user password

        Returns:
            response: login response
        """
        response = self.post('/v1.0/iot-03/users/login', {
            'username': username,
            'password': hashlib.sha256(password.encode('utf8')).hexdigest().lower(),
        })
        self.tokenInfo = TuyaTokenInfo(response)
        return response

    def isLogin(self) -> bool:
        return self.tokenInfo != None and len(self.tokenInfo.accessToken) > 0

    def request(self, method: str, path: str, params: Optional[Dict[str, Any]] = None, body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:

        self._refresh_access_token_if_need(path)

        accessToken = ''
        if self.tokenInfo:
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

        if result.get('code', -1) == TUYA_ERROR_CODE_TOKEN_INVALID:
            self.tokenInfo = None
            # TODO send event

        return result

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Http Get
        Requests the server to return specified resources.

        Args:
            path (str): api path
            params (map): request parameter

        Returns:
            response: response body
        """
        return self.request('GET', path, params, None)

    def post(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Http Post
        Requests the server to update specified resources.

        Args:
            path (str): api path
            params (map): request body

        Returns:
            response: response body
        """
        return self.request('POST', path, None, params)

    def put(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Http Put
        Requires the server to perform specified operations.

        Args:
            path (str): api path
            params (map): request body

        Returns:
            response: response body
        """
        return self.request('PUT', path, None, params)

    def delete(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Http Delete
        Requires the server to delete specified resources.

        Args:
            path (str): api path
            params (map): request param

        Returns:
            response: response body
        """
        return self.request('DELETE', path, params, None)
