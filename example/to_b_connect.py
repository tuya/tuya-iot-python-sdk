"""This module has components that are used for testing to B connect."""
import logging
from tuya_iot.tuya_enums import TuyaCloudPulsarTopic
from tuya_iot import (
    TuyaOpenAPI,
    DevelopMethod,
    AuthType,
    TuyaOpenPulsar,
    TuyaCloudPulsarWSEndpoint,
    TuyaCloudOpenAPIEndpoint,
    TuyaCloudPulsarTopic,
    TUYA_LOGGER
)

ACCESS_ID = "xxxxx"
ACCESS_KEY = "xxxxx"

# Enable debug log
TUYA_LOGGER.setLevel(logging.DEBUG)

# Init openapi and connect
openapi = TuyaOpenAPI(TuyaCloudOpenAPIEndpoint.CHINA,
                      ACCESS_ID,
                      ACCESS_KEY,
                      DevelopMethod.SMART_HOME,
                      AuthType.TO_B)
openapi.connect()
response = openapi.get("/v1.0/statistics-datas-survey", dict())

# Init Message Queue 
open_pulsar = TuyaOpenPulsar(ACCESS_ID,
                             ACCESS_KEY,
                             TuyaCloudPulsarWSEndpoint.CHINA,
                             TuyaCloudPulsarTopic.TEST)
# Add Message Queue listener
open_pulsar.add_message_listener(lambda msg: print(f"---\nexample receive: {msg}"))

# Start Message Queue
open_pulsar.start()

input()
# Stop Message Queue
open_pulsar.stop()
