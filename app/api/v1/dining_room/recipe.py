from typing import Any
from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from ....models.base import Base
from ....models.recipe import *
from ..tags import ORDER

from ....core.repository import get_recipe

router = APIRouter()


class RecipeRequest(Base):
    """an inbound recipe request"""

    recipe: Recipe


class RecipeResponse(Base):
    """an outbound recipe response"""

    recipe: Recipe


@router.get("/{recipe_id}", response_model=RecipeResponse, tags=[ORDER])
def recipe(recipe_id: int) -> Any:
    """
    Get a specific recipe from the kitchen (by id)
    """

    data = get_recipe(recipe_id)
    json = jsonable_encoder(data)
    return JSONResponse(content=json)
