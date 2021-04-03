#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from tuya_iot import TuyaOpenAPI, TuyaOpenMQ

from env import *

# Init
openapi = TuyaOpenAPI(ENDPOINT, ACCESS_ID, ACCESS_KEY)
openapi.login(USERNAME, PASSWORD)

# Receive device message
def on_message(msg):
	print('on_message: %s'%msg)

openmq = TuyaOpenMQ(openapi)
openmq.start()
openmq.add_message_listener(on_message)
