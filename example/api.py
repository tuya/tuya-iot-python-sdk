#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import logging
from tuya_iot import TuyaOpenAPI, tuya_logger

from env import *

tuya_logger.setLevel(logging.DEBUG)
# Init
openapi = TuyaOpenAPI(ENDPOINT, ACCESS_ID, ACCESS_KEY)
openapi.login(USERNAME, PASSWORD)

# Get asset list of the user
openapi.get('/v1.0/iot-03/users/assets', {
  'parent_asset_id': '',
  'page_no': 0,
  'page_size': 100,
})

# Get device list of the asset
openapi.get('/v1.0/iot-02/assets/{}/devices'.format(ASSET_ID))

# Get device functions
openapi.get( '/v1.0/iot-03/devices/{}/functions'.format(DEVICE_ID))

# Get device status
openapi.get('/v1.0/iot-03/devices/{}'.format(DEVICE_ID))

# Control device
## Set up the bright value to 25
commands = {'commands': [{'code': 'bright_value', 'value': 25}]}
openapi.post('/v1.0/iot-03/devices/{}/commands'.format(DEVICE_ID), commands)

## Turn on and turn off the light
flag = True
while True:
  input() # wait for input
  flag = not flag
  commands = {'commands': [{'code': 'switch_led', 'value': flag}]}
  openapi.post('/v1.0/iot-03/devices/{}/commands'.format(DEVICE_ID), commands)
