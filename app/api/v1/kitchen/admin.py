from typing import Any, Optional, Dict

import requests
import sys

from fastapi import APIRouter, Body, BackgroundTasks, Request
from app.api.v1.dining_room.order import run_render_task

from app.core.repository import *
from app.models.chainlink_token import ChainlinkToken
from app.models.render_task import RenderTask
from app.models.order import OrderPizzaResponse

from ..tags import ADMIN

from app.core.config import Settings

router = APIRouter()
settings = Settings()


@router.post("/add_chainlink_token", tags=[ADMIN])
async def add_chainlink_token(
    data: ChainlinkToken = Body(...),
) -> Any:
    set_chainlink_token(data)
    return


@router.get("/render_task/{job_id}", tags=[ADMIN])
async def get_existing_render_task(job_id: str) -> Optional[RenderTask]:
    render_task = get_render_task(job_id)
    return render_task


@router.post("/render_task/{job_id}/rerun", tags=[ADMIN])
async def rerun_existing_render_task(job_id: str) -> Optional[OrderPizzaResponse]:
    render_task = get_render_task(job_id)
    if render_task is None:
        print("re run render failed")
        return None
    return run_render_task(render_task.job_id, render_task)
