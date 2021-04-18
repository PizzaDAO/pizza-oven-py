from contextlib import contextmanager
import os

import ipfshttpclient


class IPFSSession:
    def __init__(self, server_uri: str):
        self.server_uri = server_uri

    def __enter__(self):
        self._client = ipfshttpclient.connect(self.server_uri, session=True)
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._client.close()

    def pin_json(self, json: str):
        """pin the json file to ipfs"""
        resource_hash = self._client.add_json(json)
        print(resource_hash)
        print(self._client.stat(resource_hash))

    def get_json(self, resource_hash: str) -> str:
        return self._client.get_json(resource_hash)
