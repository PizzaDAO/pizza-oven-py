from typing import Any, Optional, Dict

import requests
import sys

from fastapi import APIRouter, Body, BackgroundTasks, Request
from google.oauth2.credentials import Credentials

from app.api.v1.dining_room.order import run_render_task

from app.core.repository import *
from app.models.auth_tokens import ChainlinkToken, GSheetsToken
from app.models.render_task import RenderTask, TaskStatus
from app.models.order import OrderPizzaResponse

from ..tags import ADMIN

from app.core.config import Settings, OvenToppingParams

router = APIRouter()
settings = Settings()


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


@router.post("/oven_params", tags=[ADMIN])
async def add_oven_params(
    data: OvenToppingParams = Body(...),
) -> Any:
    return set_oven_params(data)


@router.get("/oven_params", tags=[ADMIN])
async def fetch_oven_params() -> OvenToppingParams:
    return get_oven_params()


@router.get("/render_task/{job_id}", tags=[ADMIN])
async def get_existing_render_task(job_id: str) -> Optional[RenderTask]:
    """get an existing render task"""
    render_task = get_render_task(job_id)
    return render_task


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
    """rerun a specific render task"""
    render_task = get_render_task(job_id)
    if render_task is None:
        print(f"{job_id} - re run render failed to find job")
        return None
    return run_render_task(render_task.job_id, render_task)


@router.post("/render_task/{job_id}/rerun-async", tags=[ADMIN])
async def rerun_existing_render_task_async(
    job_id: str, background_tasks: BackgroundTasks
) -> Optional[OrderPizzaResponse]:
    """rerun a specific render task asynchronously"""
    render_task = get_render_task(job_id)
    if render_task is None:
        print(f"{job_id} - re run render failed to find job")
        return None

    render_task.status = TaskStatus.new
    set_render_task(render_task)

    response = OrderPizzaResponse(jobRunID=render_task.job_id, pending=True)
    background_tasks.add_task(run_render_task, render_task.job_id, render_task)

    return response
