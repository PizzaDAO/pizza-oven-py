from typing import Any, Optional
from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.models.base import Base
from app.models.recipe import Recipe
from app.core.recipe_box import get_pizza_recipe

from ..tags import ORDER

router = APIRouter()


class RecipeRequest(Base):
    """an inbound recipe request"""

    token_id: int
    random_seed: Optional[str] = None
    recipe: Recipe


class RecipeResponse(Base):
    """an outbound recipe response"""

    recipe: Recipe


@router.get("/{recipe_id}", response_model=RecipeResponse, tags=[ORDER])
def recipe(recipe_id: int) -> Any:
    """
    Get a specific recipe from the kitchen (by id)
    """

    pizza_recipe = get_pizza_recipe(recipe_id)
    json = jsonable_encoder(pizza_recipe)
    return JSONResponse(content=json)
