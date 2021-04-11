from typing import Any
from fastapi import APIRouter, Body
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from ....models.base import Base
from ....models.order import PizzaOrder, PizzaOrderData
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


def sample(request: OrderPizzaRequest) -> OrderPizzaResponse:
    """just a sample"""

    return OrderPizzaResponse(
        jobRunID=request.id,
        data=PizzaOrder(
            address=request.data.address,
            artwork="QmZ4q72eVU3bX95GXwMXLrguybKLKavmStLWEWVJZ1jeyz",
        ),
    )


@router.post("/order", response_model=OrderPizzaResponse, tags=[DELIVER])
def orderPizza(request: OrderPizzaRequest = Body(...)) -> Any:
    """
    order a pizza from the blockchain
    """

    print(f"{request}")

    # TODO: all the things like call into the renderpielijne or whatever

    data = sample(request)

    json = jsonable_encoder(data)
    return JSONResponse(content=json)