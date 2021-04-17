from typing import Any
from fastapi import APIRouter, Body
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


from app.models.base import Base
from app.models.prep import KitchenOrder
from app.core.prep_line import reduce

from ..dining_room.recipe import RecipeRequest
from ..tags import PREP

router = APIRouter()


class KitchenOrderRequest(Base):
    """an inbound order request"""

    order: KitchenOrder


class KitchenOrderResponse(Base):
    """an outbound order response"""

    order: KitchenOrder


@router.post("/preparePizza", response_model=KitchenOrderResponse, tags=[PREP])
def prepare_pizza(request: RecipeRequest = Body(...)) -> Any:
    """
    prepares a recipe for baking by reducing instruction ranges to scalars
    """

    data = reduce(request.recipe)
    json = jsonable_encoder(data)
    return JSONResponse(content=json)
