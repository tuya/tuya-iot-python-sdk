#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import logging
from tuya_iot import TuyaOpenAPI, TuyaOpenMQ, tuya_logger

from env import ENDPOINT, ACCESS_ID, ACCESS_KEY, USERNAME, PASSWORD

tuya_logger.setLevel(logging.DEBUG)

# Init
openapi = TuyaOpenAPI(ENDPOINT, ACCESS_ID, ACCESS_KEY)
openapi.login(USERNAME, PASSWORD)


# Receive device message
def on_message(msg):
    print("on_message: %s" % msg)


openmq = TuyaOpenMQ(openapi)
openmq.start()
openmq.add_message_listener(on_message)
