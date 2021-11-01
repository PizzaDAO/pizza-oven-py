from typing import List
from enum import Enum
from pydantic import AnyHttpUrl, BaseSettings
from pydantic.fields import Field
from app.models.base import Base

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


class OvenToppingParams(Base):
    """vars from env config"""

    # Pizza Oven Config
    min_topping_layer_count: int = 3
    max_topping_layer_count: int = 6

    # Rarity
    rarity_weight_common: int = 2000
    rarity_weight_uncommon: int = 700
    rarity_weight_rare: int = 250
    rarity_weight_superrare: int = 100
    rarity_weight_epic: int = 50
    rarity_weight_grail: int = 25

    lastchance_occurance_percentage: int = 20

    # Scatter
    scatter_origin_x: int = 0
    scatter_origin_y: int = 0
    scatter_center_x: int = 1536
    scatter_center_y: int = 1536

    # circumference beyond which instances are pulled back to center
    prevent_overflow_control_diameter: int = 2900

    # Hero
    hero_random_offset_x: int = 0
    hero_random_offset_y: int = 0

    # FiveSpot
    five_spot_x_1: int = 850
    five_spot_y_1: int = 850
    five_spot_x_2: int = 2222
    five_spot_y_2: int = 850
    five_spot_x_3: int = 2222
    five_spot_y_3: int = 2222
    five_spot_x_4: int = 850
    five_spot_y_4: int = 2222
    five_spot_x_5: int = 1536
    five_spot_y_5: int = 1536
    five_spot_x_random_offset: int = 5
    five_spot_y_random_offset: int = 5

    # SpokeCluster
    spokecluster_inner_circle: int = 2800
    spokecluster_max_radius_offset: int = 200
    spokecluster_min_radius: int = 300

    # Grid
    grid_random_offset_x: int = 95
    grid_random_offset_y: int = 95
    grid_inner_circle: int = 2800
    grid_line_shift_offset: int = 90

    # Treering
    treerinng_inner_circle: int = 2800
    treering_min_radius: int = 100
    treering_variance_threshold: float = 0.5

    # random scatter
    random_inner_circle: int = 3052

    # scatter selection
    scatter_small_count_threshold: int = 5
    small_tier_1: int = 20
    small_tier_2: int = 60
    large_tier_1: int = 10
    large_tier_2: int = 40
    large_tier_3: int = 70


# pylint:disable=too-few-public-methods
class Settings(BaseSettings):
    """Settings for the app"""

    # Application
    API_MODE: ApiMode = ApiMode.development
    STORAGE_MODE: StorageMode = StorageMode.local
    ETHEREUM_MODE: EthereumMode = EthereumMode.testnet
    IPFS_MODE: IPFSMode = IPFSMode.remote

    RENDER_TASK_RESTART_TIMEOUT_IN_MINUTES: int = 15
    BLOCKCHAIN_RESPONSE_TIMEOUT_IN_S: int = 120

    DINING_SETUP_SHOULD_EXEC_ON_STARTUP = True

    RERUN_SHOULD_EXECUTE_ON_STARTUP = True
    RERUN_SHOULD_RENDER_TASKS_RECUSRIVELY = True
    RERUN_JOB_STAGGERED_START_DELAY_IN_S = 60
    RERUN_JOB_EXECUTION_TIMEOUT_IN_MINS = 20
    RERUN_MAX_CONCURRENT_RESCHEDULED_TASKS = 2

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

    class Config:
        case_sensitive = True
