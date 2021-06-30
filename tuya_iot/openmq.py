#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Tuya Open IOT HUB which base on MQTT."""

import base64
import json
import time
import threading
import uuid
from typing import Any, Callable, Dict
from urllib.parse import urlsplit
from paho.mqtt import client as mqtt
from Crypto.Cipher import AES

from .openapi import TuyaOpenAPI
from .project_type import ProjectType
from .logging import logger

LINK_ID = "tuya-iot-app-sdk-python.{}".format(uuid.uuid1())
GCM_TAG_LENGTH = 16
CONNECT_FAILED_NOT_AUTHORISED = 5


class TuyaMQConfig:
    """Tuya mqtt config."""

    url = ""
    client_id = ""
    username = ""
    password = ""
    source_topic = {}
    sink_topic = {}
    expireTime = 0

    def __init__(self, mqConfigResponse: Dict[str, Any] = {}):
        """Init TuyaMQConfig."""
        result = mqConfigResponse.get("result", {})

        self.url = result.get("url", "")
        self.client_id = result.get("client_id", "")
        self.username = result.get("username", "")
        self.password = result.get("password", "")
        self.source_topic = result.get("source_topic", {})
        self.sink_topic = result.get("sink_topic", {})
        self.expireTime = result.get("expire_time", 0)


class TuyaOpenMQ(threading.Thread):
    """Tuya open iot hub.

    Tuya open iot hub base on mqtt.

    Attributes:
      openapi: tuya openapi
    """

    def __init__(self, api: TuyaOpenAPI):
        """Init TuyaOpenMQ."""
        threading.Thread.__init__(self)
        self.api: TuyaOpenAPI = api
        self._stop_event = threading.Event()
        self.client = None
        self.message_listeners = set()

    def _get_mqtt_config(self) -> TuyaMQConfig:
        response = self.api.post(
            "/v1.0/iot-03/open-hub/access-config",
            {
                "uid": self.api.token_info.uid,
                "link_id": LINK_ID,
                "link_type": "mqtt",
                "topics": "device",
                "msg_encrypted_version": "2.0"
                if (self.api.project_type == ProjectType.INDUSTY_SOLUTIONS)
                else "1.0",
            },
        )

        if response.get("success", False) is False:
            return None

        return TuyaMQConfig(response)

    def _decode_mq_message(
        self, b64msg: str, password: str, t: str
    ) -> Dict[str, Any]:
        key = password[8:24]

        if self.api.project_type == ProjectType.SMART_HOME:
            cipher = AES.new(key.encode("utf8"), AES.MODE_ECB)
            msg = cipher.decrypt(base64.b64decode(b64msg))
            padding_bytes = msg[-1]
            msg = msg[:-padding_bytes]
            return json.loads(msg)
        else:
            # base64 decode
            buffer = base64.b64decode(b64msg)

            # get iv buffer
            iv_length = int.from_bytes(buffer[0:4], byteorder="big")
            iv_buffer = buffer[4: iv_length + 4]

            # get data buffer
            data_buffer = buffer[iv_length + 4: len(buffer) - GCM_TAG_LENGTH]

            # aad
            aad_buffer = str(t).encode("utf8")

            # tag
            tag_buffer = buffer[len(buffer) - GCM_TAG_LENGTH:]

            cipher = AES.new(key.encode("utf8"), AES.MODE_GCM, nonce=iv_buffer)
            cipher.update(aad_buffer)
            plaintext = cipher.decrypt_and_verify(data_buffer, tag_buffer).decode(
                "utf8"
            )
            return json.loads(plaintext)

    def _on_disconnect(self, client, userdata, rc):
        if rc != 0:
            logger.error(f"Unexpected disconnection.{rc}")
        else:
            logger.debug("disconnect")

    def _on_connect(self, mqttc: mqtt.Client, userData: Any, flags, rc):
        logger.debug(f"connect flags->{flags}, rc->{rc}")
        if rc == 0:
            for (key, value) in self.mq_config.source_topic.items():
                mqttc.subscribe(value)
        elif rc == CONNECT_FAILED_NOT_AUTHORISED:
            self.__run_mqtt()

    def _on_message(
        self, mqttc: mqtt.Client, userData: Any, msg: mqtt.MQTTMessage
    ):
        logger.debug(f"payload-> {msg.payload}")

        msgDict = json.loads(msg.payload.decode("utf8"))

        # topic = msg.topic
        # protocol = msgDict.get("protocol", 0)
        # pv = msgDict.get("pv", "")
        # data = msgDict.get("data", "")

        t = msgDict.get("t", "")

        mq_config = userData["mqConfig"]
        decryptedData = self._decode_mq_message(
            msgDict["data"], mq_config.password, t)
        if decryptedData is None:
            return

        msgDict["data"] = decryptedData
        logger.debug(f"on_message: {msgDict}")

        for listener in self.message_listeners:
            listener(msgDict)

    def _on_subscribe(
        self, mqttc: mqtt.Client, userData: Any, mid, granted_qos
    ):
        logger.debug(f"_on_subscribe: {mid}")

    def _on_log(self, mqttc: mqtt.Client, userData: Any, level, string):
        logger.debug(f"_on_log: {string}")

    def run(self):
        """Method representing the thread's activity which should not be used directly."""
        while not self._stop_event.is_set():
            self.__run_mqtt()

            # reconnect every 2 hours required.
            time.sleep(self.mq_config.expireTime - 60)

    def __run_mqtt(self):
        mq_config = self._get_mqtt_config()
        if mq_config is None:
            logger.error("error while get mqtt config")
            return

        self.mq_config = mq_config

        logger.debug(f"connecting {mq_config.url}")
        mqttc = self._start(mq_config)

        if self.client:
            self.client.disconnect()
        self.client = mqttc

    def _start(self, mq_config: TuyaMQConfig) -> mqtt.Client:
        mqttc = mqtt.Client(mq_config.client_id)
        mqttc.username_pw_set(mq_config.username, mq_config.password)
        mqttc.user_data_set({"mqConfig": mq_config})
        mqttc.on_connect = self._on_connect
        mqttc.on_message = self._on_message
        mqttc.on_subscribe = self._on_subscribe
        mqttc.on_log = self._on_log
        mqttc.on_disconnect = self._on_disconnect

        url = urlsplit(mq_config.url)
        if url.scheme == "ssl":
            mqttc.tls_set()

        mqttc.connect(url.hostname, url.port)

        mqttc.loop_start()
        return mqttc

    def start(self):
        """Start mqtt.

        Start mqtt thread
        """
        logger.debug("start")
        super().start()

    def stop(self):
        """Stop mqtt.

        Stop mqtt thread
        """
        logger.debug("stop")
        self.message_listeners = set()
        self.client.disconnect()
        self.client = None
        self._stop_event.set()

    def add_message_listener(self, listener: Callable[[str], None]):
        """Add mqtt message listener."""
        self.message_listeners.add(listener)

    def remove_message_listener(self, listener: Callable[[str], None]):
        """Remvoe mqtt message listener."""
        self.message_listeners.discard(listener)
