import requests
import json

from models.iotc_types import IOTCTypes

API_USER_URL = "https://avnetuser.iotconnect.io/api/v2"
API_AUTH_URL = "https://avnetauth.iotconnect.io/api/v2"
API_DEVICE_URL = "https://avnetdevice.iotconnect.io/api/v2"


class IotcApiHelper(object):

    def __init__(self, config):
        self.company_name = config['company_name']
        self.solution_key = config['solution_key']
        self.company_guid = config['company_guid']
        self.timeout = 10
        self.header = {
            "Authorization": f"Bearer {self.get_access_token()}",
            "Content-type": "application/json",
        }

    def get_access_token(self):
        print('authorising IotcApiHelper ...')
        response = requests.get(f"{API_USER_URL}/company/{self.company_guid}/service-account", timeout=self.timeout)
        service_account = json.loads(response.text)
        username = service_account["data"]["username"]
        password = service_account["data"]["password"]

        response = requests.get(f"{API_AUTH_URL}/Auth/basic-token", timeout=self.timeout)
        if response.status_code != 200:
            print("error")
            exit(-1)

        basic_token = json.loads(response.text)['data']
        header = {
            "Authorization": f"Basic {basic_token}",
            "solution-key": self.solution_key,
            "Content-type": "application/json",
        }

        body = {
            "username": username,
            "password": password
        }
        access_token = requests.post(f"{API_AUTH_URL}/Auth/login", timeout=self.timeout, headers=header, json=body)
        access_token = json.loads(access_token.text)
        return access_token["access_token"]

    def get_template_guid(self, template_name):
        response = requests.get(f"{API_DEVICE_URL}/device-template{'?DeviceTemplateName='}{template_name}", headers=self.header, timeout=self.timeout)
        response = json.loads(response.text)
        # print(json.dumps(response, indent=2))
        for data in response["data"]:
            return data["guid"]

    def get_device_guid(self, device_name):
        uri = f"{API_DEVICE_URL}/Device?Name={device_name}"
        response = requests.get(uri, headers=self.header, timeout=self.timeout)
        response = json.loads(response.text)
        for data in response["data"]:
            return data["guid"]

    def get_device_guid_for_template(self, template_guid):
        uri = f"{API_DEVICE_URL}/template/{template_guid}/device"
        response = requests.get(uri, headers=self.header, timeout=self.timeout)
        response = json.loads(response.text)
        for data in response["data"]:
            return data["guid"]

    def get_entity_guid(self, company_name):
        response = requests.get(f"{API_USER_URL}/Entity", headers=self.header, timeout=self.timeout)
        response = json.loads(response.text)
        ret = ""
        for data in response["data"]:
            if data["name"] == company_name:
                ret = data["guid"]
                break
        return ret

    def get_data_types(self):
        """
        useless, does not provide all of the attributes
        """
        response = requests.get("https://avnetmaster.iotconnect.io/Property/custom-field-type", headers=self.header, timeout=self.timeout)
        response = json.loads(response.text)
        print('get_data_types', response)

    def create_gateway_template(self, template_code, auth_type, tag, template_name):
        """
        create a blank template
        return template.guid
        """
        template_create_request = {
            "code": template_code,
            "isEdgeSupport": "false",
            "authType": auth_type,
            "tag": tag,
            "messageVersion": "2.1",
            "name": template_name,
            # "isSphere": "true",
            # "trustedPartnerGuid": "string",
            # "dataLength": 0,
            # "isIotEdgeEnable": "true",
            # "firmwareguid": "string"
        }

        response = requests.post(f"{API_DEVICE_URL}/device-template", timeout=self.timeout, headers=self.header, json=template_create_request)
        # print('create_gateway_template', response.json()['message'])
        if response.status_code != 200:
            return False
        return json.loads(response.text)['data'][0]['deviceTemplateGuid']

    def delete_device(self, device_guid):

        response = requests.delete(f"{API_DEVICE_URL}/Device/{device_guid}", timeout=self.timeout, headers=self.header)
        # response = json.loads(response.text)
        if response.status_code != 200:
            print('delete_device', response)
        return response.status_code == 200

    def delete_template(self, template_guid):
        uri = f"{API_DEVICE_URL}/device-template/{template_guid}"
        response = requests.delete(uri, timeout=self.timeout, headers=self.header)
        # response = json.loads(response.text)
        if response.status_code != 200:
            print('delete_template', response)
        return response.status_code == 200

    def get_template(self, template_guid):
        response = requests.get(f"{API_DEVICE_URL}/device-template/{template_guid}",
                                   timeout=self.timeout, headers=self.header)
        # response = json.loads(response.text)
        if response.status_code != 200:
            print('get_template', response)
        return response.status_code == 200

    def add_template_object_attribute(self, template_guid, attribute_name, child_attributes, attribute_tag):

        children = []

        sequence = 0
        for child_key, child_value in child_attributes.items():
            AttributeBaseObject = {
                'localName': child_key,
                "dataTypeGuid": IOTCTypes.to_guid(child_value),
                "sequence": sequence,
                # 'description' : "",
                # 'dataValidation' : '',
                # "unit": "string",
                # "startIndex": 0,
                # "numChar": 0,
                # "attributeColor": "string"
            }
            sequence += 1
            children.append(AttributeBaseObject)

        attribute_create_request = {
            "localName": attribute_name,
            "deviceTemplateGuid": template_guid,
            "dataTypeGuid": IOTCTypes.guids["OBJECT"],
            "tag": attribute_tag,
            "attributes": children,
            # "description": "string",
            # "dataValidation": "string",
            # "unit": "string",
            # "aggregateType": [
            #     "string"
            # ],
            # "tumblingatewayindow": "string",
            # "xmlAttributes": {},
            # "startIndex": 0,
            # "numChar": 0,
            # "attributeColor": "string"
        }

        response = requests.post(f"{API_DEVICE_URL}/template-attribute", timeout=self.timeout, headers=self.header, json=attribute_create_request)
        # response = json.loads(response.text)
        # for data in response["data"]:
        #     return data["newid"]
        print(f'obj attr "{attribute_name}": {response.json()["message"]}')

    def add_template_attribute(self, template_guid, attribute_name, attribute_type_guid, attribute_tag):
        attribute_create_request = {
            "localName": attribute_name,
            "deviceTemplateGuid": template_guid,
            "dataTypeGuid": attribute_type_guid,
            "tag": attribute_tag,
            # "description": "string",
            # "dataValidation": "string",
            # "unit": "string",
            # "aggregateType": [
            #     "string"
            # ],
            # "tumblingatewayindow": "string",
            # "attributes": [
            #     {
            #     "localName": "string",
            #     "description": "string",
            #     "dataValidation": "string",
            #     "dataTypeGuid": "string",
            #     "sequence": 0,
            #     "unit": "string",
            #     "startIndex": 0,
            #     "numChar": 0,
            #     "attributeColor": "string"
            #     }
            # ],
            # "xmlAttributes": {},
            # "startIndex": 0,
            # "numChar": 0,
            # "attributeColor": "string"
        }

        response = requests.post(f"{API_DEVICE_URL}/template-attribute", timeout=self.timeout, headers=self.header, json=attribute_create_request)
        response = json.loads(response.text)
        # for data in response["data"]:
        #     return data["newid"]
        try:
            msg = response["error"][0]["message"]
        except KeyError:
            msg = response["message"]
        print(f'attr "{attribute_name}": {msg}')

    def create_device(self, unique_id, template_guid, tag, name, entity_guid, parent_device_id=None):
        request = {
            "uniqueId": unique_id,
            "deviceTemplateGuid": template_guid,
            "tag": tag,
            "parentDeviceGuid": parent_device_id,
            "displayName": name,
            "entityGuid": entity_guid
            # "firmwareUpgradeGuid": "string",
            # "primaryThumbprint": "string",
            # "secondaryThumbprint": "string",
            # "endorsementKey": "string",
            # "properties": [
            #     {
            #     "guid": "string",
            #     "value": "string"
            #     }
            # ],
            # "xmlProperties": {},
            # "deviceCertificateGuid": "string",
            # "deviceCertificate": "string",
            # "deviceCertificatePassword": "string",
            # "primaryKey": "string",
            # "secondaryKey": "string",
            # "certificateText": "string",
            # "note": "string",
        }

        response = requests.post(f"{API_DEVICE_URL}/Device",
                                 timeout=self.timeout, headers=self.header, json=request)
        return response.status_code == 200

    @staticmethod
    def remove_chars(in_str, chars):
        return ''.join(c for c in in_str if c not in chars)

    def create_template_and_gateway_device_on_iotc(self, lora_gateway):

        # Create template
        template_guid = self.create_gateway_template(
            lora_gateway.template_data['code'],
            1,
            lora_gateway.tag(),
            lora_gateway.template_name()
        )
        lora_gateway.template_data['template_guid'] = template_guid
        # print('template_guid', template_guid)

        # Add gateways's attributes
        for attribute, value in lora_gateway.get_state().items():
            if isinstance(value, dict):
                self.add_template_object_attribute(template_guid, attribute, value, lora_gateway.tag())
                continue
            self.add_template_attribute(template_guid, attribute, IOTCTypes.to_guid(value), lora_gateway.tag())

        entity_guid = self.get_entity_guid(self.company_name)
        # Create Actual instance of gateway
        self.create_device(lora_gateway.unique_id, template_guid, lora_gateway.tag(), lora_gateway.name, entity_guid)
        lora_gateway.device_guid = self.get_device_guid(lora_gateway.name)
        return template_guid

    def create_child_on_iotc(self, gateway, child_obj):

        for attribute, value in child_obj.get_state().items():
            if isinstance(value, dict):
                self.add_template_object_attribute(
                    gateway.template_data['template_guid'],
                    attribute,
                    value,
                    child_obj.tag)
                continue
            self.add_template_attribute(gateway.template_data['template_guid'], attribute, IOTCTypes.to_guid(value), child_obj.tag)

        entity_guid = self.get_entity_guid(self.company_name)
        parent_device_guid = self.get_device_guid(gateway.name)

        self.create_device(child_obj.unique_id, gateway.template_data['template_guid'], child_obj.tag, child_obj.name, entity_guid, parent_device_guid)

    def delete_device_and_template(self, device_name):
        print(f'delete {device_name} and template from IOTC')
        try:
            device_guid = self.get_device_guid(device_name)
            self.delete_device(device_guid)
        except Exception as e:
            print('response from IOTC in delete_device', e)

        try:
            template_guid = self.get_template_guid(device_name)
            self.delete_template(template_guid)
        except Exception as e:
            print('response from IOTC in delete_template', e)

