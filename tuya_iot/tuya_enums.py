#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Tuya iot enums."""

from enum import Enum


class DevelopMethod(Enum):
    """Tuya Cloud Project Develop Method."""

    SMART_HOME = 0
    CUSTOM = 1


class AuthType(Enum):
    """Tuya Cloud Auth Type."""

    TO_B = 0
    TO_C = 1


class TuyaCloudOpenAPIEndpoint:
    """Tuya Cloud Open API Endpoint."""

    CHINA = "https://openapi.tuyacn.com"
    AMERICA = "https://openapi.tuyaus.com"
    AMERICA_AZURE = "https://openapi-ueaz.tuyaus.com"
    EUROPE = "https://openapi.tuyaeu.com"
    EUROPE_MS = "https://openapi-weaz.tuyaeu.com"
    INDIA = "https://openapi.tuyain.com"


class TuyaCloudPulsarWSEndpoint:
    """Tuya Cloud Pulsar websocket Endpoint."""

    CHINA = "wss://mqe.tuyacn.com:8285/"
    AMERICA = "wss://mqe.tuyaus.com:8285/"
    EUROPE = "wss://mqe.tuyaeu.com:8285/"
    INDIA = "wss://mqe.tuyain.com:8285/"


class TuyaCloudPulsarTopic:
    """Tuya Cloud Pulsar Topic."""

    RELEASE = "event"
    TEST = "event-test"
