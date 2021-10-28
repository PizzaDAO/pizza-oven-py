from typing import Any, Optional, Dict
from concurrent.futures import (
    ProcessPoolExecutor,
    ThreadPoolExecutor,
    wait,
    as_completed,
)

import requests
import sys
import time

import base58

from fastapi import status
from app.core.repository import get_render_task, set_render_task

from app.models.order import *
from app.core.recipe_box import get_pizza_recipe
from app.core.prep_line import reduce
from app.core.metadata import to_blockchain_metadata
from app.core.random_num import get_random_remote
from app.core.repository import *
from app.core.renderer import Renderer
from app.core.utils import from_hex, to_hex
from app.models.pizza import HotPizza
from app.models.prep import KitchenOrder
from app.models.recipe import Recipe
from app.models.render_task import RenderTask, TaskStatus

from app.core.config import ApiMode, Settings

settings = Settings()


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
    print(f"{render_task.job_id} - metadata_hash: {metadata_hash}")
    print(f"{render_task.job_id} - metadata_hash_len: {len(metadata_hash)}")
    print(f"{render_task.job_id} - from_bytes_big: {from_bytes_big}")
    print(f"{render_task.job_id} - decoded_metadata: {decoded_metadata}")
    print(f"{render_task.job_id} - decoded_metadata: {decoded_metadata.hex()}")
    print(f"{render_task.job_id} - truncated_metadata: {truncated_metadata}")
    print(f"{render_task.job_id} - truncated_metadata_len: {len(truncated_metadata)}")
    print("\n --------- YOUR PIZZA IS COMPLETE ---------- \n")
    print(f"\n    ipfs image: {metadata.image} \n")
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
        render_task.message = str(error)
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
        message = "the pizza order didnt complete"
        print(f"{render_task.job_id} - {message}")
        render_task.message = message
        render_task.set_status(TaskStatus.error)
        set_render_task(render_task)
        return None

    # if there's a chainlink callback specified,
    # then patch to the callback
    if render_task.request.responseURL is not None:
        print(f"{render_task.job_id} - issuing chainlink response.")

        # fetch the chainlink token needed to patch back
        chainlink_token = get_chainlink_token(render_task.request.data.bridge)
        if chainlink_token is None:
            print(f"{render_task.job_id} - no chainlink token found for job")
            return None

        try:

            # patch back to the node using the response url
            patch_response = requests.patch(
                render_task.request.responseURL,
                data=order_response.json(),
                headers={"authorization": f"Bearer {chainlink_token.inbound_token}"},
            )
            print(patch_response)

            # check the status code to make sure it was successful
            # before we mark the job complete
            if (
                patch_response.status_code >= status.HTTP_200_OK
                and patch_response.status_code < status.HTTP_300_MULTIPLE_CHOICES
            ):
                message = "post back to chainlink complete"
                print(f"{render_task.job_id} - {message}.")
                # update the job as complete
                render_task.message = message
                render_task.set_status(TaskStatus.complete)
                set_render_task(render_task)
                print(f"{render_task.job_id} - job complete!")
            else:
                print(f"{render_task.job_id} - chainlink postback failed")
                render_task.message = (
                    f"{patch_response.status_code} - {patch_response.text}"
                )
                render_task.set_status(TaskStatus.error)
                set_render_task(render_task)
        except Exception as error:
            print(
                f"{render_task.job_id} - chainlink postback failed with request error"
            )
            print(error)
            print(sys.exc_info())
            render_task.message = "chainlink postback failed with request error"
            render_task.set_status(TaskStatus.error)
            set_render_task(render_task)

    else:
        # chainlink wasnt specified so just mark the job complete
        message = "chainlink responseURL not specified"
        print(f"{render_task.job_id} - {message}")
        render_task.message = message
        render_task.set_status(TaskStatus.complete)
        set_render_task(render_task)
        print(f"{render_task.job_id} - job complete!")

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
        print(f"{job_id} - could not find job. searching for others.")
        render_tasks = pluck_render_tasks()
        if len(render_tasks) > 0:
            render_task = render_tasks[0]

    if render_task is None:
        print(f"{job_id} - could not find job.")
        # if settings.RERUN_SHOULD_RENDER_TASKS_RECUSRIVELY:
        #     print("recursively requeueing render tasks")
        #     rerun_render_jobs(settings.RERUN_JOB_STAGGERED_START_DELAY_IN_S)
        return None

    # if the job is already complete
    if render_task.status == TaskStatus.complete:
        print(f"{job_id} - job complete")
        completed_job_response = patch_and_complete_job(render_task)
        # if settings.RERUN_SHOULD_RENDER_TASKS_RECUSRIVELY:
        #     print("recursively requeueing render tasks")
        #     rerun_render_jobs(settings.RERUN_JOB_STAGGERED_START_DELAY_IN_S)
        return completed_job_response

    # check if the job finished but just didnt get marked complete
    if render_task.metadata_hash is not None:
        print(f"{job_id} - job finished rendering but wasn't complete")
        completed_job_response = patch_and_complete_job(render_task)
        # if settings.RERUN_SHOULD_RENDER_TASKS_RECUSRIVELY:
        #     print("recursively requeueing render tasks")
        #     rerun_render_jobs(settings.RERUN_JOB_STAGGERED_START_DELAY_IN_S)
        return completed_job_response

    # if the job is already in progress, skip it
    if not render_task.should_restart(settings.RENDER_TASK_RESTART_TIMEOUT_IN_MINUTES):
        print(f"{job_id} - job already in progress")
        # if settings.RERUN_SHOULD_RENDER_TASKS_RECUSRIVELY:
        #     print("recursively requeueing render tasks")
        #     rerun_render_jobs(settings.RERUN_JOB_STAGGERED_START_DELAY_IN_S)
        return None

    # set the job as started
    render_task.set_status(TaskStatus.started)
    render_task.message = None
    set_render_task(render_task)

    print("\n --------- PIZZA RENDER JOB STARTED ---------- \n")
    print("")
    print(f"    job_id:   {render_task.job_id}")
    print(f"    started:  {render_task.timestamp}")
    print(f"    token_id: {render_task.request.data.token_id}")
    print(f"    recipe:   {render_task.request.data.recipe_id}")
    print("")
    print("\n --------------------------------------------- \n")

    # transform the data

    # For names of pizza types see /data/recipes
    # they are index based
    recipe = get_pizza_recipe(render_task.request.data.recipe_id)
    if recipe is None:
        message = f"recipe_id {render_task.request.data.recipe_id} not found. did you run the setup task?"
        print(f"{render_task.job_id} - {message}")
        render_task.set_status(TaskStatus.error)
        render_task.message = message
        set_render_task(render_task)
        return None

    random_number = None

    # check if the render task already has a random number
    # which can happen if the rerun is restarted
    if render_task.random_number is not None:
        loaded_random = from_hex(render_task.random_number)
        print(
            f"{job_id} - rendering with render_task preloaded number: {loaded_random}"
        )
        random_number = loaded_random

    # get a random number and reduce the recipe into a kitchen order
    if random_number is None:
        random_number = get_random_remote(render_task.job_id)

    # if we didnt get a verifiable random number
    # then kill the job and allow it to be restart later
    # but we leave it marked "started" so that it
    # waits the full time out for another node to pick it up
    if random_number is None:
        render_task.message = "could not get a VRF random number"
        render_task.set_status(TaskStatus.started)
        set_render_task(render_task)
        # no recursive rerun function call here because this call
        # because if we get stuck in a loop calling the blockchain
        # we do not want to minimize transactions that fail
        return None

    # cache the random number since we know we have one
    render_task.random_number = to_hex(random_number)
    set_render_task(render_task)

    # resolve the kitchen order for natron from the input values
    kitchen_order = reduce(recipe, render_task.request.data.token_id, random_number)

    try:
        # render the pizza
        pizza = Renderer(
            frame=render_task.request.data.token_id, job_id=job_id
        ).render_pizza(kitchen_order)

    except Exception as error:
        print(sys.exc_info())
        print(f"{job_id} - {error}")
        render_task.message = str(error)
        render_task.set_status(TaskStatus.error)
        set_render_task(render_task)
        return None

    # cache the data and get a response object
    order_response = publish_order_result(render_task, recipe, kitchen_order, pizza)

    # update the task with the ipfs hash
    if order_response is not None:
        print(f"{job_id} - updating the task with the ipfs hash of the metadata")

        render_task.metadata_hash = order_response.data.metadata
        render_task.message = None
        set_render_task(render_task)

        completed_job_response = patch_and_complete_job(render_task, order_response)

        # if (
        #     completed_job_response is not None
        #     and settings.RERUN_SHOULD_RENDER_TASKS_RECUSRIVELY
        # ):
        #     print("recursively requeueing render tasks")
        # rerun_render_jobs(settings.RERUN_JOB_STAGGERED_START_DELAY_IN_S)

        return completed_job_response
    else:
        print(f"{job_id} - the order response was malformed.")

    message = "something went wrong. setting error state and returning none."
    print(f"{job_id} - {message}")
    render_task.set_status(TaskStatus.error)
    render_task.message = message
    set_render_task(render_task)
    return None


