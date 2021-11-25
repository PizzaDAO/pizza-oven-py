import os
from typing import Any
import sys
import uuid
from fastapi import APIRouter, Body, Request, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


from app.models.base import Base
from app.models.prep import KitchenOrder
from app.core.prep_line import reduce
from app.core.utils import from_hex, to_hex
from app.core.repository import get_kitchen_order_from_data_directory, set_render_task
from app.models.render_task import RenderTask, TaskStatus
from app.models.order import OrderPizzaRequest, PizzaOrderData
from app.core.random_num import get_random
from ..dining_room.recipe import RecipeRequest
from ..tags import TEST
from app.core.order_task import run_render_jobs

from app.core.renderer import Renderer
import app.core.custom_ko as custom_ko

from app.core.dropbox_adapter import DropboxSession

from app.core.config import Settings

router = APIRouter()
settings = Settings()


class KitchenOrderRequest(Base):
    """an inbound order request"""

    job_id: str
    order: KitchenOrder


class KitchenOrderResponse(Base):
    """an outbound order response"""

    order: KitchenOrder


@router.get(
    "/ingredient/{ingredient_id}", response_model=KitchenOrderResponse, tags=[TEST]
)
def test_get_ingredient(ingredient_id: str) -> Any:
    """
    Get a specific recipe from the kitchen (by id)
    """
    ko = custom_ko.get_kitchen_order(ingredient_id)

    if int(ingredient_id) < 4000:
        return "Ingredient ID must be above 4000"

    json = jsonable_encoder(ko)
    return JSONResponse(content=json)


@router.post("/order", tags=[TEST])
def test_kitchen_order(request: Request, skip: int = 0, limit: int = 100) -> Any:
    """
    run a set of predefined kitchen orders as a test
    """

    # iterate through each of the kitchen orders
    # and run them
    for i in range(skip, limit):
        # get orders from /data as list

        kitchen_order = get_kitchen_order_from_data_directory(i)

        try:
            # render the pizza
            pizza = Renderer(
                frame=i, job_id=f"test-kitchen-order-{str(i)}"
            ).render_pizza(kitchen_order)

            # publish out the pizza to Dropbox
            DropboxSession().send_image_file(pizza.assets["IMAGE_PATH"])

            print("Pizza is complete! moving to next...")

        except Exception as error:
            print(sys.exc_info())
            print(error)

    print("All pizzas in session are complete. nice job!")

    return


@router.post("/order-pizza", tags=[TEST])
def test_order_pizza(
    background_tasks: BackgroundTasks, recipe_id: int, skip: int = 0, limit: int = 100
) -> Any:
    """
    run a set of predefined kitchen orders as a test
    """

    # iterate through each of the kitchen orders
    # and run them
    for i in range(skip, limit):
        try:
            job_id = uuid.uuid1()
            set_render_task(
                RenderTask(
                    job_id=str(job_id),
                    request_token="",
                    request=OrderPizzaRequest(
                        id=str(job_id),
                        data=PizzaOrderData(
                            bridge="orderpizzav1",
                            address="0xTESTING",
                            token_id=1000 + i,
                            recipe_id=recipe_id,
                            requestor="0xTESTING",
                        ),
                    ),
                    status=TaskStatus.new,
                    random_number=to_hex(get_random()),
                )
            )

        except Exception as error:
            print(sys.exc_info())
            print(error)

    print("All pizzas in session are complete. nice job!")
    background_tasks.add_task(
        run_render_jobs, settings.RERUN_JOB_STAGGERED_START_DELAY_IN_S
    )

    return
