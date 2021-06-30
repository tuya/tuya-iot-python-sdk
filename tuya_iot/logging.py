#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Tuya iot logging."""

import logging

logger = logging.getLogger('tuya iot')

default_handler = logging.StreamHandler()
default_handler.setFormatter(logging.Formatter(
    "[%(asctime)s] [tuya-%(module)s] %(message)s"
))

logger.addHandler(default_handler)
tuya_logger = logger
