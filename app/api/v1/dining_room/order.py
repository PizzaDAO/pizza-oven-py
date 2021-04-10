from typing import Any
from fastapi import APIRouter, Body
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from ..models.order import sample, OrderPizzaRequest, OrderPizzaResponse
from ..tags import DELIVER

router = APIRouter()


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