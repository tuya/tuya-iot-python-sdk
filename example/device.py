#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from example.env import *
import time
from tuya_iot import *

# Init
openapi = TuyaOpenAPI(ENDPOINT, ACCESS_ID, ACCESS_KEY, ProjectType.INDUSTY_SOLUTIONS)
openapi.login(USERNAME, PASSWORD)
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
# device = deviceManager.deviceMap.get(DEVICE_ID)

class tuyaDeviceListener(TuyaDeviceListener):
        
        def updateDevice(self, device:TuyaDevice):
            print("_update-->", device)
    
        def addDevice(self, device:TuyaDevice):
            print("_add-->", device)

        def removeDevice(self, id:str):
            pass
    
deviceManager.addDeviceListener(tuyaDeviceListener())

# Turn on the light
# deviceManager.sendCommands(device.id, [{'code': 'switch_led', 'value': True}])
# time.sleep(1)
# print('status: ', device.status)

# # Turn off the light
# deviceManager.sendCommands(device.id, [{'code': 'switch_led', 'value': False}])
# time.sleep(1)
# print('status: ', device.status)

flag = True
while True:
    input()
    # flag = not flag
    # commands = {'commands': [{'code': 'switch_led', 'value': flag}]}
    response = openapi.post('/v1.0/iot-03/users/token/{}'.format(openapi.tokenInfo.refreshToken))
    openapi.tokenInfo = TuyaTokenInfo(response)
    # openapi.post('/v1.0/iot-03/devices/{}/commands'.format(DEVICE_ID), commands)
