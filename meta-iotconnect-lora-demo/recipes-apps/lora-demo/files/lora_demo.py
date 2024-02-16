#!/usr/bin/env python3

import time
from models.lora_gateway_model import *
from helpers.chirpstack_helper import ChirpstackHelper
from local_settings import *


def main():

    print('instantiate gateway instance from GRPC')
    chirp = ChirpstackHelper(server_ip, chirpstack_api_token)
    gw_list = chirp.list_gateways()
    if len(gw_list) > 1:
        print('too many gateways. 80% model is one to many: gateway to nodes')
        exit()
    lora_gw = gw_list[0]
    gw = LoraGateway(cpid, lora_gw['id'], env, iotc_config, server_ip, gw_json=lora_gw, sid=sid)

    print('instantiate devices from GRPC')
    devices = chirp.list_devices()
    for device in devices:
        gw.add_child_from_json(device)

    print('check/create/update iotc template')
    gw.template_check()

    print('init MQTT listener')
    gw.mqtt_listener_thread_init()

    print('connect gw to IOTC')
    gw.connect()

    m_time = 0
    while 1:
        if time.time() - m_time > min_transmit:
            m_time = time.time()
            if not gw.is_connected():
                gw.connect()
            gw.SdkClient._dftime = None
            gw.send_device_states()
            # print('gw.get_device_states():')
            # print(json.dumps(gw.get_device_states(), indent=2))


if __name__ == "__main__":
    main()

