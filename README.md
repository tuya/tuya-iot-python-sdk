⚠️ Working in progress. Will be released before 2021 summer.

# [WIP] tuya-iot-app-sdk-python

With diversified devices and industries, Cloud Development Platform opens basic IoT capabilities like device management, AI scenarios, and data analytics services, as well as industry capabilities, helping you create IoT solutions.

## Preview

<!-- 
[![Watch the video](https://img.youtube.com/vi/izV4b-ZQSds/maxresdefault.jpg)](https://youtu.be/izV4b-ZQSds)
 -->


## Features
- OpenAPI
  - Get device list
  - Get device detail
  - Get device status
  - Control device
  - Modify device name
  - Query device log
  - Remove device
  - ...
- Open IoT Hub (Not released yet)
  - Get device status change

## Possible Scenario

- HomeAssistant Tuya Plugin
- ...

## Before Use

### Part 1. Tuya IoT Platform

1. Register a Tuya Developer account in [Tuya Iot Platform](https://iot.tuya.com/).
2. Go to [Tuya IoT Platform > Cloud Develop > Projects](https://iot.tuya.com/cloud/), create a project. (Project Type - Industry Solutions, Industry - Smart Home)
3. Go to Projects > Your Project > Applications > Cloud, get your AccessID and AccessSecret
4. Go to Projects > Your Project > Users, create a user.
5. Go to Projects > Your Project > Assets, create an asset.
6. Manage your asset, Authorized Users > Add Authorization, add the user created in step 4.
7. Go to Projects > API Products > Industry Project, subscribe api products you need
8. Go to Projects > API Products > Your subscribe API project > Project > New Authorization, authorize your project to use this API
9. Add AccessID, AccessSecret, username, password, asset id in your code.

<!-- Steps Video -->

<!--
 - [Make a developer account on Tuya's site](https://iot.tuya.com/)
 - Once signed in, click on "Cloud" which on the left(or go to https://iot.tuya.com/cloud/)
 - Create a project
 - Click on your new project, you should see a screen similar to this![The project page](https://images.tuyacn.com/smart/developer/93ceaec6-8a9b-453a-a6a5-a9d8625aa955.png)
 - Note your Access ID and Access Secret
 - Click "Link Devices" in the left sidebar, then select the way you want to linked devices. For example, "Link devices by App Account", follow instructions on the site to add your Tuya app account and connected devices.
 - Click "API Groups" in the left sidebar, then apply api group as needed by your usage. For example, "Device Management".
-->

### Part 2. Device Config

1. Open a IoT Config App.(WeChat Mini Programs/iOS App/Android, not ready)
2. Login Tuya developer account.
3. Choose the asset created in part 1.
4. Config your device into the asset.

<!-- Steps Video -->

## Usage

## Installation

`pip3 install tuya-iot-app-sdk-python`

## Code Sample

[OpenAPI Sample](./example/api.py)

[Open IoT Hub Sample](./example/mq.py)

## Tuya Open API Reference

Tuya opens up a variety of APIs covering business scenarios such as device pairing, smart home management, device control, and scene automation. You can call APIs according to API integration documents to implement applications.

See: https://developer.tuya.com/cn/docs/cloud/
<!-- [Documentation > Cloud Development > API Reference](https://developer.tuya.com/docs/iot/open-api/api-reference/api-reference) -->
