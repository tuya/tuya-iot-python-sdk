import logging
from env import ENDPOINT, ACCESS_ID, ACCESS_KEY, USERNAME, PASSWORD
from tuya_iot import (
    TuyaOpenAPI,
    AuthType,
    TuyaOpenMQ,
    TuyaDeviceManager,
    TuyaHomeManager,
    TuyaDeviceListener,
    TuyaDevice,
    TuyaTokenInfo,
    TUYA_LOGGER
)

TUYA_LOGGER.setLevel(logging.DEBUG)
# Init
openapi = TuyaOpenAPI(ENDPOINT, ACCESS_ID, ACCESS_KEY, AuthType.CUSTOM)

openapi.connect(USERNAME, PASSWORD)
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
    flag = not flag
    commands = {'commands': [{'code': 'switch_led', 'value': flag}]}
    openapi.post('/v1.0/iot-03/devices/{}/commands'.format(DEVICE_ID), commands)
