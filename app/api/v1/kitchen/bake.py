from typing import Any
from fastapi import APIRouter, Body
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from ....models.base import Base
from .prep import KitchenOrderRequest
from ....models.prep import *
from ....models.pizza import *
from ..tags import BAKE

router = APIRouter()


class HotPizzaResponse(Base):
    """a made pizza response"""

    pizza: HotPizza


def sample(order: KitchenOrder) -> HotPizza:
    """just a sample"""
    return HotPizza(
        unique_id=12345, order_id=order.unique_id, recipe_id=order.recipe_id, assets={}
    )


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
