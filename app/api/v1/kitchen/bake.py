from typing import Any
from fastapi import APIRouter, Body
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.models.base import Base
from app.models.pizza import HotPizza
from app.core.renderer import Renderer

from .prep import KitchenOrderRequest
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

    pizza = Renderer(frame=request.order.token_id).render_pizza(
        request.job_id, request.order
    )

    json = jsonable_encoder(pizza)
    return JSONResponse(content=json)
