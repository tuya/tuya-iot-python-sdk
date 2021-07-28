#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Tuya iot logging."""

import logging
from typing import Any, Dict
import copy

logger = logging.getLogger('tuya iot')

default_handler = logging.StreamHandler()
default_handler.setFormatter(logging.Formatter(
    "[%(asctime)s] [tuya-%(module)s] %(message)s"
))

logger.addHandler(default_handler)
tuya_logger = logger

ACCESS_TOKEN = "access_token"
CLIENT_ID = "client_id"
IP = "ip"
LAT = "lat"
LINK_ID = "link_id"
LOCAL_KEY = "local_key"
LON = "lon"
PASSWORD = "password"
REFRESH_TOKEN = "refresh_token"
UID = "uid"

STAR = "***"


def filter_logger(result_info: Dict[str, Any]):
    if result_info is None:
        return result_info
    filter_info_original = copy.deepcopy(result_info)
    if "result" in filter_info_original:
        filter_info = filter_info_original["result"]
    else:
        filter_info = filter_info_original
    if type(filter_info) == list:
        for item in filter_info:
            if ACCESS_TOKEN in item:
                item[ACCESS_TOKEN] = STAR
            if CLIENT_ID in filter_info:
                item[CLIENT_ID] = STAR
            if IP in item:
                item[IP] = STAR
            if LAT in item:
                item[LAT] = STAR
            if LINK_ID in item:
                item[LINK_ID] = STAR
            if LOCAL_KEY in item:
                item[LOCAL_KEY] = STAR
            if LON in item:
                item[LON] = STAR
            if PASSWORD in filter_info:
                item[PASSWORD] = STAR
            if REFRESH_TOKEN in filter_info:
                item[REFRESH_TOKEN] = STAR
            if UID in item:
                item[UID] = STAR

    elif type(filter_info) == dict:
        if ACCESS_TOKEN in filter_info:
            filter_info[ACCESS_TOKEN] = STAR
        if CLIENT_ID in filter_info:
            filter_info[CLIENT_ID] = STAR
        if IP in filter_info:
            filter_info[IP] = STAR
        if LAT in filter_info:
            filter_info[LAT] = STAR
        if LINK_ID in filter_info:
            filter_info[LINK_ID] = STAR
        if LOCAL_KEY in filter_info:
            filter_info[LOCAL_KEY] = STAR
        if LON in filter_info:
            filter_info[LON] = STAR
        if PASSWORD in filter_info:
            filter_info[PASSWORD] = STAR
        if REFRESH_TOKEN in filter_info:
            filter_info[REFRESH_TOKEN] = STAR
        if UID in filter_info:
            filter_info[UID] = STAR

    return filter_info_original
