from typing import Any, Dict, List, Optional

import os
import requests

import ipfshttpclient
from ipfshttpclient.client import Client
from ipfshttpclient.client.base import ResponseBase

ResponsePayload = Dict[str, Any]
OptionsDict = Dict[str, Any]
Headers = Dict[str, str]

API_ENDPOINT: str = "https://api.pinata.cloud/"


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

    def pin_json(self, json: Any) -> str:
        """pin the json file to ipfs"""
        resource_hash = self._client.add_json(json)
        print(f"json_hash: {resource_hash}")
        return resource_hash

    def get_json(self, resource_hash: str) -> str:
        return self._client.get_json(resource_hash)


class PinataPy:
    """
    A pinata api client session object
    mostly this: https://github.com/Vourhey/pinatapy
    """

    def __init__(self, pinata_api_key: str, pinata_secret_api_key: str) -> None:
        self._auth_headers: Headers = {
            "pinata_api_key": pinata_api_key,
            "pinata_secret_api_key": pinata_secret_api_key,
        }

    @staticmethod
    def _error(response: requests.Response) -> ResponsePayload:
        """Construct dict from response if an error has occurred"""

        print(f"PinataPy:_error {response}")
        return {
            "status": response.status_code,
            "reason": response.reason,
            "text": response.text,
        }

    def pin_file_to_ipfs(
        self, path_to_file: str, options: Optional[OptionsDict] = None
    ) -> ResponsePayload:
        """
        Pin any file, or directory, to Pinata's IPFS nodes
        More: https://docs.pinata.cloud/api-pinning/pin-file
        """
        url: str = API_ENDPOINT + "pinning/pinFileToIPFS"
        headers: Headers = self._auth_headers

        def get_all_files(directory: str) -> List[str]:
            """get a list of absolute paths to every file located in the directory"""
            paths: List[str] = []
            for root, dirs, files_ in os.walk(os.path.abspath(directory)):
                for file in files_:
                    paths.append(os.path.join(root, file))
            return paths

        files: Dict[str, Any]

        if os.path.isdir(path_to_file):
            all_files: List[str] = get_all_files(path_to_file)
            files = {"file": [(file, open(file, "rb")) for file in all_files]}
        else:
            files = {"file": open(path_to_file, "rb")}

        if options is not None:
            if "pinataMetadata" in options:
                headers["pinataMetadata"] = options["pinataMetadata"]
            if "pinataOptions" in options:
                headers["pinataOptions"] = options["pinataOptions"]
        response: requests.Response = requests.post(
            url=url, files=files, headers=headers
        )
        return response.json() if response.ok else self._error(response)  # type: ignore

    def pin_to_pinata_using_ipfs_hash(
        self, ipfs_hash: str, filename: str
    ) -> ResponsePayload:
        """
        Pin file to Pinata using its IPFS hash
        https://docs.pinata.cloud/api-pinning/pin-by-hash
        """
        payload: OptionsDict = {
            "pinataMetadata": {"name": filename},
            "hashToPin": ipfs_hash,
        }
        url: str = API_ENDPOINT + "/pinning/pinByHash"
        response: requests.Response = requests.post(
            url=url, json=payload, headers=self._auth_headers
        )
        return self._error(response) if not response.ok else response.json()  # type: ignore

    def pin_jobs(self, options: Optional[OptionsDict] = None) -> ResponsePayload:
        """
        Retrieves a list of all the pins that are currently in the pin queue for your user.
        More: https://docs.pinata.cloud/api-pinning/pin-jobs
        """
        url: str = API_ENDPOINT + "pinning/pinJobs"
        payload: OptionsDict = options if options else {}
        response: requests.Response = requests.get(
            url=url, params=payload, headers=self._auth_headers
        )
        return response.json() if response.ok else self._error(response)  # type: ignore

    def get_from_gateway(self, ipfs_hash: str) -> ResponsePayload:
        """return the json"""
        response: requests.Response = requests.get(
            f"https://gateway.pinata.cloud/ipfs/{ipfs_hash}"
        )
        return response.json() if response.ok else self._error(response)

    def pin_json_to_ipfs(
        self, json_to_pin: Any, options: Optional[OptionsDict] = None
    ) -> ResponsePayload:
        """pin provided JSON"""

        url: str = API_ENDPOINT + "pinning/pinJSONToIPFS"
        headers: Headers = self._auth_headers
        headers["Content-Type"] = "application/json"
        payload: ResponsePayload = {"pinataContent": json_to_pin}
        if options is not None:
            if "pinataMetadata" in options:
                payload["pinataMetadata"] = options["pinataMetadata"]
            if "pinataOptions" in options:
                payload["pinataOptions"] = options["pinataOptions"]
        response: requests.Response = requests.post(
            url=url, json=payload, headers=headers
        )
        return response.json() if response.ok else self._error(response)  # type: ignore

    def remove_pin_from_ipfs(self, hash_to_remove: str) -> ResponsePayload:
        """Removes specified hash pin"""
        url: str = API_ENDPOINT + "pinning/removePinFromIPFS"
        headers: Headers = self._auth_headers
        headers["Content-Type"] = "application/json"
        body = {"ipfs_pin_hash": hash_to_remove}
        response: requests.Response = requests.post(url=url, json=body, headers=headers)
        return self._error(response) if not response.ok else {"message": "Removed"}

    def pin_list(self, options: Optional[OptionsDict] = None) -> ResponsePayload:
        """https://pinata.cloud/documentation#PinList"""
        url: str = API_ENDPOINT + "data/pinList"
        payload: OptionsDict = options if options else {}
        response: requests.Response = requests.get(
            url=url, params=payload, headers=self._auth_headers
        )
        return response.json() if response.ok else self._error(response)  # type: ignore

    def user_pinned_data_total(self) -> ResponsePayload:
        url: str = API_ENDPOINT + "data/userPinnedDataTotal"
        response: requests.Response = requests.get(url=url, headers=self._auth_headers)
        return response.json() if response.ok else self._error(response)  # type: ignore
