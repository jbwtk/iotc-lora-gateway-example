import json
from datetime import datetime
from iotconnect import IoTConnectSDK
from models.enums import Enums as E


def print_msg(title, msg):
    print("{}: \n{}".format(title, json.dumps(msg, indent=2)))


class GenericDevice(object):
    """
    minimal device, no connectivity, has to be child device
    """
    template = None
    children = None
    attr_ignore_list = ['unique_id']
    tag = 'GenericDevice'

    def get_attributes_to_send(self):
        return [attribute for attribute in self.attributes_to_send if attribute not in self.attributes_to_exclude]

    def __init__(self, unique_id, tag=None):
        self.unique_id = unique_id
        self.name = unique_id
        if tag is not None:
            self.tag = tag

        self.attributes_to_send = []
        self.attributes_to_exclude = ['attributes_to_exclude', 'attributes_to_send', 'unique_id', 'name', 'children']

    # Not updated
    def for_iotconnect_upload(self):
        export_dict = {
            "name": self.name,
            "uniqueId": self.unique_id,
            "tag": self.tag,
            "properties": []
        }
        for attr in vars(self):
            if attr not in self.attr_ignore_list:
                prop_obj = {'key': attr, 'val': vars(self)[attr]}
                export_dict['properties'].append(prop_obj)
        return export_dict

    # Not updated
    def template_attributes(self, export_dict):
        """
        appends attributes to export dictionary for IOTC template creation
        :param export_dict:
        :return export_dict:
        """

        for attr in vars(self):
            if attr not in self.attr_ignore_list:
                attr_obj = {
                    'name': attr,
                    'type': self.type_for_iotc(vars(self)[attr]),
                    'tag': self.tag,
                    'description': None,
                    'unit': None
                }
                export_dict['attributes'].append(attr_obj)
        return export_dict

    @staticmethod
    def type_for_iotc(obj):
        """
        attempts to set the template attribute type
        :param obj: object
        :return string:
        """
        if isinstance(obj, str):
            return 'STRING'
        elif isinstance(obj, bool):
            return 'BOOLEAN'
        elif isinstance(obj, float):
            return 'DECIMAL'
        elif isinstance(obj, int):
            # or isinstance(obj, numbers.Integral)
            return 'INTEGER'
        elif isinstance(obj, dict):
            return 'OBJECT'
        elif isinstance(obj, str):
            return 'STRING'
        elif isinstance(obj, datetime):
            return 'DATETIME'
        # elif isinstance(obj, bit):
        #     return 'BIT'
        # elif isinstance(obj, ):
        #     return 'LATLONG'
        # elif isinstance(obj, type):
        #     return 'DATE'
        # elif isinstance(obj, type):
        #     return 'TIME'
        return 'STRING'

    # provides the object JSON structure for sending to IOTC
    def get_d2c_data(self):
        data_obj = {
            "uniqueId": self.unique_id,
            "time": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "data": self.get_state()
        }
        return data_obj

    def get_d2c_rpt_data(self):
        # 'id': '0080e115000a9280', 'dt': '2023-11-21T16:57:38.000Z', 'tg': 'astra1b', 'd':
        data_obj = {
            "uniqueId": self.name,
            "time": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "data": self.get_state()
        }
        return data_obj

    def get_state(self):
        # return {attribute: vars(self)[attribute] for attribute in self.get_attributes_to_send() if attribute in vars(self)}
        return {attribute: vars(self)[attribute] for attribute in vars(self) if attribute not in self.attributes_to_exclude}


