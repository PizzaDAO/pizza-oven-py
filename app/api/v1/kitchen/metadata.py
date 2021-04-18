from typing import Any
from fastapi import APIRouter, Body
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.models.base import Base
from app.models.recipe import Recipe
from app.models.prep import KitchenOrder
from app.models.pizza import HotPizza, RarePizzaMetadata
from app.core.metadata import to_blockchain_metadata
from app.core.repository import get_metadata, set_metadata
from ..tags import METADATA

router = APIRouter()


class RarePizzaMetadataRequest(Base):
    """a request for blockchain metadata made from constituent parts"""

    recipe: Recipe
    order: KitchenOrder
    pizza: HotPizza


class RarePizzaMetadataResponse(Base):
    """metadata response for the blockchain"""

    ipfs_hash: str
    metadata: RarePizzaMetadata


@router.get("/{ipfs_hash}", response_model=RarePizzaMetadataResponse, tags=[METADATA])
def get_blockchain_metadata(ipfs_hash: str) -> Any:
    """
    get the metadata for the specific pizza
    """

    metadata = get_metadata(ipfs_hash)
    data = RarePizzaMetadataResponse(ipfs_hash=ipfs_hash, metadata=metadata)

    json = jsonable_encoder(data)
    return JSONResponse(content=json)


@router.post("/{job_id}", response_model=RarePizzaMetadataResponse, tags=[METADATA])
def set_blockchain_metadata(
    job_id: str, request: RarePizzaMetadataRequest = Body(...)
) -> Any:
    """
    set the metadata for the specific pizza
    """

    # TODO: get data from ipfs or the database or something

    metadata = to_blockchain_metadata(
        job_id, request.recipe, request.order, request.pizza
    )

    ipfs_hash = set_metadata(metadata)

    data = RarePizzaMetadataResponse(ipfs_hash=ipfs_hash, metadata=metadata)

    json = jsonable_encoder(data)
    return JSONResponse(content=json)
