from typing import Any
from fastapi import APIRouter, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from app.models.base import Base
from ..tags import UTILITY
from app.core.ingredients_db import *

""" -This is a FastAPI endpoint that should be called at the beginning of a session
    -It will read from the Google sheets (ingredients_db, and Pizza_types)
    -It saves JSON files for all the pizza recipes in data/recipes for later use"""

router = APIRouter()


class SetupRequest(Base):
    """an inbound setup request"""

    status: str


class SetupResponse(Base):
    """an outbound setup response"""

    status: str


@router.get("", response_model=SetupResponse, tags=[UTILITY])
def setup() -> SetupResponse:
    """
    Gather all the recipes from Google Sheets
    """

    # TODO - Better error handling/reporting would be helpful here... Just sends back if it was successful or not
    success = True
    try:
        read_ingredients()
    except:
        success = False

    try:
        read_recipes()
    except:
        success = False

    response = SetupResponse(status=success)

    return response