is_processing = False


def run_render_jobs(delay_in_s: int = 5):
    global is_processing
    if is_processing:
        print("run_render_jobs: already processing work")
        return
    print("run_render_jobs: starting render job loop")

    with ProcessPoolExecutor() as executor:
        is_processing = True

        added_task = 0
        futures = []
        tasks = pluck_render_tasks()
        if len(tasks) == 0:
            print("run_render_jobs: no tasks")
            is_processing = False
            return

        for task in tasks:
            # only schedule 3
            if added_task < settings.RERUN_MAX_CONCURRENT_RESCHEDULED_TASKS:
                print(f"run_render_jobs: {task.job_id} - scheduling")
                future = executor.submit(run_render_task, task.job_id)
                futures.append(future)
                added_task += 1
                time.sleep(delay_in_s)

        try:
            timeout = settings.RERUN_JOB_EXECUTION_TIMEOUT_IN_MINS * 60

            for future in as_completed(futures, timeout=timeout):
                if future.exception():
                    print("run_render_jobs: task failed")
                if future.result():
                    print("run_render_jobs: task suceeded")

                # result = future.result(
                #     timeout=settings.RERUN_JOB_EXECUTION_TIMEOUT_IN_MINS * 60
                # )
        except Exception as error:
            print(error)

        is_processing = False

        if settings.RERUN_SHOULD_RENDER_TASKS_RECUSRIVELY:
            print("run_render_jobs: recursively restarting jobs")
            run_render_jobs(settings.RERUN_JOB_STAGGERED_START_DELAY_IN_S)


def rerun_render_jobs(delay_in_s: int = 5):
    """rerun render jobs but staggering the startup"""
    render_tasks = pluck_render_tasks()
    added_task = 0
    for task in render_tasks:
        # only schedule 3
        if added_task < settings.RERUN_MAX_CONCURRENT_RESCHEDULED_TASKS:
            print(f"{task.job_id} - scheduling")

            time.sleep(3)
            schedule_task(task.job_id)
            added_task += 1

            time.sleep(delay_in_s)


executor2 = None


def schedule_task(job_id: str):
    global executor2
    if executor2 is None:
        # TODO: determine if we need to limit the worker pool
        # max_workers=3
        executor2 = ProcessPoolExecutor()

    if executor2 is not None:
        time.sleep(2)
        future = executor2.submit(run_render_task, job_id)


def executor_shutdown():
    global executor2
    if executor2 is not None:
        executor2.shutdown()
        executor2 = None
