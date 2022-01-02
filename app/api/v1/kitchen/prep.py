from typing import Any
from fastapi import APIRouter, Body, Query
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from starlette import status
from app.core.repository import get_kitchen_order, get_kitchen_order_from_data_directory


from app.models.base import Base
from app.models.prep import KitchenOrderResponse
from app.core.prep_line import reduce
from app.core.utils import from_hex

from app.core.config import IPFSMode, Settings

from ..dining_room.recipe import RecipeRequest
from ..tags import PREP

router = APIRouter()
settings = Settings()


@router.post("/preparePizza", response_model=KitchenOrderResponse, tags=[PREP])
def prepare_pizza(data: RecipeRequest = Body(...)) -> Any:
    """
    prepares a recipe for baking by reducing instruction ranges to scalars
    """
    if data.random_seed is None:
        data = reduce(data.recipe, data.token_id)
    else:
        print(f"reducing recipe with random_seed in_hex: {data.random_seed}")
        data = reduce(data.recipe, data.token_id, from_hex(data.random_seed))
    json = jsonable_encoder(data)
    return JSONResponse(content=json)


@router.get("/kitchen_order", response_model=KitchenOrderResponse, tags=[PREP])
def fetch_kitchen_order(ipfs_hash=Query(...)) -> KitchenOrderResponse:
    """
    Fetch a kitchen order
    """
    # get the kitchen order
    if settings.IPFS_MODE == IPFSMode.local:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="only works in ipfs or pinata modes",
        )
    else:
        return KitchenOrderResponse(order=get_kitchen_order(ipfs_hash))
