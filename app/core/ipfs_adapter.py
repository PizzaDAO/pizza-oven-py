from contextlib import contextmanager
import os

import ipfshttpclient
from ipfshttpclient.client import Client
from ipfshttpclient.client.base import ResponseBase


class IPFSSession:
    def __init__(self, server_uri: str):
        self.server_uri = server_uri
        self._client: Client

    def __enter__(self):
        self._client = ipfshttpclient.connect(self.server_uri, session=True)
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._client.close()

    def pin_resource(self, path: str) -> str:
        """pin a resource"""
        response = self._client.add(path)
        print(f"response: {response.as_json()}")
        if isinstance(response, ResponseBase):
            return response["Hash"]
        else:
            return "not yet implemented"

    def pin_json(self, json: str) -> str:
        """pin the json file to ipfs"""
        resource_hash = self._client.add_json(json)
        print(f"json_hash: {resource_hash}")
        return resource_hash

    def get_json(self, resource_hash: str) -> str:
        return self._client.get_json(resource_hash)
