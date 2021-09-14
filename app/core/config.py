from typing import List
from enum import Enum
from pydantic import AnyHttpUrl, BaseSettings
from pydantic.fields import Field

import os


class ApiMode(str, Enum):
    development = "development"
    production = "production"


# pylint:disable=too-few-public-methods
class Settings(BaseSettings):
    """Settings for the app"""

    API_MODE: ApiMode = ApiMode.development
    API_V1_STR: str = "/api/v1"
    DEFAULT_NATRON_EXECUTABLE_PATH = os.environ["NATRON_PATH"]
    DEFAULT_NATRON_PROJECT_PATH = os.environ["NATRON_PROJECT_PATH"]
    DEFAULT_NATRON_FRAME = 9
    IPFS_NODE_API: str = "/dns/ipfs0/tcp/5001/http"
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = Field(
        default=["http://localhost", "http://localhost:8080", "https://localhost"]
    )
    PROJECT_NAME: str = "pizza-oven-py"

    # ingredients_db settings
    # Are these overwritted by an env file??
    TOKEN_PATH = "data/sheets_auth_token.json"
    CREDENTIALS_PATH = "data/credentials.json"
    SCOPE = "https://www.googleapis.com/auth/spreadsheets.readonly"
    PIZZA_TYPES_SHEET = "1wHfP2I1m8_TV5tZt3FchI_zYgzZg9AomU7GOkof7TW8"
    PIZZA_TYPE_RANGE_NAME = "Jed - Pizza Types!A3:W"
    PIZZA_INGREDIENTS_SHEET = "1xN149zkgSXPfJhDwQrIzlMzcU9gB--ihdoO_XJXCqf0"
    TOPPINGS_RANGE_NAME = "ingredients-db"

    class Config:
        case_sensitive = True
