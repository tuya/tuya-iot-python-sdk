#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Tuya Open API."""

from __future__ import annotations

import hmac
import hashlib
import time
import json
import requests
from typing import Tuple
from typing import Any, Dict, Optional
from .project_type import ProjectType
from .logging import logger, filter_logger
from .version import VERSION

TUYA_ERROR_CODE_TOKEN_INVALID = 1010


class TuyaTokenInfo:
    """Tuya token info.

    Attributes:
        access_token: Access token.
        expire_time: Valid period in seconds.
        refresh_token: Refresh token.
        uid: Tuya user ID.
        platform_url: user region platform url
    """

    def __init__(self, tokenResponse: Dict[str, Any] = {}):
        """Init TuyaTokenInfo."""
        result = tokenResponse.get("result", {})

        self.expire_time = (
            tokenResponse.get("t", 0)
            + result.get("expire", result.get("expire_time", 0)) * 1000
        )
        self.access_token = result.get("access_token", "")
        self.refresh_token = result.get("refresh_token", "")
        self.uid = result.get("uid", "")
        self.platform_url = result.get("platform_url", "")


class TuyaOpenAPI:
    """Open Api.

    Typical usage example:

    openapi = TuyaOpenAPI(ENDPOINT, ACCESS_ID, ACCESS_KEY)
    """

    def __init__(
        self,
        endpoint: str,
        access_id: str,
        access_secret: str,
        project_type: ProjectType = ProjectType.INDUSTY_SOLUTIONS,
        lang: str = "en",
    ):
        """Init TuyaOpenAPI."""
        self.session = requests.session()

        self.endpoint = endpoint
        self.access_id = access_id
        self.access_secret = access_secret
        self.lang = lang

        self.project_type = project_type
        self.login_path = (
            "/v1.0/iot-03/users/login"
            if (self.project_type == ProjectType.INDUSTY_SOLUTIONS)
            else "/v1.0/iot-01/associated-users/actions/authorized-login"
        )
        self.token_info: TuyaTokenInfo = None

        self.dev_channel: str = ""

    # https://developer.tuya.com/docs/iot/open-api/api-reference/singnature?id=Ka43a5mtx1gsc
    def _calculate_sign(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = {},
        body: Optional[Dict[str, Any]] = {},
    ) -> Tuple[str, int]:

        # HTTPMethod
        str_to_sign = method
        str_to_sign += "\n"

        # Content-SHA256
        content_to_sha256 = (
            "" if body is None or len(body.keys()) == 0 else json.dumps(body)
        )

        str_to_sign += (
            hashlib.sha256(content_to_sha256.encode(
                "utf8")).hexdigest().lower()
        )
        str_to_sign += "\n"

        # Header
        str_to_sign += "\n"

        # URL
        str_to_sign += path

        if params is not None and len(params.keys()) > 0:
            str_to_sign += "?"

            query_builder = ""
            params_keys = sorted(params.keys())

            for key in params_keys:
                query_builder += f"{key}={params[key]}&"
            str_to_sign += query_builder[:-1]

        # Sign
        t = int(time.time() * 1000)

        message = self.access_id
        if self.token_info is not None:
            message += self.token_info.access_token
        message += str(t) + str_to_sign
        sign = (
            hmac.new(
                self.access_secret.encode("utf8"),
                msg=message.encode("utf8"),
                digestmod=hashlib.sha256,
            )
            .hexdigest()
            .upper()
        )
        return sign, t

    def _refresh_access_token_if_need(self, path: str):
        if self.is_login() is False:
            return

        if path.startswith(self.login_path):
            return

        # should use refresh token?
        now = int(time.time() * 1000)
        expired_time = self.token_info.expire_time

        if expired_time - 60 * 1000 > now:  # 1min
            return

        self.token_info.access_token = ""
        response = self.post(
            "/v1.0/iot-03/users/token/{}".format(self.token_info.refresh_token)
        )
        self.token_info = TuyaTokenInfo(response)

    def set_dev_channel(self, dev_channel: str):
        """Set dev channel."""
        self.dev_channel = dev_channel

    def login(
        self, username: str,
        password: str,
        country_code: str = "",
        schema: str = ""
    ) -> Dict[str, Any]:
        """User login.

        Args:
            username (str): user name
            password (str): user password
            country_code (str): country code in SMART_HOME

        Returns:
            response: login response
        """
        self.__username = username
        self.__password = password
        self.__country_code = country_code
        self.__schema = schema

        response = (
            self.post(
                "/v1.0/iot-03/users/login",
                {
                    "username": username,
                    "password": hashlib.sha256(password.encode("utf8"))
                    .hexdigest()
                    .lower(),
                },
            )
            if (self.project_type == ProjectType.INDUSTY_SOLUTIONS)
            else self.post(
                "/v1.0/iot-01/associated-users/actions/authorized-login",
                {
                    "username": username,
                    "password": hashlib.md5(password.encode("utf8")).hexdigest(),
                    "country_code": country_code,
                    "schema": schema,
                },
            )
        )

        if not response["success"]:
            return response

        self.token_info = TuyaTokenInfo(response)

        return response

    def is_login(self) -> bool:
        """Is login."""
        return self.token_info is not None and len(self.token_info.access_token) > 0

    def __request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:

        self._refresh_access_token_if_need(path)

        access_token = ""
        if self.token_info:
            access_token = self.token_info.access_token

        sign, t = self._calculate_sign(method, path, params, body)
        headers = {
            "client_id": self.access_id,
            "sign": sign,
            "sign_method": "HMAC-SHA256",
            "access_token": access_token,
            "t": str(t),
            "lang": self.lang,
        }

        if self.login_path == path:
            headers["dev_lang"] = "python"
            headers["dev_version"] = VERSION
            headers["dev_channel"] = self.dev_channel

        logger.debug(
            f"Request: method = {method}, url = {self.endpoint + path}, params = {params}, body = {filter_logger(body)}, t = {int(time.time()*1000)} "
        )

        response = self.session.request(
            method, self.endpoint + path, params=params, json=body, headers=headers
        )

        if response.ok is False:
            logger.error(
                f"Response error: code={response.status_code}, body={response.body}"
            )
            return None

        result = response.json()

        logger.debug(
            f"Response: {json.dumps(filter_logger(result), ensure_ascii=False, indent=2)}"
        )

        if result.get("code", -1) == TUYA_ERROR_CODE_TOKEN_INVALID:
            self.token_info = None
            self.login(
                self.__username,
                self.__password,
                self.__country_code,
                self.__schema
            )
            # TODO send event

        return result

    def get(
        self, path: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Http Get.

        Requests the server to return specified resources.

        Args:
            path (str): api path
            params (map): request parameter

        Returns:
            response: response body
        """
        return self.__request("GET", path, params, None)

    def post(
        self, path: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Http Post.

        Requests the server to update specified resources.

        Args:
            path (str): api path
            params (map): request body

        Returns:
            response: response body
        """
        return self.__request("POST", path, None, params)

    def put(
        self, path: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Http Put.

        Requires the server to perform specified operations.

        Args:
            path (str): api path
            params (map): request body

        Returns:
            response: response body
        """
        return self.__request("PUT", path, None, params)

    def delete(
        self, path: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Http Delete.

        Requires the server to delete specified resources.

        Args:
            path (str): api path
            params (map): request param

        Returns:
            response: response body
        """
        return self.__request("DELETE", path, params, None)
