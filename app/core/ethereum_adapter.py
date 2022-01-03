from typing import Any, Dict, List, Optional
from eth_typing import abi, Address

import os
import json
import time

from web3 import Web3
from web3.contract import Contract
from web3._utils.filters import LogFilter

from app.core.config import EthereumMode, EthereumNetworkChainId, Settings
from app.core.utils import to_hex

settings = Settings()


def get_server_uri() -> str:
    if settings.ETHEREUM_MODE == EthereumMode.mainnet:
        return settings.ETHEREUM_POLYGON_HTTP_SERVER
    return settings.ETHEREUM_MUMBAI_HTTP_SERVER


def get_chain_id() -> int:
    if settings.ETHEREUM_MODE == EthereumMode.mainnet:
        return EthereumNetworkChainId.matic
    return EthereumNetworkChainId.maticmum


def get_contract_address() -> str:
    if settings.ETHEREUM_MODE == EthereumMode.mainnet:
        return settings.ETHEREUM_MAINNET_CONTRACT_ADDRESS
    return settings.ETHEREUM_TESTNET_CONTRACT_ADDRESS


def get_account_address() -> str:
    if settings.ETHEREUM_MODE == EthereumMode.mainnet:
        return settings.ETHEREUM_MAINNET_ACCOUNT_ADDRESS
    return settings.ETHEREUM_TESTNET_ACCOUNT_ADDRESS


def get_private_key() -> str:
    if settings.ETHEREUM_MODE == EthereumMode.mainnet:
        return settings.ETHEREUM_MAINNET_PRIVATE_KEY
    return settings.ETHEREUM_TESTNET_PRIVATE_KEY


class EthereumAdapter:

    job_events: Dict[str, LogFilter] = {}

    def __init__(
        self,
        contract_address: str,
    ):
        print(f"connecting to contract: {contract_address}")
        self._client: Web3 = Web3(Web3.HTTPProvider(get_server_uri()))
        # Address
        self._contract: Contract = self._client.eth.contract(
            address=Web3.toChecksumAddress(contract_address), abi=self._load_abi()
        )

    def get_random_number(self, job_id: str) -> Optional[int]:
        """get a random number for the job id"""

        # Strip the job id and covert it to bytes
        stripped = job_id.replace("-", "")
        job_id_bytes = bytes.fromhex(stripped)
        print(f"{job_id} - querying VRF for jobId: {stripped}")

        try:

            # try to find the number if it exists already
            existing = self.find_random_number(job_id_bytes)
            if existing != 0:
                print(f"{job_id} - existing VRF found")
                return existing

            nonce = self._client.eth.get_transaction_count(get_account_address())
            print(f"{job_id} - account: {get_account_address()} nonce: {nonce}")

            # build the transaction
            tx = self._contract.functions.getRandomNumber(
                job_id_bytes
            ).buildTransaction(
                {
                    "chainId": get_chain_id(),
                    "from": get_account_address(),
                    "nonce": nonce,
                }
            )
            # 'maxFeePerGas': self._client.toWei(250, 'gwei'),
            # 'maxPriorityFeePerGas': self._client.toWei(2.5, 'gwei'),

            print(tx)

            # sign the transaction
            signed_tx = self._client.eth.account.sign_transaction(
                tx, private_key=get_private_key()
            )

            print(signed_tx)

            # TODO: cache the Tx? or something else that allows recovery
            # in the event we can't get the random number in the time
            # or another error occurs

            # braodcast the transaction
            self._client.eth.send_raw_transaction(signed_tx.rawTransaction)

            # wait for a response
            random_number = self.wait_for_random_number(job_id_bytes)
            if random_number != 0:
                print(f"{job_id} - VRF success: {random_number}")
                return random_number

        except Exception as error:
            print(error)
        return None

    def wait_for_random_number(self, job_id_bytes: bytes) -> int:
        random_number = 0

        loops = settings.BLOCKCHAIN_RESPONSE_TIMEOUT_IN_S / 15
        current = 0
        while True:
            # query for the number we need
            random_number = self.find_random_number(job_id_bytes)
            if random_number != 0:
                return random_number

            # if it wasnt found wait a bit
            if current < loops:
                current += 1
                time.sleep(15)
            else:
                print("waiting for VRF random number timed out. the job must be re-run")
                break
        return random_number

    def find_random_number(self, job_id_bytes: bytes) -> Any:
        """query for an existing random number"""
        return self._contract.get_function_by_name("getPizzaSeed")(job_id_bytes).call()

    def _load_abi(self) -> Any:
        with open("data/contracts/RarePizzasSeedStorage.json") as json_file:
            return json.load(json_file)["abi"]
