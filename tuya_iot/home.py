#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from .openapi import TuyaOpenAPI
from .openmq import TuyaOpenMQ
from .project_type import ProjectType
from .asset import TuyaAssetManager
from .device import TuyaDeviceManager


class TuyaHomeManager:
    def __init__(
        self, api: TuyaOpenAPI, mq: TuyaOpenMQ, device_manager: TuyaDeviceManager
    ):

        self.api = api
        self.mq = mq
        self.device_manager = device_manager

    def updateDeviceCache(self):
        self.device_manager.deviceMap.clear()
        if self.api.project_type == ProjectType.INDUSTY_SOLUTIONS:
            devIds = []
            assetManager = TuyaAssetManager(self.api)
            response = assetManager.getAssetList()
            assets = response.get("result", {}).get("assets", [])
            for asset in assets:
                asset_id = asset["asset_id"]
                devIds += assetManager.getDeviceList(asset_id)

            self.device_manager.updateDeviceCaches(devIds)
        elif self.api.project_type == ProjectType.SMART_HOME:
            self.device_manager.updateDeviceListInSmartHome()
