from typing import Any
import sys
from fastapi import APIRouter, Body, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from requests.sessions import requote_uri


from app.models.base import Base
from app.models.prep import KitchenOrder
from app.core.prep_line import reduce
from app.core.utils import from_hex
from app.core.repository import get_kitchen_order

from ..dining_room.recipe import RecipeRequest
from ..tags import TEST

from app.core.renderer import Renderer
import app.core.custom_ko as custom_ko

router = APIRouter()


class KitchenOrderRequest(Base):
    """an inbound order request"""

    job_id: str
    order: KitchenOrder


class KitchenOrderResponse(Base):
    """an outbound order response"""

    order: KitchenOrder


@router.get(
    "/ingredient/{ingredient_id}", response_model=KitchenOrderResponse, tags=[TEST]
)
def ingredient(ingredient_id: str) -> Any:
    """
    Get a specific recipe from the kitchen (by id)
    """
    ko = custom_ko.get_kitchen_order(ingredient_id)

    if int(ingredient_id) < 4000:
        return "Ingredient ID must be above 4000"

    json = jsonable_encoder(ko)
    return JSONResponse(content=json)


@router.post("/kitchen/order", tags=[TEST])
def kitchen_order(request: Request, skip: int = 0, limit: int = 100) -> Any:
    """
    run a set of predefined kitchen orders as a test
    """

    # iterate through each of the kitchen orders
    # and run them
    for i in range(skip, limit):
        kitchen_order = get_kitchen_order(i)

        try:
            # render the pizza
            pizza = Renderer(
                frame=i, job_id=f"test-kitchen-order-{str(i)}"
            ).render_pizza(kitchen_order)

            # TODO: publish out the pizza somewhere it can be viewed, like dropbox

        except Exception as error:
            print(sys.exc_info())
            print(error)

    return
