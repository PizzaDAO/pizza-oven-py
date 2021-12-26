from typing import Any, Optional, Dict
from fastapi.param_functions import Query
from pydantic.main import BaseModel

import requests
import sys

from fastapi import APIRouter, Body, BackgroundTasks, Request, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from google.oauth2.credentials import Credentials

from app.core.order_task import render_and_post, run_render_task, run_render_jobs

from app.core.prep_line import revise_kitchen_order

from app.core.repository import *
from app.core.recipe_box import get_pizza_recipe
from app.models.base import BaseQueryRequest
from app.models.auth_tokens import ChainlinkToken, GSheetsToken
from app.models.render_task import RenderTask, TaskStatus
from app.models.order import OrderPizzaResponse
from app.models.prep import KitchenOrder, KitchenOrderResponse, KitchenOrderRequest

from ..tags import ADMIN

from app.core.config import Settings, OvenToppingParams

router = APIRouter()
settings = Settings()


class KitchenOrderRerunRequest(BaseModel):
    order: KitchenOrder
    task: RenderTask


# TOKEN UPDATES


@router.post("/gsheets_token", tags=[ADMIN])
async def add_gsheets_token(
    data: GSheetsToken = Body(...),
) -> Any:
    return set_gsheets_token(data)


@router.get("/gsheets_token", tags=[ADMIN])
async def fetch_gsheets_token() -> Optional[GSheetsToken]:
    return get_gsheets_token()


@router.post("/add_chainlink_token", tags=[ADMIN])
async def add_chainlink_token(
    data: ChainlinkToken = Body(...),
) -> Any:
    """add a chainlink token"""
    set_chainlink_token(data)
    return


# OVEN PARAMS


@router.post("/oven_params", tags=[ADMIN])
async def add_oven_params(
    data: OvenToppingParams = Body(...),
) -> Any:
    return set_oven_params(data)


@router.get("/oven_params", tags=[ADMIN])
async def fetch_oven_params() -> OvenToppingParams:
    return get_oven_params()


# KITCHEN ORDER


@router.post("/kitchen_order/rerun", tags=[ADMIN])
async def rerun_kitchen_order(
    data: KitchenOrderRerunRequest = Body(...),
) -> Optional[OrderPizzaResponse]:
    """
    rerun a specific kitchen order.

    Useful for when a published kitchen order needs its data updated,
    but you do not want to re-roll the ingredients.

    This endpoint will regenerate the pie and post it to ipfs.

    In order to actually update the token, it must be done by the contract admin.
    """

    recipe = get_pizza_recipe(data.task.request.data.recipe_id)
    kitchen_order = revise_kitchen_order(data.order)
    return render_and_post(recipe, kitchen_order, data.task)


@router.post("/kitchen_order/revise", response_model=KitchenOrderResponse, tags=[ADMIN])
def revise_order(data: KitchenOrderRequest = Body(...)) -> Any:
    """
    Revise data in a kitchen order for a published pizza pie.

    Useful for when a published kitchen order needs its data updated,
    but you do not want to re-roll the ingredients.

    This is used when regenerating pies to inspect the data that will be used to render.
    """

    kitchen_order = revise_kitchen_order(data.order)

    json = jsonable_encoder(kitchen_order)
    return JSONResponse(content=json)


# RENDER TASKS


@router.get("/render_task/job/{job_id}", tags=[ADMIN])
async def get_existing_render_task(job_id: str = Query(...)) -> Optional[RenderTask]:
    """get an existing render task"""
    render_task = get_render_task(job_id)
    return render_task


@router.get("/render_task/find", tags=[ADMIN])
async def find_existing_render_tasks(
    data: BaseQueryRequest = Body(...),
) -> Optional[RenderTask]:
    """find existing render tasks according to the supplied filter"""
    render_tasks = find_render_task(data.filter)
    return render_tasks


@router.get("/pluck_render_task", tags=[ADMIN])
def pluck_render_tasks_for_restart() -> Any:
    """find an existing render tasks that are not marked complete."""
    render_tasks = pluck_render_tasks()
    return render_tasks


@router.post("/render_task_schedule_all", tags=[ADMIN])
def render_task_schedule_all() -> Any:
    """rerun all outstanding jobs"""
    run_render_jobs(settings.RERUN_MAX_CONCURRENT_RESCHEDULED_TASKS)


@router.post("/render_task", tags=[ADMIN])
async def set_existing_render_task(
    data: RenderTask = Body(...),
) -> Optional[str]:
    """
    set or update a specific render task.
    Note this endpoint is naive and does not consider
    wether an existing blockchain requests exists
    which means it can succeed in the render but fail
    when posting the transaction back to the contract
    """
    # TODO: update instead
    render_task = set_render_task(data)
    return render_task


@router.post("/render_task/{job_id}/rerun", tags=[ADMIN])
async def rerun_existing_render_task(job_id: str) -> Optional[OrderPizzaResponse]:
    """
    rerun a specific render task.

    useful if a job gets stuck and you want to debug it live.
    """
    render_task = get_render_task(job_id)
    if render_task is None:
        print(f"{job_id} - re run render failed to find job")
        return None
    render_task.status = TaskStatus.new
    render_task.metadata_hash = None
    return run_render_task(render_task.job_id, render_task)


@router.post("/render_task/{job_id}/rerun-async", tags=[ADMIN])
async def rerun_existing_render_task_async(
    job_id: str, background_tasks: BackgroundTasks
) -> Optional[OrderPizzaResponse]:
    """
    rerun a specific render task asynchronously.

    useful if a job gets stuck and you just want to queue it.
    """
    render_task = get_render_task(job_id)
    if render_task is None:
        print(f"{job_id} - re run render failed to find job")
        return None

    render_task.status = TaskStatus.new
    set_render_task(render_task)

    response = OrderPizzaResponse(jobRunID=render_task.job_id, pending=True)
    background_tasks.add_task(run_render_task, render_task.job_id, render_task)

    return response
