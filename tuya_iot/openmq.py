#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import base64
import hashlib
import json
import time
import threading
from urllib.parse import urlsplit
from paho.mqtt import client as mqtt
from Crypto.Cipher import AES

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
    self.expireTime = mqConfigResponse.get('t', 0) + result.get('expire_time', 0) * 1000

class TuyaOpenMQ(threading.Thread):
  openapi = None
  callback = None
  message_listeners = set()

  def __init__(self, openapi):
    threading.Thread.__init__(self)
    self.openapi = openapi

  def _update_mqtt_config_if_need(self):
    mqConfig = self.openapi.post('/v1.0/open-hub/access/config', {
      'uid': self.openapi.tokenInfo.uid,
      'link_id': 'tuya-iot-app-sdk-python',
      'link_type': 'mqtt',
      'topics': 'device',
    })
    self.mqConfig = TuyaMQConfig(mqConfig)

  def _decode_mq_message(self, b64msg, password):
    password = password[8:24]
    cipher = AES.new(password.encode("utf8"), AES.MODE_ECB)
    msg = cipher.decrypt(base64.b64decode(b64msg))
    padding_bytes = msg[-1]
    msg = msg[:-padding_bytes]
    return json.loads(msg)

  def _on_connect(self, mqttc, obj, flags, rc):
    print("[tuya-openmq] _on_connect")

  def _on_message(self, mqttc, obj, msg):
    msgDict = json.loads(msg.payload.decode('utf8'))

    topic = msg.topic

    protocol = msgDict.get('protocol', 0)
    pv = msgDict.get('pv', '')
    data = msgDict.get('data', '')
    sign = msgDict.get('sign', '')

    ## TODO sign check

    decryptedData = self._decode_mq_message(msgDict['data'], self.mqConfig.password)
    if decryptedData == None:
      return

    msgDict['data'] = self._decode_mq_message(msgDict['data'], self.mqConfig.password)
    print("[tuya-openmq] _on_message: {}".format(msgDict))

    for listener in self.message_listeners:
      listener(msgDict)

  def _on_subscribe(self, mqttc, obj, mid, granted_qos):
    # print("[tuya-openmq] _on_subscribe: {}".format(mid))
    pass

  def _on_log(self, mqttc, obj, level, string):
    # print("[tuya-openmq] _on_log: {}".format(string))
    pass

  def run(self):
    self.client.loop_forever()

  def start(self):
    self._update_mqtt_config_if_need()
    print("[tuya-openmq] start connecting {}".format(self.mqConfig.url))

    self.client = mqttc = mqtt.Client(self.mqConfig.client_id)
    mqttc.username_pw_set(self.mqConfig.username, self.mqConfig.password)
    mqttc.on_connect = self._on_connect
    mqttc.on_message = self._on_message
    mqttc.on_subscribe = self._on_subscribe
    mqttc.on_log = self._on_log

    url = urlsplit(self.mqConfig.url)
    if url.scheme == 'ssl':
      mqttc.tls_set()

    mqttc.connect(url.hostname, url.port)
    for (key, value) in self.mqConfig.source_topic.items():
      self.subscribe(value)

    super().start()

  def stop(self):
    print("[tuya-openmq] stop")
    self.callback = None
    self.client.close()

  def subscribe(self, topic):
    print("[tuya-openmq] subscribe topic: {}".format(topic))
    self.client.subscribe(topic)

  def unsubscribe(self, topic):
    print("[tuya-openmq] unsubscribe topic: {}".format(topic))
    self.client.unsubscribe(topic)

  # def subscribe_device(self, device_id):
  #   topic = self.mqConfig.sink_topic['device'].format(device_id=device_id)
  #   self.subscribe(topic)

  # def unsubscribe_device(self, device_id):
  #   topic = self.mqConfig.sink_topic['device'].format(device_id=device_id)
  #   self.unsubscribe(topic)

  def add_message_listener(self, listener):
    self.message_listeners.add(listener)

  def remove_message_listener(self, listener):
    self.message_listeners.remove(listener)
