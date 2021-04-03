#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

class TuyaAssetManager:

  def __init__(self, api):
    self.api = api

  ##############################
  # Asset Management
  # https://wiki.tuya-inc.com:7799/pages/viewpage.action?pageId=89526663

  def getDeviceList(self, assetId):
    devIdList = []

    hasNext = True
    lastRowKey = ''
    while hasNext:
      response = self.api.get('/v1.0/iot-02/assets/{}/devices'.format(assetId), {'last_row_key': lastRowKey})
      result = response.get('result', {})
      hasNext = result.get('has_next', False)
      lastRowKey = result.get('last_row_key', '')
      totalSize = result.get('total_size', 0)

      if len(devIdList) > totalSize: # Error
        raise Exception('getDeviceList error, too many devices.')

      for item in result.get('list', []):
        devIdList.append(item['device_id'])

    return devIdList

  def getAssetInfo(self, assetId):
    return self.api.get('/v1.0/iot-02/assets/{}'.format(assetId))

  # TODO
