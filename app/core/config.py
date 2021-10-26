from typing import List
from enum import Enum
from pydantic import AnyHttpUrl, BaseSettings
from pydantic.fields import Field

import os


class ApiMode(str, Enum):
    development = "development"
    production = "production"


class StorageMode(str, Enum):
    local = "local"
    firebase = "firebase"


class EthereumMode(str, Enum):
    testnet = "testnet"
    mainnet = "mainnet"


class IPFSMode(str, Enum):
    local = "local"
    remote = "remote"
    pinata = "pinata"


class EthereumNetworkChainId(int, Enum):
    mainnet = 1
    rinkeby = 4
    matic = 137
    maticmum = 80001


# pylint:disable=too-few-public-methods
class Settings(BaseSettings):
    """Settings for the app"""

    # Application
    API_MODE: ApiMode = ApiMode.development
    STORAGE_MODE: StorageMode = StorageMode.local
    ETHEREUM_MODE: EthereumMode = EthereumMode.testnet
    IPFS_MODE: IPFSMode = IPFSMode.remote

    RENDER_TASK_TIMEOUT_IN_MINUTES: int = 15
    BLOCKCHAIN_RESPONSE_TIMEOUT_IN_S: int = 120

    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = Field(
        default=["http://localhost", "http://localhost:8080", "https://localhost"]
    )
    PROJECT_NAME: str = "pizza-oven-py"

    # Ethereum
    ETHEREUM_RINKEBY_HTTP_SERVER: str = ""
    ETHEREUM_MUMBAI_HTTP_SERVER: str = ""
    ETHEREUM_MAINNET_HTTP_SERVER: str = ""
    ETHEREUM_POLYGON_HTTP_SERVER: str = ""

    ETHEREUM_TESTNET_ACCOUNT_ADDRESS: str = ""
    ETHEREUM_TESTNET_PRIVATE_KEY: str = ""

    ETHEREUM_MAINNET_ACCOUNT_ADDRESS: str = ""
    ETHEREUM_MAINNET_PRIVATE_KEY: str = ""

    ETHEREUM_TESTNET_CONTRACT_ADDRESS: str = ""
    ETHEREUM_MAINNET_CONTRACT_ADDRESS: str = ""

    # IPFS
    IPFS_NODE_API: str = "/dns/ipfs0/tcp/5001/http"
    PINATA_API_KEY = ""
    PINATA_API_SECRET = ""

    # Google Firebase
    GOOGLE_APPLICATION_CREDENTIALS = "secrets/firebase.dev.json"

    # Google Sheets
    # ingredients_db settings
    GOOGLE_SHEETS_TOKEN_PATH = "secrets/sheets.json"
    GOOGLE_SHEETS_CREDENTIALS_PATH = "secrets/credentials.json"
    SCOPE = "https://www.googleapis.com/auth/spreadsheets.readonly"
    PIZZA_TYPES_SHEET = "1xN149zkgSXPfJhDwQrIzlMzcU9gB--ihdoO_XJXCqf0"
    PIZZA_TYPE_RANGE_NAME = "recipe-db!A3:Q"
    PIZZA_INGREDIENTS_SHEET = "1xN149zkgSXPfJhDwQrIzlMzcU9gB--ihdoO_XJXCqf0"
    TOPPINGS_RANGE_NAME = "ingredients-db"

    # Dropbox - natron testing
    DROPBOX_TOKEN = ""

    # Misc ENV VARS
    DEFAULT_NATRON_EXECUTABLE_PATH = os.environ["NATRON_PATH"]
    DEFAULT_NATRON_PROJECT_PATH = os.environ["NATRON_PROJECT_PATH"]
    DEFAULT_NATRON_FRAME = 9

    DATA_FONT_SIZE = 64
    WATERMARK_FILE = "pizza_watermark.png"

    INTERMEDIATE_FOLDER_PATH = ".cache/intermediate"
    OUTPUT_FOLDER_PATH = ".cache/output"
    lOCAL_RECIPES_PATH = ".cache/local/recipes/"
    lOCAL_INGREDIENT_DB_MANIFEST_PATH = ".cache/local/"
    LOCAL_INGREDIENT_DB_MANIFEST_FILENAME = "ingredient_manifest.json"
    LOCAL_INGREDIENTS_DB_PATH = "ingredients-db"

    # Local Storage - Natron testing
    KO_STRESS_TEST_PATH = "/../data/ko_stress_test/"

    # Pizza Oven Config
    MIN_TOPPING_LAYER_COUNT = 1
    MAX_TOPPING_LAYER_COUNT = 4
    RARITY_WEIGHT_COMMON = 550
    RARITY_WEIGHT_UNCOMMON = 340
    RARITY_WEIGHT_RARE = 100
    RARITY_WEIGHT_GRAIL = 10
    LASTCHANCE_OCCURENCE_PERCENTAGE = 20

    class Config:
        case_sensitive = True
