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

    min_topping_layer_count: int = 1
    max_topping_layer_count: int = 4
    rarity_weight_common: int = 2000
    rarity_weight_uncommon: int = 700
    rarity_weight_rare: int = 250
    rarity_weight_superrare: int = 100
    rarity_weight_epic: int = 40
    rarity_weight_grail: int = 5
    lastchance_occurance_percentage: int = 20
    scatter_origin_x: int = 0
    scatter_origin_y: int = 0
    scatter_center_x: int = 1536
    scatter_center_y: int = 1536
    prevent_overflow_control_diameter: int = 2650
    hero_random_offset_x: int = 0
    hero_random_offset_y: int = 0
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
    spokecluster_inner_circle: int = 2800
    spokecluster_max_radius_offset: int = 200
    spokecluster_min_radius: int = 300
    grid_random_offset_x: int = 95
    grid_random_offset_y: int = 95
    grid_inner_circle: int = 2800
    grid_line_shift_offset: int = 90
    treerinng_inner_circle: int = 2800
    treering_min_radius: int = 100
    treering_variance_threshold: float = 0.5
    random_inner_circle: int = 3052
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
    MIN_TOPPING_LAYER_COUNT: int = 1
    MAX_TOPPING_LAYER_COUNT: int = 4

    LASTCHANCE_OCCURENCE_PERCENTAGE: int = 20

    # Rarity
    RARITY_WEIGHT_COMMON: int = 2000
    RARITY_WEIGHT_UNCOMMON: int = 700
    RARITY_WEIGHT_RARE: int = 250
    RARITY_WEIGHT_SUPERRARE: int = 100
    RARITY_WEIGHT_EPIC: int = 40
    RARITY_WEIGHT_GRAIL: int = 5

    # Scatter
    SCATTER_ORIGIN_X: int = 0
    SCATTER_ORIGIN_Y: int = 0
    SCATTER_CENTER_X: int = 1536
    SCATTER_CENTER_Y: int = 1536
    # circumference beyond which instances are pulled back to center
    PERVENT_OVERFLOW_CONTROL_DIAMETER: int = 2650
    # Hero
    HERO_RANDOM_OFFSET_X: int = 0
    HERO_RANDOM_OFFSET_Y: int = 0
    # FiveSpot
    FIVE_SPOT_X_1: int = 850
    FIVE_SPOT_Y_1: int = 850
    FIVE_SPOT_X_2: int = 2222
    FIVE_SPOT_Y_2: int = 850
    FIVE_SPOT_X_3: int = 2222
    FIVE_SPOT_Y_3: int = 2222
    FIVE_SPOT_X_4: int = 850
    FIVE_SPOT_Y_4: int = 2222
    FIVE_SPOT_X_5: int = 1536
    FIVE_SPOT_Y_5: int = 1536
    FIVE_SPOT_X_RANDOM_OFFSET: int = 5
    FIVE_SPOT_Y_RANDOM_OFFSET: int = 5
    # SpokeCluster
    SPOKECLUSTER_INNER_CIRCLE: int = 2800
    SPOKECLUSTER_MAX_RADIUS_OFFSET: int = 200
    SPOKECLUSTER_MIN_RADIUS: int = 300
    # Grid
    GRID_RANDOM_OFFSET_X: int = 95
    GRID_RANDOM_OFFSET_Y: int = 95
    GRID_INNER_CIRCLE: int = 2800
    GRID_LINE_SHIFT_OFFSET: int = 90
    # TreeRing
    TREERING_INNER_CIRCLE: int = 2800
    TREERING_MIN_RADIUS: int = 100
    TREERING_VARIANCE_THRESHOLD: float = 0.5
    # RandomScatter
    RANDOM_INNER_CIRCLE: int = 3052

    # Scatter Selection
    SCATTER_SMALL_COUNT_THRESHOLD: int = 5
    SMALL_TIER_1: int = 20
    SMALL_TIER_2: int = 60
    LARGE_TIER_1: int = 10
    LARGE_TIER_2: int = 40
    LARGE_TIER_3: int = 70

    class Config:
        case_sensitive = True
