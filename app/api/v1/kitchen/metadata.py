from typing import Any
from fastapi import APIRouter, Body
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.models.base import Base
from app.models.recipe import Recipe
from app.models.prep import KitchenOrder
from app.models.pizza import HotPizza, RarePizzaMetadata
from app.core.metadata import to_blockchain_metadata
from ..tags import METADATA

router = APIRouter()


class RarePizzaMetadataRequest(Base):
    """a made pizza response"""

    recipe: Recipe
    order: KitchenOrder
    pizza: HotPizza


@router.post("/{job_id}", response_model=RarePizzaMetadata, tags=[METADATA])
def get_metadata(job_id: str, request: RarePizzaMetadataRequest = Body(...)) -> Any:
    """
    get the metadata of a specific pizza
    """

    # TODO: get data from ipfs or the database or something

    metadata = to_blockchain_metadata(
        job_id, request.recipe, request.order, request.pizza
    )

    json = jsonable_encoder(metadata)
    return JSONResponse(content=json)
