#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from typing import Any, Dict, List

from .openapi import TuyaOpenAPI


class TuyaAssetManager:
  """Asset Manager

  Attributes:
    api: tuya openapi


  """

  api: TuyaOpenAPI

  def __init__(self, api: TuyaOpenAPI):
    self.api = api

  ##############################
  # Asset Management
  # https://developer.tuya.com/docs/cloud/industrial-general-asset-management/4872453fec?id=Kag2yom602i40

  def getDeviceList(self, assetId: str) -> List[str]:
    """Get devices by assetId

    Args:
      assetId(str): asset id

    Returns:
      A list of device id. For
      example:
      
      [1111,2222]
    
    """
    
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

  def getAssetInfo(self, assetId: str) -> Dict[str, Any]:
    return self.api.get('/v1.0/iot-02/assets/{}'.format(assetId))

  def getAssetList(self, parent_asset_id: str = '') -> Dict[str, Any]:
    return self.api.get('/v1.0/iot-03/users/assets', {'parent_asset_id': parent_asset_id, 'page_no': 0, 'page_size': 100})

  # TODO
