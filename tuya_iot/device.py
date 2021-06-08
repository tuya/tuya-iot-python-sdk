#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import json
import abc
import time
from types import SimpleNamespace
from typing import Any, Dict, List

from .openapi import TuyaOpenAPI
from .openmq import TuyaOpenMQ
from .project_type import ProjectType

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
    """
    Tuya Device

    https://developer.tuya.com/en/docs/iot/open-api/api-reference/smart-home-devices-management/device-management?id=K9g6rfntdz78a#title-5-Return%20parameter

    Attributes:
          id: Device id
          name: Device name
          local_key: Key
          category: Product category
          product_id: Product ID
          product_name: Product name
          sub: Determine whether it is a sub-device, true-> yes; false-> no
          uuid: The unique device identifier
          asset_id: asset id of the device
          online: Online status of the device
          icon: Device icon
          ip: Device IP
          time_zone: device time zone
          active_time: The last pairing time of the device
          create_time: The first network pairing time of the device
          update_time: The update time of device status

          status: Functional status of the device
    """

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

class TuyaDeviceListener(metaclass=abc.ABCMeta):
    @abc.abstractclassmethod
    def updateDevice(self, device:TuyaDevice):
        pass

    @abc.abstractclassmethod
    def addDevice(self, device:TuyaDevice):
        pass

    @abc.abstractclassmethod
    def removeDevice(self, id:str):
        pass

