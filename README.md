⚠️ Working in progress. Will be released before 2021 summer.

# [WIP] tuya-iot-app-sdk-python

With diversified devices and industries, Cloud Development Platform opens basic IoT capabilities like device management, AI scenarios, and data analytics services, as well as industry capabilities, helping you create IoT solutions.

## Preview

<!-- 
[![Watch the video](https://img.youtube.com/vi/izV4b-ZQSds/maxresdefault.jpg)](https://youtu.be/izV4b-ZQSds)
 -->


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
- Open IoT Hub (Not released yet)
  - Get device status change

## Possible scenarios

- HomeAssistant Tuya Plugin
- ...

## Before use

### Part 1. Tuya IoT Platform

1. Register a Tuya Developer account in [Tuya IoT Platform](https://iot.tuya.com/).
2. Go to [Tuya IoT Platform > Cloud > Projects](https://iot.tuya.com/cloud/), and Click **Create**. Select **Industry Solutions** in the **Project Type** field, and select **Smart Home** in the **Industry** field.
3. Go to **Projects** > **My Project**, and click the created project to view details. Click **Applications** > **Cloud** to get your AccessID and AccessSecret.
4. Click **Users** > **Add User** to create a user.
5. Click **Assets** > **New Asset** to create an asset.
6. To manage your asset, click **Manage** in the **Action** column. Click **Authorized Users** > **Add Authorization**, and add the user created in Step 4.
7. Go to **Projects** > **API Products** > **All Products**, click **Industry Project**, and subscribe to your desired API products.
8. Go to **Projects** > **API Products** > **Subscribed Products**. Click one of your subscribed products, and click **Project** > **New Authorization** to authorize your project to use this API.
9. Add the AccessID, AccessSecret, username, password, and asset ID in your code.

<!-- Steps Video -->

<!--
 - [Register a developer account on Tuya's site](https://iot.tuya.com/).
 - Once signed in, click **Cloud** on the left sidebar (or go to https://iot.tuya.com/cloud/).
 - Create a project.
 - Click your new project, and you will see a screen similar to this. [The project page](https://images.tuyacn.com/smart/developer/93ceaec6-8a9b-453a-a6a5-a9d8625aa955.png)
 - Find your Access ID and Access Secret.
 - Click **Link Devices**, and select the way you want to link the devices. For example, select **Link devices by App Account**, follow instructions on the screen to add your Tuya Smart app account and connected devices.
 - Click **API Products** in the left sidebar, and apply the API products as needed by your usage. For example, **Device Management**.
-->

### Part 2. Device configuration

1. Open the IoT Config app (not available for WeChat Mini Programs, iOS apps, and Android apps).
2. Log in to [Tuya IoT Platform](https://iot.tuya.com/).
3. Choose the asset created in Part 1.
4. Configure your device into the asset.

<!-- Steps Video -->

## Usage

## Installation

`pip3 install tuya-iot-app-sdk-python`

## Sample code

[OpenAPI Sample](./example/api.py)

[Open IoT Hub Sample](./example/mq.py)

## Tuya Open API reference

Tuya opens up a variety of APIs covering business scenarios such as device pairing, smart home management, device control, and scene automation. You can call APIs according to API integration documents to implement applications.

For more information, see the [documentation](https://developer.tuya.com/en/docs/cloud/).
<!-- [Documentation > Cloud Development > API Reference](https://developer.tuya.com/docs/iot/open-api/api-reference/api-reference) -->
