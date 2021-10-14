from typing import Any, Optional, Dict

import requests
import time

import base58

from fastapi import APIRouter, Body, BackgroundTasks, Request

from app.models.base import Base
from app.models.order import PizzaOrder, PizzaOrderData
from app.core.recipe_box import get_pizza_recipe, make_recipe
from app.core.prep_line import reduce
from app.core.metadata import to_blockchain_metadata
from app.core.random_num import get_random
from app.core.repository import *
from app.core.renderer import Renderer
from ..tags import DELIVER

router = APIRouter()

CHAINLINK_AUTH_TOKEN = str
"this is the outgoing token in the chainlink node"
CHAINLINK_RESPONSE_TOKEN = str
"this is the incoming token in the chainlink node"

# Job tokens are required to communicate with the chainlink node
# the chainlink node web interface shows these tokens when you create a bridge.
# add your token to the list for testing only.  not for prod.
# TODO: cache this collection and make it runtime configurable
# so that the chainlink bridge can change.
chainlink_job_tokens: Dict[CHAINLINK_AUTH_TOKEN, CHAINLINK_RESPONSE_TOKEN] = {
    "Bearer nqpw1bzD4isqeYfXCixyAbhpLs/lkim4": "SI/8gEsllRRJLD5HDHH1/2ESG1RKmCOy"
}


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


def render_pizza(
    chainlink_auth_token: str, job_id: str, data: OrderPizzaRequest
) -> OrderPizzaResponse:
    print(data)

    # transform the data

    # For names of pizza types see /data/recipes
    # filenames are pizza types in alphabetical order
    recipe = get_pizza_recipe(data.data.recipe_index)

    # get a random number and reduce the recipe into a kitchen order
    random_number = get_random()
    kitchen_order = reduce(recipe, data.data.token_id, random_number)

    # render
    pizza = Renderer(frame=data.data.token_id, job_id=job_id).render_pizza(
        kitchen_order
    )

    # publish the pizza image to IPFS
    pizza_image_hash = set_pizza_image(pizza)
    pizza.assets["IPFS_HASH"] = pizza_image_hash

    # publish the pizza blockchain metadata
    metadata = to_blockchain_metadata(data.id, recipe, kitchen_order, pizza)
    metadata_hash = set_metadata(metadata)
    pizza.assets["METADATA_HASH"] = metadata_hash

    # publish the recipe, kitchen order, and the pizza object
    recipe_hash = set_recipe(recipe)
    order_hash = set_kitchen_order(kitchen_order)
    pizza_hash = set_pizza(pizza)

    decoded_metadata = base58.b58decode(metadata_hash)
    truncated_metadata = decoded_metadata[2 : len(decoded_metadata)]
    from_bytes_big = int.from_bytes(truncated_metadata, "big")

    # debug log out some values
    print(f"metadata_hash: {metadata_hash}")
    print(f"metadata_hash_len: {len(metadata_hash)}")
    print(f"from_bytes_big: {from_bytes_big}")
    print(f"decoded_metadata: {decoded_metadata}")
    print(f"decoded_metadata: {decoded_metadata.hex()}")
    print(f"truncated_metadata: {truncated_metadata}")
    print(f"truncated_metadata_len: {len(truncated_metadata)}")
    print("\n --------- YOUR PIZZA IS COMPLETE ---------- \n")
    print(f"\nipfs image: {metadata.image} \n")
    print("\n ------------------------------------------- \n")

    # build the response object
    response = OrderPizzaResponse(
        jobRunID=data.id,
        data=PizzaOrder(
            address=data.data.address,
            artwork=str(from_bytes_big),
            metadata=metadata_hash,
            recipe=recipe_hash,
            order=order_hash,
            pizza=pizza_hash,
        ),
        pending=False,
    )

    print(response.json())

    # if there's a chainlink callback specified,
    # then patch to the callback
    if data.responseURL is not None:
        print("issuing chainlink response.")
        # TODO: real login params loaded from an env var
        patch_response = requests.patch(
            data.responseURL,
            data=response.json(),
            headers={
                "authorization": f"Bearer {chainlink_job_tokens[chainlink_auth_token]}"
            },
        )
        print(patch_response.text)
    return response


@router.post("/order", response_model=OrderPizzaResponse, tags=[DELIVER])
async def orderPizza(
    request: Request,
    background_tasks: BackgroundTasks,
    data: OrderPizzaRequest = Body(...),
) -> OrderPizzaResponse:
    """
    order a pizza from the blockchain
    """

    # TODO: validate caller has the correct inbound auth token
    print(request.headers)

    # TODO ISSUE #32: cache a record of the incoming jobs
    # and add an api to query them.
    # allow for incomplete jobs to be queried and restarted.
    # allow for more than one job to be queued at a time

    response = OrderPizzaResponse(jobRunID=data.id, pending=True)
    background_tasks.add_task(
        render_pizza, request.headers["authorization"], data.id, data
    )

    return response


@router.post("/chainlink", response_model=OrderPizzaResponse, tags=[DELIVER])
async def testPatchChainlink(
    data: OrderPizzaRequest = Body(...),
) -> OrderPizzaResponse:
    # this is just for testing so just take the first key
    return render_pizza(list(chainlink_job_tokens.keys())[0], "abc-12345", data)
