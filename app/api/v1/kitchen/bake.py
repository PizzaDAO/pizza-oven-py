from typing import Any
from fastapi import APIRouter, Body
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from ....models.base import Base
from .prep import KitchenOrderRequest
from ....models.prep import *
from ....models.pizza import *
from ....core.renderer import Renderer
from ..tags import BAKE

router = APIRouter()


class HotPizzaResponse(Base):
    """a made pizza response"""

    pizza: HotPizza


@router.post("/bake", response_model=HotPizzaResponse, tags=[BAKE])
def bake_pizza(request: KitchenOrderRequest = Body(...)) -> Any:
    """
    Bake the pizza!
    """

    pizza = Renderer().render_pizza(request.order)

    # TODO: all the things save out the assets, populate IPFS, etc.

    json = jsonable_encoder(pizza)
    return JSONResponse(content=json)
