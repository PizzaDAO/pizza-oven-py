from typing import Any
from fastapi import APIRouter, Body
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from requests.sessions import requote_uri


from app.models.base import Base
from app.models.prep import KitchenOrder
from app.core.prep_line import reduce
from app.core.utils import from_hex

from ..dining_room.recipe import RecipeRequest
from ..tags import PREP

from app.core.custom_ko import get_kitchen_order

router = APIRouter()


class KitchenOrderRequest(Base):
    """an inbound order request"""

    job_id: str
    order: KitchenOrder


class KitchenOrderResponse(Base):
    """an outbound order response"""

    order: KitchenOrder


@router.get(
    "/ingredient/{ingredient_id}", response_model=KitchenOrderResponse, tags=[PREP]
)
def ingredient(ingredient_id: str) -> Any:
    """
    Get a specific recipe from the kitchen (by id)
    """
    ko = get_kitchen_order(ingredient_id)

    if int(ingredient_id) < 4000:
        return "Ingredient ID must be above 4000"

    json = jsonable_encoder(ko)
    return JSONResponse(content=json)