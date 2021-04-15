from typing import Any
from fastapi import APIRouter, Body
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from ....models.base import Base
from ....models.order import PizzaOrder, PizzaOrderData
from .recipe import Recipe, sample
from ....core.prep_line import reduce
from ....core.renderer import Renderer
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

    recipe = sample(1)
    order = reduce(recipe)

    pizza = Renderer().render_pizza(order)

    # TODO: all the things like save to IPFS, etc.

    response = OrderPizzaResponse(
        jobRunID=request.id,
        data=PizzaOrder(
            address=request.data.address,
            artwork=pizza.assets["IPFS_ID"],
        ),
    )

    json = jsonable_encoder(response)
    return JSONResponse(content=json)