class TuyaDeviceManager:
    """Tuya Device Manager

    This Manager support device control, including getting device status, specifications, the latest statuses, and sending commands

    """

    def __init__(self, 
        api: TuyaOpenAPI, 
        mq: TuyaOpenMQ):
        self.api = api
        self.mq = mq
        self.device_manage = SmartHomeDeviceManage(api) if (api.project_type == ProjectType.SMART_HOME) else IndustrySolutionDeviceManage(api)

        mq.add_message_listener(self._onMessage)
        self.deviceMap: Dict[str, TuyaDevice] = {}
        self.device_listeners = set()


    def __del__(self):
        self.mq.remove_message_listener(self._onMessage)

    def _onMessage(self, msg: str):
        print("device mq->", msg)
        protocol = msg.get('protocol', 0)
        data = msg.get('data', {})
        if protocol == PROTOCOL_DEVICE_REPORT:
            self._onDeviceReport(data['devId'], data['status'])
        elif protocol == PROTOCOL_OTHER:
            self._onDeviceOther(data['devId'], data['bizCode'], data)
        else:
            pass
    
    def __update_device(self, device:TuyaDevice):
        for listener in self.device_listeners:
            listener.updateDevice(device)

    def _onDeviceReport(self, devId: str, status: List):
        device = self.deviceMap.get(devId, None)
        if not device:
            return
        print('_onDeviceReport->', status)
        for item in status:
            if 'code' in item and 'value' in item:
                code = item['code']
                value = item['value']
                device.status[code] = value
        
        self.__update_device(device)

    def _onDeviceOther(self, devId: str, bizCode: str, data: Dict[str, Any]):
        print('_onDeviceReport->', devId, '--', bizCode)

        ## bind device to user
        if bizCode == BIZCODE_BIND_USER:
            devId = data['devId']
            devIds = [devId]
            ## wait for es sync
            time.sleep(1)
            
            self._updateDeviceListInfoCache(devIds)
            self._updateDeviceListStatusCache(devIds)
            response = self.getDeviceFunctions(devId)
            if response.get('success'):
                result = response.get('result', {})
                functionMap = {}
                for function in result['functions']:
                    code = function['code']
                    functionMap[code] = TuyaDeviceFunction(**function)
                self.deviceMap[devId].function = functionMap
            
            if devId in self.deviceMap.keys():
                device = self.deviceMap.get(devId)
                for listener in self.device_listeners:
                    listener.addDevice(device)

        ## device status update
        device = self.deviceMap.get(devId, None)
        if not device:
            return

        if bizCode == BIZCODE_ONLINE:
            device.online = True
            self.__update_device(device)
        elif bizCode == BIZCODE_OFFLINE:
            device.online = False
            self.__update_device(device)
        elif bizCode == BIZCODE_NAME_UPDATE:
            device.name = data['bizData']['name']
            self.__update_device(device)
        elif bizCode == BIZCODE_DPNAME_UPDATE:
            pass
        elif bizCode == BIZCODE_DELETE:
            del self.deviceMap[devId]
            for listener in self.device_listeners:
                listener.removeDevice(device.id)
        elif bizCode == BIZCODE_P2P_SIGNAL:
            pass
        else:
            pass

    ##############################
    # Memory Cache

    def updateDeviceListInSmartHome(self):
        """update devices status in Project type SmartHome
        """
        response = self.api.get(
                '/v1.0/users/{}/devices'.format(self.api.tokenInfo.uid))
        if response['success']:
            for item in response['result']:
                device = TuyaDevice(**item)
                status = {}
                for item_status in device.status:
                    code = item_status['code']
                    value = item_status['value']
                    status[code] = value
                device.status = status
                self.deviceMap[item['id']] = device

        self.updateDeviceFunctionCache()

    def updateDeviceCaches(self, devIds: List[str]):
        ##TODO industry solution devIds max handle 20 devices once call
        """update devices status in cache

        Update devices info, devices status

        Args:
          devIds(List[str]): devices' id
        """
        self._updateDeviceListInfoCache(devIds)
        self._updateDeviceListStatusCache(devIds)


        self.updateDeviceFunctionCache()

    def _updateDeviceListInfoCache(self, devIds: List[str]):
        
        response = self.getDeviceListInfo(devIds)
        result = response.get('result', {})
        for item in result.get('list', []):
            devId = item['id']
            self.deviceMap[devId] = TuyaDevice(**item)

    def _updateDeviceListStatusCache(self, devIds: List[str]):
        
        response = self.getDeviceListStatus(devIds)
        for item in response.get('result', []):
            devId = item['id']
            for status in item['status']:
                code = status['code']
                value = status['value']
                device = self.deviceMap[devId]
                device.status[code] = value
    
    def updateDeviceFunctionCache(self):
        for (devId, device) in self.deviceMap.items():
            response = self.getDeviceFunctions(devId)
            if response.get('success'):
                result = response.get('result', {})
                functionMap = {}
                for function in result['functions']:
                    code = function['code']
                    functionMap[code] = TuyaDeviceFunction(**function)
                device.function = functionMap

    def addDeviceListener(self, listener:TuyaDeviceListener):
        self.device_listeners.add(listener)
    
    def removeDeviceListener(self, listener:TuyaDeviceListener):
        self.device_listeners.remove(listener)

    ##############################
    # OpenAPI

    # Device Management
    # https://developer.tuya.com/docs/cloud/industrial-general-device-management/2fed20dbd9?id=Kag2t5om665oi

    def getDeviceInfo(self, devId: str) -> Dict[str, Any]:
        """Get device info

        Args:
          devId(str): device id
        """
        return self.device_manage.getDeviceInfo(devId)

    def getDeviceListInfo(self, devIds: List[str]) -> Dict[str, Any]:
        """Get devices info

        Args:
          devId(list): device id list

        Returns:
            response: response body

        """
        return self.device_manage.getDeviceListInfo(devIds)

    # def updateDeviceInfo(self, devId: str, info) -> Dict[str, Any]:
        # """Update device information

        # Update device information, such as the device name.

        # Args:
        #   devId(str): device id
        #   info(map): A dict mapping device information, for example:{"name": "room light"}

        # Returns:
        #     response: response body

        # """
        # return self.device_manage.getDeviceInfo(devId, info)

    def removeDevice(self, devId: str) -> Dict[str, Any]:
        """Remove device

        Args:
          devId(str): device id

        Returns:
            response: response body
        """
        return self.device_manage.removeDevice(devId)

    def removeDeviceList(self, devIds: List[str]) -> Dict[str, Any]:
        """Remove devices

        Args:
          devId(list): device id list

        Returns:
            response: response body
        """
        return self.device_manage.removeDeviceList(devIds)

    def getFactoryInfo(self, devId: str) -> Dict[str, Any]:
        """Remove devices factory infos

        Args:
          devId(list): device id list

        Returns:
            response: response body
        """
        return self.device_manage.getFactoryInfo(devId)

    def factoryReset(self, devId: str) -> Dict[str, Any]:
        """Reset device to factory status

        Args:
          devId(str): device id

        Returns:
            response: response body
        """
        return self.device_manage.factoryReset(devId)

    # Device Status
    # https://developer.tuya.com/docs/cloud/industrial-general-device-status-query/f8108a55e3?id=Kag2t60ii54jf

    def getDeviceStatus(self, devId: str) -> Dict[str, Any]:
        """Get device status

        Args:
          devId(str): device id

        Returns:
            response: response body
        """
        return self.device_manage.getDeviceStatus(devId)

    def getDeviceListStatus(self, devIds: List[str]) -> Dict[str, Any]:
        """Get devices status

        Args:
          devIds(list): device ids

        Returns:
            response: response body
        """
        return self.device_manage.getDeviceListStatus(devIds)

    # Device Control
    # https://developer.tuya.com/docs/cloud/industrial-general-device-control/5d2e6fbe8e?id=Kag2t6n3ony2c

    # def getDeviceSpecification(self, devId: str) -> Dict[str, Any]:
    #     """Get device specification attributes

    #     Obtain device specification attributes according to device ID, including command set and status set.

    #     Args:
    #       devId: device id

    #     Returns:
    #         response: response body
    #     """
    #     return self.api.get('/v1.0/iot-03/devices/{}/specification'.format(devId))

    def getDeviceFunctions(self, devId: str) -> Dict[str, Any]:
        """Get the command set supported by the device

        Get the command set supported by the device based on the device ID.

        Args:
          devId: device id

        Returns:
            response: response body
        """
        return self.device_manage.getDeviceFunctions(devId)

    def getCategoryFunctions(self, categoryId: str) -> Dict[str, Any]:
        """Get the instruction set supported by the category

        Get the instruction set supported by the category based on the product category Code

        Args:
          category: category code

        Returns:
            response: response body
        """
        return self.device_manage.getCategoryFunctions(categoryId)

    def sendCommands(self, devId: str, commands: List[str]) -> Dict[str, Any]:
        """Send commands

        Send command to the device.For example:
          {"commands": [{"code": "switch_led","value": true}]}

        Args:
          devId(str): device id
          commands(list):  commands list

        Returns:
            response: response body
        """
        return self.device_manage.sendCommands(devId, commands)

    # Device Registration
    # https://developer.tuya.com/en/docs/cloud/industrial-general-device-registration/41bd0ed112?id=Kag2t66tjhp2i

    # TODO

    ##############################

