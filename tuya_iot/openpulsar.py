#!/usr/bin/python
# -*- coding: UTF-8 -*-

""" This module handle Tuya to B Message Queue by websocket base on websocket-client
    websocket-client doc: https://websocket-client.readthedocs.io/en/latest/getting_started.html
"""
from __future__ import annotations

import base64
import hashlib
import ssl
import threading
import json
import time
import logging
from typing import Callable

import websocket
from Crypto.Cipher import AES

from .openlogging import logger
from .tuya_enums import TuyaCloudPulsarTopic

# basic config
WEB_SOCKET_QUERY_PARAMS = "?ackTimeoutMillis=3000&subscriptionType=Failover"

CONNECT_TIMEOUT_SECONDS = 3
CHECK_INTERVAL_SECONDS = 3

PING_INTERVAL_SECONDS = 30
PING_TIMEOUT_SECONDS = 3

RECONNECT_MAX_TIMES = 1000


class TuyaOpenPulsar(threading.Thread):
    """Tuya Open Pulsar."""

    def __init__(self,
                 access_id: str,
                 access_secret: str,
                 ws_endpoint: str,
                 topic: str):
        """Init TuyaOpenPulsar."""
        threading.Thread.__init__(self)
        self._stop_event = threading.Event()
        self.__reconnect_count = 1

        self.__access_id = access_id
        self.__access_secret = access_secret
        self.__ws_endpoint = ws_endpoint
        self.__topic = topic

        self.message_listeners = set()

        header = {"Connection": "Upgrade",
                  "username": access_id,
                  "password": self.__gen_pwd()}
        websocket.setdefaulttimeout(CONNECT_TIMEOUT_SECONDS)
        self.ws_app = websocket.WebSocketApp(self.__get_topic_url(),
                                             header=header,
                                             on_message=self._on_message,
                                             on_error=self._on_error,
                                             on_close=self._on_close)

        # if logger.level == logging.DEBUG:
        #     websocket.enableTrace(True)

    def _on_message(self, _, message):
        message_json = json.loads(message)
        payload = base64.b64decode(message_json["payload"]).decode('ascii')
        logger.debug("received message origin payload: %s", payload)
        try:
            self.__message_handler(payload)
        except Exception as exception:
            logger.debug(
                "handler message, a business exception has occurred,e:%s", exception)
        self.__send_ack(message_json["messageId"])

    def __gen_pwd(self):
        mix_str = self.__access_id + \
            TuyaOpenPulsar.__md5_hex(self.__access_secret)
        return self.__md5_hex(mix_str)[8:24]

    def __get_topic_url(self):
        return self.__ws_endpoint + "ws/v2/consumer/persistent/"\
            + self.__access_id + "/out/"\
            + self.__topic + "/"\
            + self.__access_id + "-sub"\
            + WEB_SOCKET_QUERY_PARAMS

    def __message_handler(self, payload):
        """Handle message from Tuya cloud."""
        data_map = json.loads(payload)
        decrypt_data = TuyaOpenPulsar.__decrypt_by_aes(
            data_map['data'], self.__access_secret)
        logger.debug("received message descripted: %s", decrypt_data)

        for listener in self.message_listeners:
            listener(decrypt_data)

    @staticmethod
    def __decrypt_by_aes(raw: str,
                         key: str) -> str:
        raw = base64.b64decode(raw)
        key = key[8:24]
        cipher = AES.new(key.encode('utf-8'), AES.MODE_ECB)
        raw = cipher.decrypt(raw)
        res_str = str(raw, "utf-8").strip()
        return res_str

    @staticmethod
    def __md5_hex(md5_str) -> str:
        md_tool = hashlib.md5()
        md_tool.update(md5_str.encode('utf-8'))
        return md_tool.hexdigest()

    def __reconnect(self):
        logger.debug("ws-client connect status is not ok.\n\
                     trying to reconnect for the % d time",
                     self.__reconnect_count)
        self.__reconnect_count += 1
        if self.__reconnect_count < RECONNECT_MAX_TIMES:
            self.__connect()

    def __connect(self):
        logger.debug("---\nws-client connecting...")
        self.ws_app.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE},
                                ping_interval=PING_INTERVAL_SECONDS,
                                ping_timeout=PING_TIMEOUT_SECONDS)

    def __send_ack(self, message_id):
        json_str = json.dumps({"messageId": message_id})
        self.ws_app.send(json_str)

    def _on_error(self, _, error):
        logger.debug("on error is: %s", error)

    def _on_close(self, ws_app, close_status_code, close_msg):
        logger.debug(
            f"Connection closed, code={close_status_code}, close_msg={close_msg}")
        ws_app.close()

    def run(self):
        """Method representing the thread's activity
            which should not be used directly."""

        while not self._stop_event.is_set():

            try:
                if self.ws_app.sock.status == 101:
                    logger.debug("ws-client connect status is ok.")
                    self.__reconnect_count = 1
            except Exception:
                self.__reconnect()

            time.sleep(CHECK_INTERVAL_SECONDS)

    def start(self):
        """Start Message Queue.

        Start Message Queue thread
        """
        logger.debug("start")
        super().start()

    def stop(self):
        """Stop Message Queue.

        Stop Message Queue thread
        """
        logger.debug("stop")
        self.message_listeners = set()
        self.ws_app.close()
        self.ws_app = None
        self._stop_event.set()

    def add_message_listener(self, listener: Callable[[str], None]):
        """Add Message Queue listener."""
        self.message_listeners.add(listener)

    def remove_message_listener(self, listener: Callable[[str], None]):
        """Remvoe Message Queue listener."""
        self.message_listeners.discard(listener)
