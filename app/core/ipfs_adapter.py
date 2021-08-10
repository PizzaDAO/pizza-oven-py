from contextlib import contextmanager
import os

import ipfshttpclient
from ipfshttpclient.client import Client


class IPFSSession:
    def __init__(self, server_uri: str):
        self.server_uri = server_uri
        self._client: Client

    def __enter__(self):
        self._client = ipfshttpclient.connect(self.server_uri, session=True)
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._client.close()

    def pin_json(self, json: str) -> str:
        """pin the json file to ipfs"""
        resource_hash = self._client.add_json(json)
        print(f"json_hash: {resource_hash}")
        return resource_hash

    def get_json(self, resource_hash: str) -> str:
        return self._client.get_json(resource_hash)