class DeviceManage(metaclass=abc.ABCMeta):
    api: TuyaOpenAPI

    def __init__(self, api: TuyaOpenAPI):
        self.api = api

    @abc.abstractclassmethod
    def updateDeviceCaches(self, devIds: List[str]):
        pass

    @abc.abstractclassmethod
    def getDeviceInfo(self, devId: str) -> Dict[str, Any]:
        pass

    @abc.abstractclassmethod
    def getDeviceListInfo(self, devIds: List[str]) -> Dict[str, Any]:
        pass

    @abc.abstractclassmethod
    def getDeviceStatus(self, devId: str) -> Dict[str, Any]:
        pass
    
    @abc.abstractclassmethod
    def getDeviceListStatus(self, devIds: List[str]) -> Dict[str, Any]:
        pass
    
    @abc.abstractclassmethod
    def getFactoryInfo(self, devId: str) -> Dict[str, Any]:
        pass

    @abc.abstractclassmethod
    def factoryReset(self, devId: str) -> Dict[str, Any]:
        pass
    
    @abc.abstractclassmethod
    def removeDevice(self, devId: str) -> Dict[str, Any]:
        pass
    
    @abc.abstractclassmethod
    def removeDeviceList(self, devIds: List[str]) -> Dict[str, Any]:
        pass

    @abc.abstractclassmethod
    def getDeviceFunctions(self, devId: str) -> Dict[str, Any]:
        pass
    
    @abc.abstractclassmethod
    def getCategoryFunctions(self, categoryId: str) -> Dict[str, Any]:
        pass
    
    @abc.abstractclassmethod
    def sendCommands(self, devId: str, commands: List[str]) -> Dict[str, Any]:
        pass

