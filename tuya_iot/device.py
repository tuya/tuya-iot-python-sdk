#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

PROTOCOL_DEVICE_REPORT = 4
PROTOCOL_OTHER = 20

BIZCODE_ONLINE = 'online'
BIZCODE_OFFLINE = 'offline'
BIZCODE_NAME_UPDATE = 'nameUpdate'
BIZCODE_DPNAME_UPDATE = 'dpNameUpdate'
BIZCODE_BIND_USER = 'bindUser'
BIZCODE_DELETE = 'delete'
BIZCODE_P2P_SIGNAL = 'p2pSignal'

class TuyaDeviceManager:

  deviceInfoMap = {}
  deviceStatusMap = {}
  categoryFunctionMap = {}

  def __init__(self, api, mq):
    self.api = api
    self.mq = mq
    mq.add_message_listener(self._onMessage)

  def __del__(self):
    self.mq.remove_message_listener(self._onMessage)

  def _onMessage(self, msg):
    protocol = msg.get('protocol', 0)
    data = msg.get('data', {})
    if protocol == PROTOCOL_DEVICE_REPORT:
      self._onDeviceReport(data['devId'], data['status'])
    elif protocol == PROTOCOL_OTHER:
      self._onDeviceOther(data['devId'], data['bizCode'], data)
    else:
      pass

  def _onDeviceReport(self, devId, status):
    oldStatus = self.deviceStatusMap.get(devId, {})
    newStatus = oldStatus.copy()
    for item in status:
      code = item['code']
      value = item['value']
      newStatus[code] = value
    self.deviceStatusMap[devId] = newStatus

  def _onDeviceOther(self, devId, bizCode, data):
    # TODO
    pass

  ##############################
  # Memory Cache

  def updateDeviceCaches(self, devIds):
    self._updateDeviceListStatusCache(devIds)
    self._updateDeviceListInfoCache(devIds)
    self._updateCategoryFunctionCache()

  def _updateDeviceListStatusCache(self, devIds):
    response = self.getDeviceListStatus(devIds)
    for item in response.get('result', []):
      devId = item['id']
      devStatus = {}
      for status in item['status']:
        code = status['code']
        value = status['value']
        devStatus[code] = value
      self.deviceStatusMap[devId] = devStatus

  def _updateDeviceListInfoCache(self, devIds):
    response = self.getDeviceListInfo(devIds)
    for item in response.get('result', {}).get('list', []):
      devId = item['id']
      self.deviceInfoMap[devId] = item

  def _updateCategoryFunctionCache(self):
    categoryIds = set()
    for (devId, devInfo) in self.deviceInfoMap.items():
      category = devInfo.get('category', '')
      if category != '':
        categoryIds.add(category)
    for category in categoryIds:
      response = self.getCategoryFunctions(category)
      result = response.get('result', {})
      functions = result['functions']
      self.categoryFunctionMap[category] = functions


  ##############################
  # IoT Base
  # https://wiki.tuya-inc.com:7799/pages/viewpage.action?pageId=89526663

  # Device Management

  def getDeviceInfo(self, devId):
    return self.api.get('/v1.0/iot-03/devices/{}'.format(devId))

  def getDeviceListInfo(self, devIds):
    return self.api.get('/v1.0/iot-03/devices', {'device_ids': ','.join(devIds)})

  def updateDeviceInfo(self, devId, info):
    return self.api.put('/v1.0/iot-03/devices/{}'.format(devId), info)

  def removeDevice(self, devId):
    return self.api.delete('/v1.0/iot-03/devices/{}'.format(devId))

  def removeDeviceList(self, devIds):
    return self.api.delete('/v1.0/iot-03/devices', {'device_ids': ','.join(devIds)})

  def getFactoryInfo(self, devId):
    return self.api.get('/v1.0/iot-03/devices/factory-infos', devId)

  def factoryReset(self, devId):
    return self.api.delete('/v1.0/iot-03/devices/{}/actions/reset'.format(devId))

  # Device Status

  def getDeviceStatus(self, devId):
    return self.api.get('/v1.0/iot-03/devices/{}/status'.format(devId))

  def getDeviceListStatus(self, devIds):
    return self.api.get('/v1.0/iot-03/devices/status', {'device_ids': ','.join(devIds)})

  # Device Control

  def getDeviceSpecification(self, devId):
    return self.api.get('/v1.0/iot-03/devices/{}/specification'.format(devId))

  def getDeviceFunctions(self, devId):
    return self.api.get('/v1.0/iot-03/devices/{}/functions'.format(devId))

  def getCategoryFunctions(self, categoryId):
    return self.api.get('/v1.0/iot-03/categories/{}/functions'.format(categoryId))

  def publishCommands(self, devId, commands):
    return self.api.post('/v1.0/iot-03/devices/{}/commands'.format(devId, {'commands': commands}))

  # Device Register

  # TODO

  ##############################
