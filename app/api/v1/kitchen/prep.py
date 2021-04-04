from typing import Any
from fastapi import APIRouter, Body
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from ..models.recipe import RecipeRequest
from ..models.prep import KitchenOrderResponse, sample

from ..tags import PREP

router = APIRouter()


@router.post("/preparePizza", response_model=KitchenOrderResponse, tags=[PREP])
def prepare_pizza(request: RecipeRequest = Body(...)) -> Any:
    """
    prepares a recipe for baking by reducing instruction ranges to scalars
    """

    # TODO: things like get random numbers then deterministically generate
    # a kitchen order based on the recipe

    data = sample(request.recipe)
    json = jsonable_encoder(data)
    return JSONResponse(content=json)
