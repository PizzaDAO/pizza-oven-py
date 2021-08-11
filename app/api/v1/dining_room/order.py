from typing import Any, Optional

import time

from fastapi import APIRouter, Body, BackgroundTasks, Request

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
    meta: Optional[Any]
    responseURL: Optional[str]


class OrderPizzaResponse(Base):
    """A response for a pizza order, as the chainlink oracle expects"""

    jobRunID: str
    data: Any = {}
    error: Optional[str] = None
    pending: bool = False


@router.post("/order", response_model=OrderPizzaResponse, tags=[DELIVER])
async def orderPizza(
    request: Request,
    background_tasks: BackgroundTasks,
    request_data: OrderPizzaRequest = Body(...),
) -> OrderPizzaResponse:
    """
    order a pizza from the blockchain
    """

    # TODO: validate caller has the correct inbound auth token
    print(request.headers)

    # TODO: probably move this logic somewhere else

    # we need to keep a record of the incoming jobs and allow somoene to query them when they are complete
    # sol we basically need a document store or something in order to get the pizzas out

    def test_patch():
        # transform the data
        recipe = make_recipe()
        order = reduce(recipe)

        # render
        pizza = Renderer().render_pizza(order)

        # cache the objects in the respecitve repositories
        metadata = to_blockchain_metadata(request_data.id, recipe, order, pizza)
        ipfs_hash = set_metadata(metadata)
        pizza.assets["IPFS_HASH"] = ipfs_hash

        set_recipe(recipe)
        set_kitchen_order(order)
        set_pizza(pizza)

        response = OrderPizzaResponse(
            jobRunID=request_data.id,
            data=PizzaOrder(
                address=request_data.data.address,
                artwork=pizza.assets["IPFS_HASH"],
            ),
            pending=False,
        )
        print(request_data)
        print(response)
        # TODO: real login params loaded from the env
        # TODO: node refusing connections
        # requests.patch(
        #     request_data.responseURL,
        #     data=response.dict(),
        #     headers={"authorization": "Bearer gj87ru9gfj73429hyg8r3q"},
        # )

    response = OrderPizzaResponse(jobRunID=request_data.id, pending=True)
    background_tasks.add_task(test_patch)

    return response
