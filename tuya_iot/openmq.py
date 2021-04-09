#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import base64
import hashlib
import json
import time
import threading
import uuid
from urllib.parse import urlsplit
from paho.mqtt import client as mqtt
from Crypto.Cipher import AES

from .openapi import TuyaOpenAPI

LINK_ID = 'tuya-iot-app-sdk-python.{}'.format(uuid.uuid1())

class TuyaMQConfig:
  url = ''
  client_id = ''
  username = ''
  password = ''
  source_topic = {}
  sink_topic = {}
  expireTime = 0

  def __init__(self, mqConfigResponse = {}):
    result = mqConfigResponse.get('result', {})

    self.url = result.get('url', '')
    self.client_id = result.get('client_id', '')
    self.username = result.get('username', '')
    self.password = result.get('password', '')
    self.source_topic = result.get('source_topic', {})
    self.sink_topic = result.get('sink_topic', {})
    # self.expireTime = mqConfigResponse.get('t', 0) + result.get('expire_time', 0) * 1000
    self.expireTime = result.get('expire_time', 0)

class TuyaOpenMQ(threading.Thread):
  api: TuyaOpenAPI
  client: mqtt.Client = None
  message_listeners = set()

  def __init__(self, openapi: TuyaOpenAPI):
    threading.Thread.__init__(self)
    self.api = openapi

  def _get_mqtt_config(self) -> TuyaMQConfig:
    response = self.api.post('/v1.0/open-hub/access/config', {
      'uid': self.api.tokenInfo.uid,
      'link_id': LINK_ID,
      'link_type': 'mqtt',
      'topics': 'device',
    })

    if response.get('success', False) == False:
      return None

    return TuyaMQConfig(response)

  def _decode_mq_message(self, b64msg: str, password: str) -> dict:
    password = password[8:24]
    cipher = AES.new(password.encode("utf8"), AES.MODE_ECB)
    msg = cipher.decrypt(base64.b64decode(b64msg))
    padding_bytes = msg[-1]
    msg = msg[:-padding_bytes]
    return json.loads(msg)

  def _on_connect(self, mqttc, userData, flags, rc):
    print("[tuya-openmq] connected")

  def _on_message(self, mqttc, userData, msg):
    msgDict = json.loads(msg.payload.decode('utf8'))

    topic = msg.topic

    protocol = msgDict.get('protocol', 0)
    pv = msgDict.get('pv', '')
    data = msgDict.get('data', '')
    sign = msgDict.get('sign', '')

    ## TODO sign check

    mqConfig = userData['mqConfig']
    decryptedData = self._decode_mq_message(msgDict['data'], mqConfig.password)
    if decryptedData == None:
      return

    msgDict['data'] = self._decode_mq_message(msgDict['data'], mqConfig.password)
    print("[tuya-openmq] on_message: {}".format(msgDict))

    for listener in self.message_listeners:
      listener(msgDict)

  def _on_subscribe(self, mqttc, userData, mid, granted_qos):
    # print("[tuya-openmq] _on_subscribe: {}".format(mid))
    pass

  def _on_log(self, mqttc, userData, level, string):
    # print("[tuya-openmq] _on_log: {}".format(string))
    pass

  def run(self):
    while True:
      mqConfig = self._get_mqtt_config()
      if mqConfig == None:
        print('[tuya-openmq] error while get mqtt config')
        break

      print("[tuya-openmq] connecting {}".format(mqConfig.url))
      mqttc = self._start(mqConfig)

      if self.client:
        self.client.disconnect()
      self.client = mqttc

      time.sleep(mqConfig.expireTime - 60) # reconnect every 2 hours required.


  def _start(self, mqConfig: TuyaMQConfig) -> mqtt.Client:
    mqttc = mqtt.Client(mqConfig.client_id)
    mqttc.username_pw_set(mqConfig.username, mqConfig.password)
    mqttc.user_data_set({'mqConfig': mqConfig})
    mqttc.on_connect = self._on_connect
    mqttc.on_message = self._on_message
    mqttc.on_subscribe = self._on_subscribe
    mqttc.on_log = self._on_log

    url = urlsplit(mqConfig.url)
    if url.scheme == 'ssl':
      mqttc.tls_set()

    mqttc.connect(url.hostname, url.port)
    for (key, value) in mqConfig.source_topic.items():
      mqttc.subscribe(value)

    mqttc.loop_start()
    return mqttc

  def start(self):
    print("[tuya-openmq] start")
    super().start()

  def stop(self):
    print("[tuya-openmq] stop")
    self.message_listeners = set()
    self.client.disconnect()
    super().stop()

  def add_message_listener(self, listener):
    self.message_listeners.add(listener)

  def remove_message_listener(self, listener):
    self.message_listeners.remove(listener)
