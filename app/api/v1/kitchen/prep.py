from typing import Any
from fastapi import APIRouter, Body
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


from app.models.base import Base
from app.models.prep import KitchenOrder
from app.core.prep_line import reduce
from app.core.utils import from_hex

from ..dining_room.recipe import RecipeRequest
from ..tags import PREP

router = APIRouter()


class KitchenOrderRequest(Base):
    """an inbound order request"""

    job_id: str
    order: KitchenOrder


class KitchenOrderResponse(Base):
    """an outbound order response"""

    order: KitchenOrder


@router.post("/preparePizza", response_model=KitchenOrderResponse, tags=[PREP])
def prepare_pizza(request: RecipeRequest = Body(...)) -> Any:
    """
    prepares a recipe for baking by reducing instruction ranges to scalars
    """
    if request.random_seed is None:
        data = reduce(request.recipe, request.token_id)
    else:
        print(f"reducing recipe with random_seed in_hex: {request.random_seed}")
        data = reduce(request.recipe, request.token_id, from_hex(request.random_seed))
    json = jsonable_encoder(data)
    return JSONResponse(content=json)
