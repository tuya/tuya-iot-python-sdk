#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Tuya home's api base on asset and device api."""

from .openapi import TuyaOpenAPI
from .openmq import TuyaOpenMQ
from .project_type import ProjectType
from .asset import TuyaAssetManager
from .device import TuyaDeviceManager


class TuyaHomeManager:
    """Tuya Home Manager."""

    def __init__(
        self, api: TuyaOpenAPI,
        mq: TuyaOpenMQ,
        device_manager: TuyaDeviceManager
    ):
        """Init tuya home manager."""
        self.api = api
        self.mq = mq
        self.device_manager = device_manager

    def update_device_cache(self):
        """Update home's devices cache."""
        self.device_manager.device_map.clear()
        if self.api.project_type == ProjectType.INDUSTY_SOLUTIONS:
            device_ids = []
            asset_manager = TuyaAssetManager(self.api)

            self.__query_device_ids(asset_manager, "-1", device_ids)

            # assets = asset_manager.get_asset_list()
            # for asset in assets:
            #     asset_id = asset["asset_id"]
            #     device_ids += asset_manager.get_device_list(asset_id)
            if len(device_ids) > 0:
                self.device_manager.update_device_caches(device_ids)
        elif self.api.project_type == ProjectType.SMART_HOME:
            self.device_manager.update_device_list_in_smart_home()

    def __query_device_ids(
            self,
            asset_manager: TuyaAssetManager,
            asset_id: str,
            device_ids: list) -> list:
        print(f"query_devices{asset_id}")
        if (asset_id is not "-1"):
            device_ids += asset_manager.get_device_list(asset_id)
        assets = asset_manager.get_asset_list(asset_id)
        for asset in assets:
            print(f"asset--->{asset}")
            self.__query_device_ids(asset_manager,
                                    asset["asset_id"],
                                    device_ids)
        return device_ids
