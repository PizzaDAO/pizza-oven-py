from typing import Any
from fastapi import APIRouter, Body
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from ..models.prep import KitchenOrderRequest
from ..models.pizza import sample, HotPizzaResponse
from ..tags import BAKE

router = APIRouter()


@router.post("/bake", response_model=HotPizzaResponse, tags=[BAKE])
def bake_pizza(request: KitchenOrderRequest = Body(...)) -> Any:
    """
    Bake the pizza!
    """

    # TODO: all the things like call natron, save out the assets
    # transform whatver data, etc.

    data = sample(request.order)

    json = jsonable_encoder(data)
    return JSONResponse(content=json)
