#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import time
from tuya_iot import *

from env import *

# Init
openapi = TuyaOpenAPI(ENDPOINT, ACCESS_ID, ACCESS_KEY, ProjectType.SMART_HOME)
openapi.login()
openmq = TuyaOpenMQ(openapi)
openmq.start()

print('device test-> ', openapi.tokenInfo.uid)
# Get device list
# assetManager = TuyaAssetManager(openapi)
# devIds = assetManager.getDeviceList(ASSET_ID)



# Update device status
deviceManager = TuyaDeviceManager(openapi, openmq)


homeManager = TuyaHomeManager(openapi, openmq, deviceManager)
homeManager.updateDeviceCache()
# # deviceManager.updateDeviceCaches(devIds)
device = deviceManager.deviceMap.get(DEVICE_ID)

# Turn on the light
deviceManager.sendCommands(device.id, [{'code': 'switch_led', 'value': True}])
time.sleep(1)
print('status: ', device.status)

# Turn off the light
deviceManager.sendCommands(device.id, [{'code': 'switch_led', 'value': False}])
time.sleep(1)
print('status: ', device.status)
