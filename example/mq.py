import logging
from tuya_iot import TuyaOpenAPI, TuyaOpenMQ, TUYA_LOGGER

from env import ENDPOINT, ACCESS_ID, ACCESS_KEY, USERNAME, PASSWORD


TUYA_LOGGER.setLevel(logging.DEBUG)

# Init
openapi = TuyaOpenAPI(ENDPOINT, ACCESS_ID, ACCESS_KEY)
openapi.connect(USERNAME, PASSWORD, "86", 'tuyaSmart')

# Receive device message
def on_message(msg):
    print("on_message: %s" % msg)

openapi.token_info.expire_time = 0

openmq = TuyaOpenMQ(openapi)
openmq.start()
openmq.add_message_listener(on_message)