class ConnectedDevice(GenericDevice):

    CMD_TYPE_DEVICE = '0x01'
    CMD_TYPE_FIRMWARE = '0x02'
    CMD_TYPE_CONNECTION = '0x16'

    AUTH_TYPE_TOKEN = 1

    api_ver = 2.1

    def __init__(self, company_id, unique_id, environment, sdk_options=None, sid=None):
        super().__init__(unique_id)
        self.company_id = company_id
        self.Env = environment
        self.SdkClient = None
        self.SdkOptions = sdk_options
        self.sId = sid
        self.attributes_to_exclude = self.attributes_to_exclude + [
            "SdkClient", "SdkOptions", "company_id", "Env", "sId", "server_ip"
        ]

    # Not updated
    def template_output(self, iotc_code, iotc_name, auth_type):
        export_dict = {
            "code": iotc_code,
            "name": iotc_name,
            "tag": self.tag,
            "authType": auth_type,
            "isIotEdgeEnable": False,
            "attributes": []
        }
        export_dict = self.template_attributes(export_dict)
        for child in self.children:
            export_dict = self.children[child].template_attributes(export_dict)
        return export_dict

    def connect(self):
        print("message version {}".format(self.api_ver))

        if self.SdkClient is not None:
            self.SdkClient.Dispose()

        if self.api_ver == 2.1:
            # def __init__(self, uniqueId, sId, sdkOptions=None, initCallback=None)
            # def __init__(self, uniqueId, sId, cpid, env, sdkOptions=None, initCallback=None):
            self.SdkClient = IoTConnectSDK(
                uniqueId=self.unique_id,
                sId=self.sId,
                sdkOptions=self.SdkOptions,
                initCallback=None
            )
        else:
            # def __init__(self, cpId, uniqueId, listner, listner_twin, sdkOptions=None, env="PROD")
            self.SdkClient = IoTConnectSDK(
                self.company_id,
                self.unique_id,
                self.device_cb,
                self.twin_update_cb,
                self.SdkOptions,
                self.Env
            )

        self.bind_callbacks()

    # def device_cb(self, msg, status=None):
    #     if status is None:
    #         print("device callback")
    #         print(json.dumps(msg, indent=2))
    #         if msg["cmdType"] == self.CMD_TYPE_DEVICE:
    #             print("device command cmdType")
    #         elif msg["cmdType"] == self.CMD_TYPE_FIRMWARE:
    #             print("firmware cmdType")

    #         elif msg["cmdType"] == self.CMD_TYPE_CONNECTION:
    #             # Device connection status e.g. data["command"] = true(connected) or false(disconnected)
    #             print("connection status cmdType")

    #         else:
    #             print("unimplemented cmdType: {}".format(msg["cmdType"]))

    #         print_msg("message", msg)

    #     if msg['ack'] == "True":
    #         print_msg("ack message", msg)
    #         d2c_msg = {
    #             "ackId": msg["ackId"],
    #             "st": status,
    #             "msg": "",
    #             "childId": ""
    #         }
    #         self.SdkClient.SendACK(d2c_msg, 5)  # 5 : command acknowledgement

    def get_device_states(self):
        data_array = [self.get_d2c_data()]
        if self.children is not None:
            for child in self.children:
                child_data = self.children[child].get_d2c_data()
                data_array.append(child_data)
        return data_array

    def send_device_states(self):
        data_array = self.get_device_states()
        self.send_d2c(data_array)
        return data_array

    def send_d2c(self, data):
        if self.SdkClient is not None:
            res = self.SdkClient.SendData(data)
        else:
            print("no client")

    def direct_message_ack(self, rId, data, status=200):
        return self.SdkClient.DirectMethodACK(data, status, rId)

    def get_twins(self):
        return self.SdkClient.GetAllTwins()

    def direct_method_cb(self, msg, rId):
        print("direct method CB on template {}".format(self.template))
        print(msg)
        print(rId)
        # DirectMethodACK(msg,status,requestId
        self.SdkClient.DirectMethodACK(msg, )

    def twin_update(self, key, value):
        print("twin update on {} template {}, {} = {}".format(self.unique_id, self.template, key, value))
        self.SdkClient.UpdateTwin(key, value)

    def twin_update_cb(self, msg):
        print_msg("twin update CB on {} template {}".format(self.unique_id, self.template), msg)

    def ota_cb(self,msg):
        raise NotImplementedError()

    def module_cb(self,msg):
        raise NotImplementedError()

    def twin_change_cb(self,msg):
        raise NotImplementedError()

    def attribute_change_cb(self,msg):
        raise NotImplementedError()

    def device_change_cb(self,msg):
        raise NotImplementedError()

    def rule_change_cb(self,msg):
        raise NotImplementedError()

    def device_cb(self, msg):
        raise NotImplementedError()

    def init_cb(self, msg):
            print("connection status is " + msg["command"])
        
    def bind_callbacks(self):
        self.SdkClient.onOTACommand(self.ota_cb)
        self.SdkClient.onModuleCommand(self.module_cb)
        self.SdkClient.onTwinChangeCommand(self.twin_change_cb)
        self.SdkClient.onAttrChangeCommand(self.attribute_change_cb)
        self.SdkClient.onDeviceChangeCommand(self.device_change_cb)
        self.SdkClient.onRuleChangeCommand(self.rule_change_cb)
        self.SdkClient.onDeviceCommand(self.device_cb)

    def send_ack(self, msg, status: E.Values.AckStat, message):
        # check if ack exists in message
        if E.get_value(msg, E.Keys.ack) is None:
            print("Ack not requested, returning")
            return
        
        id_to_send = E.get_value(msg, E.Keys.id)
        self.SdkClient.sendAckCmd(msg[E.Keys.ack], status, message, id_to_send)


class Gateway(ConnectedDevice):

    def __init__(self, company_id, unique_id, environment, sdk_options=None, sid=None):
        super().__init__(company_id, unique_id, environment, sdk_options, sid)
        self.children = {}

    def add_child(self, child):
        # print('add child id:', child.name)
        self.children[child.unique_id] = child
        # self.children.append(child)

    def show_children(self):
        print(len(self.children), "children")
        if len(self.children) > 0:
            for child in self.children:
                print("child:", child, self.children[child].name)
        else:
            print("no children")

    def for_iotconnect_children_upload(self):
        # produce json for bulk child upload
        print(self.unique_id, 'for_iotconnect_upload:')
        export_dict = {
            "gateway": {
                "items": []
            }
        }
        for child in self.children:
            export_dict["gateway"]["items"].append(self.children[child].for_iotconnect_upload())
        return export_dict
