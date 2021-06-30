#!/usr/bin/env python3
# -*- coding: UTF-8 -*-


import logging
from env import ENDPOINT, ACCESS_ID, ACCESS_KEY, USERNAME, PASSWORD
from tuya_iot import (
    TuyaOpenAPI,
    ProjectType,
    TuyaOpenMQ,
    TuyaDeviceManager,
    TuyaHomeManager,
    TuyaDeviceListener,
    TuyaDevice,
    TuyaTokenInfo,
    tuya_logger
)

tuya_logger.setLevel(logging.DEBUG)
# Init
openapi = TuyaOpenAPI(ENDPOINT, ACCESS_ID, ACCESS_KEY, ProjectType.INDUSTY_SOLUTIONS)

openapi.login(USERNAME, PASSWORD)
openmq = TuyaOpenMQ(openapi)
openmq.start()

print("device test-> ", openapi.token_info.uid)
# Get device list
# assetManager = TuyaAssetManager(openapi)
# devIds = assetManager.getDeviceList(ASSET_ID)


# Update device status
deviceManager = TuyaDeviceManager(openapi, openmq)


homeManager = TuyaHomeManager(openapi, openmq, deviceManager)
homeManager.update_device_cache()
# # deviceManager.updateDeviceCaches(devIds)
# device = deviceManager.deviceMap.get(DEVICE_ID)


class tuyaDeviceListener(TuyaDeviceListener):
    def update_device(self, device: TuyaDevice):
        print("_update-->", device)

    def add_device(self, device: TuyaDevice):
        print("_add-->", device)

    def remove_device(self, device_id: str):
        pass


deviceManager.add_device_listener(tuyaDeviceListener())

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
    response = openapi.post(
        "/v1.0/iot-03/users/token/{}".format(openapi.token_info.refresh_token)
    )
    openapi.token_info = TuyaTokenInfo(response)
    # openapi.post('/v1.0/iot-03/devices/{}/commands'.format(DEVICE_ID), commands)
