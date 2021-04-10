from typing import Any
from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


from ..models.recipe import RecipeResponse, sample
from ..tags import ORDER

router = APIRouter()


@router.get("/{recipe_id}", response_model=RecipeResponse, tags=[ORDER])
def recipe(recipe_id: int) -> Any:
    """
    Order a recipe from the kitchen (by id)
    """
    # TODO: things like database lookups, etc.

    data = sample(recipe_id)
    json = jsonable_encoder(data)
    return JSONResponse(content=json)
