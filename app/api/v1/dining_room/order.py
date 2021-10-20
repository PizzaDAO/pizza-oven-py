from typing import Any, Optional, Dict

import requests
import sys

import base58

from fastapi import APIRouter, Body, BackgroundTasks, Request
from app.core.repository import get_render_task, set_render_task

from app.models.base import Base
from app.models.order import *
from app.core.ethereum_adapter import get_contract_address, EthereumAdapter
from app.core.recipe_box import get_pizza_recipe
from app.core.prep_line import reduce
from app.core.metadata import to_blockchain_metadata
from app.core.random_num import get_random_remote
from app.core.repository import *
from app.core.renderer import Renderer
from app.models.pizza import HotPizza
from app.models.prep import KitchenOrder
from app.models.recipe import Recipe
from app.models.render_task import RenderTask, TaskStatus
from ..tags import DELIVER

from app.core.config import Settings

router = APIRouter()
settings = Settings()

# TODO: api's for querying storage
# api's for chainlink tokens


def publish_order_result(
    render_task: RenderTask,
    recipe: Recipe,
    kitchen_order: KitchenOrder,
    pizza: HotPizza,
) -> Optional[OrderPizzaResponse]:
    """publish data to ipfs and the datastore"""
    # publish the pizza image to IPFS
    pizza_image_hash = set_pizza_image(pizza)
    pizza.assets["IPFS_HASH"] = pizza_image_hash

    # publish the pizza blockchain metadata
    metadata = to_blockchain_metadata(render_task.job_id, recipe, kitchen_order, pizza)
    metadata_hash = set_metadata(metadata)
    pizza.assets["METADATA_HASH"] = metadata_hash

    # publish the kitchen order, and the pizza object
    order_hash = set_kitchen_order(kitchen_order)
    pizza_hash = set_pizza(pizza)

    # convert the metadata into a format chainlink can handle
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
        jobRunID=render_task.job_id,
        data=PizzaOrder(
            address=render_task.request.data.requestor,
            artwork=str(from_bytes_big),
            metadata=metadata_hash,
            order=order_hash,
            pizza=pizza_hash,
        ),
        pending=False,
    )

    try:
        # cache the response
        set_order_response(response)
        print(response.json())
    except Exception as error:
        print(sys.exc_info())
        print(error)
        render_task.set_status(TaskStatus.error)
        set_render_task(render_task)
        return None

    return response


def patch_and_complete_job(
    render_task: RenderTask, order_response: Optional[OrderPizzaResponse] = None
) -> Optional[OrderPizzaResponse]:
    """try to patch back to chainlink or just complete the order"""

    # check to see if we have an order response
    if order_response is None:
        order_response = get_order_response(render_task.job_id)

    # its possible something failed and wasn't caught
    # so we'll queue the job to re-run again
    if order_response is None:
        print("actually the pizza order didnt complete")
        render_task.set_status(TaskStatus.error)
        set_render_task(render_task)
        return None

    # if there's a chainlink callback specified,
    # then patch to the callback
    if render_task.request.responseURL is not None:
        print("issuing chainlink response.")

        # fetch the chainlink token needed to patch back
        chainlink_token = get_chainlink_token(render_task.request_token)
        if chainlink_token is None:
            print("no chainlink token found for job")
            return None

        patch_response = requests.patch(
            render_task.request.responseURL,
            data=order_response.json(),
            headers={"authorization": f"Bearer {chainlink_token}"},
        )
        print(patch_response.text)

        # update the job as complete
        render_task.set_status(TaskStatus.error)
        set_render_task(render_task)
    else:
        # chainlink wasnt specified to jsut mark the job complete
        render_task.set_status(TaskStatus.error)
        set_render_task(render_task)

    return order_response


def run_render_task(
    job_id: str, render_task: Optional[RenderTask] = None
) -> Optional[OrderPizzaResponse]:
    """Render a pizza"""

    # check to see if we already have a job
    if render_task is None:
        render_task = get_render_task(job_id)

    # if we didnt find a job, then just get any ole job
    if render_task is None:
        print("could not find job")
        # TODO: search for *any* job
        return None

    # if the job is already in progress, skip it
    if not render_task.should_restart():
        print("job in progress or already complete")
        return None

    # check if the job finished but just didnt get marked complete
    if render_task.metadata_hash is not None:
        print("job finished rendering but wasn't complete")
        return patch_and_complete_job(render_task)

    # set the job as started
    render_task.set_status(TaskStatus.started)
    set_render_task(render_task)

    # transform the data

    # For names of pizza types see /data/recipes
    # filenames are pizza types in alphabetical order
    recipe = get_pizza_recipe(render_task.request.data.recipe_id)

    # get a random number and reduce the recipe into a kitchen order
    random_number = get_random_remote(render_task.job_id)
    if random_number is None:
        # if we didnt get a verifiable random number
        # then kill the job and allow it to be restart later
        render_task.set_status(TaskStatus.error)
        set_render_task(render_task)
        return None

    # resolve the kitchen order for natron from the input values
    kitchen_order = reduce(recipe, render_task.request.data.token_id, random_number)

    try:
        # render the pizza
        pizza = Renderer(
            frame=render_task.request.data.token_id, job_id=job_id
        ).render_pizza(kitchen_order)

    except Exception as error:
        print(sys.exc_info())
        print(error)
        render_task.set_status(TaskStatus.error)
        set_render_task(render_task)
        return None

    # cache the data and get a response object
    order_response = publish_order_result(render_task, recipe, kitchen_order, pizza)

    # update the task with the ipfs hash
    if order_response is not None:
        print("updating the task with the ipfs hash of the metadata")

        render_task.metadata_hash = order_response.data["metadata"]
        set_render_task(render_task)

        return patch_and_complete_job(render_task, order_response)
    else:
        print("something went wrong. setting error state and returning none.")
        render_task.set_status(TaskStatus.error)
        set_render_task(render_task)
        return None


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
    print(data)

    # TODO ISSUE #32: cache a record of the incoming jobs
    # and add an api to query them.
    # allow for incomplete jobs to be queried and restarted.
    # allow for more than one job to be queued at a time

    # cache the render task
    existing_job = get_render_task(data.id)
    if existing_job is None:
        print("existing job not found, caching")
        set_render_task(
            RenderTask(
                job_id=data.id,
                request_token=request.headers["authorization"],
                request=data,
                status=TaskStatus.new,
            )
        )

    response = OrderPizzaResponse(jobRunID=data.id, pending=True)
    background_tasks.add_task(run_render_task, data.id)

    return response


@router.post("/test_vrf", tags=[DELIVER])
async def testVRF(
    data: OrderPizzaRequest = Body(...),
) -> Any:
    random_num = EthereumAdapter(get_contract_address()).get_random_number(data.id)
    return random_num


@router.post("/rerender_job", response_model=OrderPizzaResponse, tags=[DELIVER])
async def rerender_job(
    request: Request,
    data: OrderPizzaRequest = Body(...),
) -> Optional[OrderPizzaResponse]:
    """
    Send in a previous job to be rerendered, bypassing the cache lookup.
    unlike order_pizza this call is blocking.
    """
    render_task = RenderTask(
        job_id=data.id,
        request_token=request.headers["authorization"],
        request=data,
        status=TaskStatus.started,
    )
    return run_render_task(data.id, render_task)


# TODO: rerender if any?
