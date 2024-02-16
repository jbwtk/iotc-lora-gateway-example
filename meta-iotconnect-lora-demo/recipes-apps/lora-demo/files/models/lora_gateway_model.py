import threading
from abc import ABC

import paho.mqtt.client as mqtt
from models.device_model import *
from helpers.iotc_helper import IotcApiHelper


def remove_chars(in_str, chars):
    return ''.join(c for c in in_str if c not in chars)


def dump(obj):
    print('\n\n')
    for attr in dir(obj):
        if hasattr(obj, attr ):
            print("obj.%s = %s" % (attr, getattr(obj, attr)))


class LoraGateway(Gateway, ABC):

    def __init__(self, company_id, unique_id, environment, iotc_config, lora_ns_ip, gw_json = None, sdk_options=None, sid=None):
        super().__init__(company_id, unique_id, environment, sdk_options, sid)
        self.mqtt_client = mqtt.Client()
        self.iotc_config = iotc_config
        self.instantiated = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")
        # self.location = {}
        self.template_data = {"code": f"T{self.unique_id[-9:]}"}
        self.attributes_to_exclude = self.attributes_to_exclude + [
            'lora_ns_ip', 'mqtt_client', 'iotc_config', 'template_data', 'api_helper', 'device_guid'
        ]
        self.lora_ns_ip = lora_ns_ip
        if gw_json is not None:
            self.name = gw_json['name']
            self.description = gw_json['description']
            # self.location = gw_json['location']
            self.createdAt = gw_json['createdAt']
            self.updatedAt = gw_json['updatedAt']
            self.firstSeenAt = gw_json['firstSeenAt']
            self.lastSeenAt = gw_json['lastSeenAt']
            self.networkServerName = gw_json['networkServerName']

    def is_connected(self):
        return self.SdkClient is not None

    def template_name(self):
        return f"{self.name} {self.unique_id[-4:]} template"

    def tag(self):
        return f"{self.name[:5]}_{self.unique_id[-4:]}"

    def template_check(self):

        api_helper = IotcApiHelper(config=self.iotc_config)
        template_guid = api_helper.get_template_guid(self.template_name())
        self.template_data['template_guid'] = template_guid
        if template_guid is None:
            print(f'create template & instance for', self.name)
            self.template_data['template_guid'] = api_helper.create_template_and_gateway_device_on_iotc(self)
        for child in self.children:
            print(f'create attrs & instance for', child)
            api_helper.create_child_on_iotc(self, self.children[child])
        if self.is_connected():
            self.connect()

    def add_child_from_json(self, device):
        lora_node = LoraNode(device['devEUI'])
        lora_node.name = device['name']
        lora_node.description = device['description']
        if not device['deviceStatusBatteryLevelUnavailable']:
            lora_node.deviceStatusBattery = device['deviceStatusBattery']
        lora_node.attributes_to_exclude.append('unique_id')
        self.add_child(lora_node)

    def mqtt_listener_thread_init(self):
        t = threading.Thread(target=self.mqtt_listener)
        t.setName(f"MQTT Listener of {self.name}")
        t.daemon = True  # thread dies when main thread exits.
        t.start()

    def mqtt_listener(self):
        self.mqtt_client.message_callback_add("application/+/device/+/event/up", self.on_child_mqtt)
        # self.mqtt_client.message_callback_add("gateway/+/event/up", self.on_gateway_mqtt)
        self.mqtt_client.on_message = self.on_mqtt_message
        self.mqtt_client.connect(self.lora_ns_ip, 1883, keepalive=500)
        self.mqtt_client.subscribe('#')
        # self.mqtt_client.subscribe(f"application/{self.application_id}/device/+/event/up")
        self.mqtt_client.loop_forever()

    def on_mqtt_message(self, client, userdata, msg):
        print('MQTT topic:', msg.topic)
        # print('payload:', msg.payload)
        # obj = json.loads(msg.payload.decode())
        # print(json.dumps(obj, indent=2))

    def on_gateway_mqtt(self, client, userdata, msg):
        print('gateway up topic:', msg.topic)
        # print('payload:', msg.payload)

    def on_child_mqtt(self, client, userdata, msg):
        print('device up topic:', msg.topic)
        payload = json.loads(msg.payload.decode())
        
        # update location
        # self.location = payload['rxInfo'][0]['location']
        self.lastSeenAt = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")

        # use objectJSON to update child
        topic = msg.topic.split('/')
        child_id = topic[3]
        # application_id = topic[1]
        upd_child = False
        try:
            child = self.children[child_id]
        except KeyError:
            # child does not exist ...
            print('MYSTERY CHILD!')
            # create_child_on_iotc
            child = LoraNode(child_id)
            self.add_child(child)
            upd_child = True

        try:
            child.rssi = payload['rxInfo'][0]['rssi']
        except IndexError:
            pass
        child_obj_json = json.loads(payload['objectJSON'])

        for m_key in child_obj_json:
            if not hasattr(child, m_key):
                upd_child = True
                pass

            for m_index in child_obj_json[m_key]:
                setattr(child, m_key, child_obj_json[m_key][m_index])

        if upd_child:
            self.updatedAt = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")
            api_helper = IotcApiHelper(config=self.iotc_config)
            api_helper.create_child_on_iotc(self, child)
            if self.is_connected():
                self.connect()


class LoraNode(GenericDevice):
    def __init__(self, unique_id, tag=None):
        if tag is None:
            tag = f"lora{unique_id[-4:]}"
        super().__init__(unique_id, tag)
        self.instantiated = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")
        self.attributes_to_exclude = self.attributes_to_exclude + ['description']

