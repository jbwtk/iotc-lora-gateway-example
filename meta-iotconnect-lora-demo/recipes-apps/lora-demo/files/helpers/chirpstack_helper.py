import json

from google.protobuf.json_format import MessageToJson
from grpc import insecure_channel
from chirpstack_api.as_pb.external import api


class ChirpstackHelper(object):

    req_limit = 100

    def __init__(self, server_ip, token):
        print('authorise GRPC helper ...')
        self.auth_token = [("authorization", "Bearer %s" % token)]
        self.channel = insecure_channel(f'{server_ip}:8080')

    def list_gateways(self, req_limit=req_limit):
        client = api.GatewayServiceStub(self.channel)
        req = api.ListGatewayRequest()
        req.limit = req_limit
        response = client.List(req, metadata=self.auth_token)
        return json.loads(MessageToJson(response))['result']

    def list_service_profiles(self, req_limit=req_limit):
        client = api.ServiceProfileServiceStub(self.channel)
        req = api.ListServiceProfileRequest()
        req.limit = req_limit
        response = client.List(req, metadata=self.auth_token)
        return json.loads(MessageToJson(response))['result']

    def list_devices(self, service_profile_id=None, req_limit=req_limit):
        client = api.DeviceServiceStub(self.channel)
        req = api.ListDeviceRequest()
        req.limit = req_limit
        device_list = []
        if service_profile_id is None:
            service_profiles = self.list_service_profiles()
        else:
            service_profiles = [{'id': service_profile_id}]
        for s_profile in service_profiles:
            req.service_profile_id = s_profile['id']
            response = client.List(req, metadata=self.auth_token)
            json_obj = json.loads(MessageToJson(response))
            device_list = device_list + json_obj['result']
        return device_list

    def list_applications(self):
        client = api.ApplicationServiceStub(self.channel)
        req = api.ListApplicationRequest()
        req.limit = 100
        response = client.List(req, metadata=self.auth_token)
        # raw_json = MessageToJson(response)
        # json_obj = json.loads(raw_json)
        return json.loads(MessageToJson(response))['result']

    def list_tenants(self):
        pass
