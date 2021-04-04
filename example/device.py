#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import time
from tuya_iot import TuyaOpenAPI, TuyaOpenMQ, TuyaAssetManager, TuyaDeviceManager

from env import *

# Init
openapi = TuyaOpenAPI(ENDPOINT, ACCESS_ID, ACCESS_KEY)
openapi.login(USERNAME, PASSWORD)
openmq = TuyaOpenMQ(openapi)
openmq.start()

# Get device list
assetManager = TuyaAssetManager(openapi)
devIds = assetManager.getDeviceList(ASSET_ID)

# Update device status
deviceManager = TuyaDeviceManager(openapi, openmq)
deviceManager.updateDeviceCaches(devIds)
device = deviceManager.deviceMap.get(DEVICE_ID)

# Turn on the light
deviceManager.publishCommands(device.id, [{'code': 'switch_led', 'value': True}])
time.sleep(1)
print('status: ', device.status)

# Turn off the light
deviceManager.publishCommands(device.id, [{'code': 'switch_led', 'value': False}])
time.sleep(1)
print('status: ', device.status)
