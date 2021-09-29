# Tuya IoT Python SDK



![PyPI](https://img.shields.io/pypi/v/tuya-iot-py-sdk)

![PyPI - Downloads](https://img.shields.io/pypi/dm/tuya-iot-py-sdk)

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/tuya-iot-py-sdk)


A Python sdk for Tuya Open API, which provides basic IoT capabilities like device management, asset management and industry capabilities, helping you create IoT solutions. 
With diversified devices and industries, Tuya Cloud Development Platform opens basic IoT capabilities like device management, AI scenarios, and data analytics services, as well as industry capabilities, helping you create IoT solutions.


## Features
### Base APIs
- TuyaOpenAPI
	- connect
	- is_connect
	- get
	- post
	- put
	- delete
 	
- TuyaOpenMQ
	- start
	- stop
	- add_message_listener
	- remove_message_listener

### APIs
- TuyaDeviceListener
	- update_device
	- add_device
	- remove_device

#### Device control
- TuyaDeviceManager
	- update_device_list_in_smart_home
	- update_device_caches
	- update_device_function_cache
	- add_device_listener
	- remove_device_listener
	- get_device_info
	- get_device_list_info
	- remove_device
	- remove_device_list
	- get_factory_info
	- factory_reset
	- get_device_status
	- get_device_list_status
	- get_device_functions
	- get_category_functions
	- get_device_specification
	- send_commands

#### Home 
- TuyaHomeManager
	- update_device_cache
	- query_scenes
	- trigger_scene
	- query_infrared_devices
	- trigger_infrared_commands
	
#### Assets
- TuyaAssetManager
	- get_device_list
	- get_asset_info
	- get_asset_list



## Possible scenarios



- [HomeAssistant Tuya Plugin](https://github.com/tuya/tuya-home-assistant)

- [Tuya Connector Python](https://github.com/tuya/tuya-connector-python)

- [FHEM Tuya Plugin by fhempy](https://github.com/dominikkarall/fhempy/tree/master/FHEM/bindings/python/fhempy/lib/tuya_cloud)

- ...


## Prerequisite

### Registration

Please check [Tuya IoT Platform Configuration Guide](https://developer.tuya.com/en/docs/iot/Configuration_Guide_custom?id=Kamcfx6g5uyot) to register an account on the [Tuya IoT Platform](https://iot.tuya.com?_source=github), and get the required information. You need to create a Cloud project and complete the configuration of asset, user, and application. Then, you will get the **username**, **password**, **Access ID**, and **Access Secret**.

## Usage

## Installation

`pip3 install tuya-iot-py-sdk`

## Sample code

[OpenAPI Sample](https://github.com/tuya/tuya-iot-python-sdk/blob/master/example/device.py)

[Open IoT Hub Sample](https://github.com/tuya/tuya-iot-python-sdk/blob/master/example/mq.py)

## Tuya Open API reference

Tuya opens up a variety of APIs covering business scenarios such as device pairing, smart home management, device control, and scene automation. You can call APIs according to API integration documents to implement applications.

For more information, see the [documentation](https://developer.tuya.com/en/docs/cloud/?_source=github).
<!-- [Documentation > Cloud Development > API Reference](https://developer.tuya.com/docs/iot/open-api/api-reference/api-reference) -->

## Issue feedback

You can provide feedback on your issue via **Github Issue** or [Technical Ticket](https://service.console.tuya.com/).

## License

tuya-iot-py-sdk is available under the MIT license. Please see the [LICENSE](./LICENSE) file for more info.
