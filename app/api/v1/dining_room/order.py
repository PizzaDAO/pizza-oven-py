from typing import Any

from fastapi import APIRouter, Body, Request, BackgroundTasks
from app.core.repository import get_render_task, set_render_task, get_order_response

from app.models.order import *
from app.core.order_task import run_render_jobs
from app.models.render_task import RenderTask, TaskStatus
from ..tags import DELIVER

from app.core.config import Settings

router = APIRouter()
settings = Settings()


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

    # cache the render task
    existing_job = get_render_task(data.id)
    if existing_job is not None:
        print(f"{existing_job.job_id} - job exists!")
        if existing_job.status == TaskStatus.complete:
            # try to return the job if it's finished
            response = get_order_response(data.id)
            if response is not None:
                print(f"{existing_job.job_id} - job complete, returning")
                return response
            # let all other cases fall through

    else:

        print(f"{data.id} - existing job not found, caching")
        set_render_task(
            RenderTask(
                job_id=data.id,
                request_token=request.headers["authorization"],
                request=data,
                status=TaskStatus.new,
            )
        )

    response = OrderPizzaResponse(jobRunID=data.id, pending=True)
    background_tasks.add_task(
        run_render_jobs, settings.RERUN_JOB_STAGGERED_START_DELAY_IN_S
    )
    # run_render_jobs(settings.RERUN_JOB_STAGGERED_START_DELAY_IN_S)
    return response
