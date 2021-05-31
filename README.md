# Tuya IoT Python SDK

![PyPI](https://img.shields.io/pypi/v/tuya-iot-py-sdk)
![PyPI - Downloads](https://img.shields.io/pypi/dm/tuya-iot-py-sdk)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/tuya-iot-py-sdk)

A Python sdk for Tuya Open API, which provides basic IoT capabilities like device management, asset management and industry capabilities, helping you create IoT solutions. With diversified devices and industries, Tuya Cloud Development Platform opens basic IoT capabilities like device management, AI scenarios, and data analytics services, as well as industry capabilities, helping you create IoT solutions.

## Features
- OpenAPI
  - Get the device list
  - Get the device details
  - Get device status
  - Control devices
  - Modify the device name
  - Query the device log
  - Remove devices
  - ...
- Open IoT Hub
  - Get device status change

## Possible scenarios

- [HomeAssistant Tuya Plugin](https://github.com/tuya/tuya-home-assistant)
- ...

## Prerequisite

### Registration

Please check [Tuya IoT Platform Configuration Guide](https://github.com/tuya/tuya-android-iot-app-sdk-sample/blob/activator_tool/Tuya_IoT_Platform_Configuration_Guide.md) to register an account on the [Tuya IoT Platform](https://iot.tuya.com?_source=github), and get the required information. You need to create a Cloud project and complete the configuration of asset, user, and application. Then, you will get the **username**, **password**, **Access ID**, and **Access Secret**.

## Usage

## Installation

`pip3 install tuya-iot-py-sdk`

## Sample code

[OpenAPI Sample](https://github.com/tuya/tuya-iot-app-sdk-python/example/api.py)

[Open IoT Hub Sample](https://github.com/tuya/tuya-iot-app-sdk-python/example/mq.py)

## Tuya Open API reference

Tuya opens up a variety of APIs covering business scenarios such as device pairing, smart home management, device control, and scene automation. You can call APIs according to API integration documents to implement applications.

For more information, see the [documentation](https://developer.tuya.com/en/docs/cloud/?_source=github).
<!-- [Documentation > Cloud Development > API Reference](https://developer.tuya.com/docs/iot/open-api/api-reference/api-reference) -->

## Issue feedback

You can provide feedback on your issue via **Github Issue** or [Technical Ticket](https://service.console.tuya.com/).

## License

tuya-iot-py-sdk is available under the MIT license. Please see the [LICENSE](./LICENSE) file for more info.
