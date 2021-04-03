#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

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
# print('deviceStatusMap = {}'.format(deviceManager.deviceStatusMap))
# print('deviceInfoMap = {}'.format(deviceManager.deviceInfoMap))
# print('categoryFunctionMap = {}'.format(deviceManager.categoryFunctionMap))