class SmartHomeDeviceManage(DeviceManage):
    def updateDeviceCaches(self, devIds: List[str]):
        pass

    def getDeviceInfo(self, devId: str) -> Dict[str, Any]:
        response = self.api.get('/v1.0/devices/{}'.format(devId))
        response['result'].pop('status')
        return response

    def getDeviceListInfo(self, devIds: List[str]) -> Dict[str, Any]:
        response = self.api.get('/v1.0/devices/', {'device_ids': ','.join(devIds)})
        if response['success'] :
            for info in response['result']['devices']:
                info.pop('status')
        response['result']['list'] = response['result']['devices']
        return response

    def getDeviceStatus(self, devId: str) -> Dict[str, Any]:
        response = self.api.get('/v1.0/devices/{}'.format(devId))
        response['result'] = response['result']['status']
        return response
    
    def getDeviceListStatus(self, devIds: List[str]) -> Dict[str, Any]:
        response = self.api.get('/v1.0/devices/', {'device_ids': ','.join(devIds)})
        status_list = []
        if response['success'] :
            for info in response['result']['devices']:
                status_list.append({"id":info["id"], 'status':info['status']})
                
        response['result'] = status_list
        return response
    
    def getFactoryInfo(self, devId: str) -> Dict[str, Any]:
        return self.api.get('/v1.0/devices/factory-infos', {'device_ids': ','.join(devIds)})

    def factoryReset(self, devId: str) -> Dict[str, Any]:
        return self.api.post('/v1.0/devices/{}/reset-factory'.format(devId))
    
    def removeDevice(self, devId: str) -> Dict[str, Any]:
        return self.api.delete('/v1.0/devices/{}'.format(devId))
    
    def removeDeviceList(self, devIds: List[str]) -> Dict[str, Any]:
        raise Exception("Api not support.") 

    def getDeviceFunctions(self, devId: str) -> Dict[str, Any]:
        return self.api.get('/v1.0/devices/{}/functions'.format(devId))
    
    def getCategoryFunctions(self, categoryId: str) -> Dict[str, Any]:
        return self.api.get('/v1.0/functions/{}'.format(categoryId))
    
    def sendCommands(self, devId: str, commands: List[str]) -> Dict[str, Any]:
        return self.api.post('/v1.0/devices/{}/commands'.format(devId), {'commands': commands})

class IndustrySolutionDeviceManage(DeviceManage):
    def updateDeviceCaches(self, devIds: List[str]):
        pass

    def getDeviceInfo(self, devId: str) -> Dict[str, Any]:
        return self.api.get('/v1.0/iot-03/devices/{}'.format(devId))

    def getDeviceListInfo(self, devIds: List[str]) -> Dict[str, Any]:
        return self.api.get('/v1.0/iot-03/devices', {'device_ids': ','.join(devIds)})

    def getDeviceStatus(self, devId: str) -> Dict[str, Any]:
        return self.api.get('/v1.0/iot-03/devices/{}/status'.format(devId))
    
    def getDeviceListStatus(self, devIds: List[str]) -> Dict[str, Any]:
        return self.api.get('/v1.0/iot-03/devices/status', {'device_ids': ','.join(devIds)})
    
    def getFactoryInfo(self, devId: str) -> Dict[str, Any]:
        return self.api.get('/v1.0/iot-03/devices/factory-infos', devId)

    def factoryReset(self, devId: str) -> Dict[str, Any]:
        return self.api.delete('/v1.0/iot-03/devices/{}/actions/reset'.format(devId))
    
    def removeDevice(self, devId: str) -> Dict[str, Any]:
        return self.api.delete('/v1.0/iot-03/devices/{}'.format(devId))
    
    def removeDeviceList(self, devIds: List[str]) -> Dict[str, Any]:
        return self.api.delete('/v1.0/iot-03/devices', {'device_ids': ','.join(devIds)})

    def getDeviceFunctions(self, devId: str) -> Dict[str, Any]:
        return self.api.get('/v1.0/iot-03/devices/{}/functions'.format(devId))
    
    def getCategoryFunctions(self, categoryId: str) -> Dict[str, Any]:
        return self.api.get('/v1.0/iot-03/categories/{}/functions'.format(categoryId))
    
    def sendCommands(self, devId: str, commands: List[str]) -> Dict[str, Any]:
        return self.api.post('/v1.0/iot-03/devices/{}/commands'.format(devId), {'commands': commands})