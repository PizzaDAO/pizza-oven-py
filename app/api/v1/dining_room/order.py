from typing import Any
from fastapi import APIRouter, Body
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.models.base import Base
from app.models.order import PizzaOrder, PizzaOrderData
from app.core.recipe_box import make_recipe
from app.core.prep_line import reduce
from app.core.metadata import to_blockchain_metadata
from app.core.repository import *
from app.core.renderer import Renderer
from ..tags import DELIVER

router = APIRouter()


class OrderPizzaRequest(Base):
    """A request to order a pizza, coming from a chainlink oracle"""

    id: str
    data: PizzaOrderData


class OrderPizzaResponse(Base):
    """A response for a pizza order, as the chainlink oracle expects"""

    jobRunID: str
    data: PizzaOrder
    statusCode: int = 200


@router.post("/order", response_model=OrderPizzaResponse, tags=[DELIVER])
def orderPizza(request: OrderPizzaRequest = Body(...)) -> Any:
    """
    order a pizza from the blockchain
    """

    print(f"{request}")

    # TODO: probably move this logic somewhere else

    # transform the data
    recipe = make_recipe()
    order = reduce(recipe)

    # render
    pizza = Renderer().render_pizza(order)

    # cache the objects in the respecitve repositories
    metadata = to_blockchain_metadata(request.id, recipe, order, pizza)
    ipfs_hash = set_metadata(metadata)
    pizza.assets["IPFS_ID"] = ipfs_hash

    set_recipe(recipe)
    set_kitchen_order(order)
    set_pizza(pizza)

    response = OrderPizzaResponse(
        jobRunID=request.id,
        data=PizzaOrder(
            address=request.data.address,
            artwork=pizza.assets["IPFS_ID"],
        ),
    )

    json = jsonable_encoder(response)
    return JSONResponse(content=json)