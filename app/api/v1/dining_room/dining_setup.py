from typing import Any
from fastapi import APIRouter
from app.models.base import Base
from ..tags import UTILITY
from app.core.ingredients_db import *
from app.core.repository import set_recipe

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

    ingredients = read_ingredients()
    recipes = read_recipes(ingredients)
    for _, recipe in recipes.items():
        set_recipe(recipe)

    # save all the ingredients to a JSON file so we can access later
    save_ingredients(ingredients)

    return SetupResponse(status=True)
