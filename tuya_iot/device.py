#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import json
from types import SimpleNamespace
from typing import Dict

PROTOCOL_DEVICE_REPORT = 4
PROTOCOL_OTHER = 20

BIZCODE_ONLINE = 'online'
BIZCODE_OFFLINE = 'offline'
BIZCODE_NAME_UPDATE = 'nameUpdate'
BIZCODE_DPNAME_UPDATE = 'dpNameUpdate'
BIZCODE_BIND_USER = 'bindUser'
BIZCODE_DELETE = 'delete'
BIZCODE_P2P_SIGNAL = 'p2pSignal'


class TuyaDeviceFunction(SimpleNamespace):
  code: str
  desc: str
  name: str
  type: str
  values: Dict[str, Any]

class TuyaDevice(SimpleNamespace):
  id: str
  name: str
  local_key: str
  category: str
  product_id: str
  product_name: str
  sub: bool
  uuid: str
  asset_id: str
  online: bool
  icon: str
  ip: str
  time_zone: str
  active_time: int
  create_time: int
  update_time: int

  status: Dict[str, Dict[str, Any]] = {}
  function: Dict[str, TuyaDeviceFunction] = {}

  def __eq__(self, other):
    return self.id == other.id


class TuyaDeviceManager:

  deviceMap: Dict[str, TuyaDevice] = {}

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
    device = self.deviceMap.get(devId, None)
    if not device:
      return

    for item in status:
      code = item['code']
      value = item['value']
      device.status[code] = value

  def _onDeviceOther(self, devId, bizCode, data):
    device = self.deviceMap.get(devId, None)
    if not device:
      return

    if bizCode == BIZCODE_ONLINE:
      device.online = True
    elif bizCode == BIZCODE_OFFLINE:
      device.online = False
    elif bizCode == BIZCODE_NAME_UPDATE:
      device.name = data['name']
    elif bizCode == BIZCODE_DPNAME_UPDATE:
      pass
    elif bizCode == BIZCODE_BIND_USER:
      pass
    elif bizCode == BIZCODE_DELETE:
      del self.deviceMap[devId]
    elif bizCode == BIZCODE_P2P_SIGNAL:
      pass
    else:
      pass


  ##############################
  # Memory Cache

  def updateDeviceCaches(self, devIds):
    self._updateDeviceListInfoCache(devIds)
    self._updateDeviceListStatusCache(devIds)
    self._updateCategoryFunctionCache()

  def _updateDeviceListInfoCache(self, devIds):
    response = self.getDeviceListInfo(devIds)
    result = response.get('result', {})
    for item in result.get('list', []):
      devId = item['id']
      self.deviceMap[devId] = TuyaDevice(**item)

  def _updateDeviceListStatusCache(self, devIds):
    response = self.getDeviceListStatus(devIds)
    for item in response.get('result', []):
      devId = item['id']
      for status in item['status']:
        code = status['code']
        value = status['value']
        device = self.deviceMap[devId]
        device.status[code] = value

  def _updateCategoryFunctionCache(self):
    categoryIds = set()
    for (devId, device) in self.deviceMap.items():
      if device.category != '':
        categoryIds.add(device.category)
    for category in categoryIds:
      response = self.getCategoryFunctions(category)
      result = response.get('result', {})
      functionMap = {}
      for function in result['functions']:
        code = function['code']
        functionMap[code] = TuyaDeviceFunction(**function)
      self.categoryFunctionMap[category] = functionMap
    for (devId, device) in self.deviceMap.items():
      device.function = self.categoryFunctionMap[device.category]

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
    return self.api.post('/v1.0/iot-03/devices/{}/commands'.format(devId), {'commands': commands})

  # Device Register

  # TODO

  ##############################
