from fastapi import APIRouter

from . import bake
from . import prep
from . import metadata

router = APIRouter()

router.include_router(prep.router, prefix="/kitchen")
router.include_router(bake.router, prefix="/oven")
router.include_router(metadata.router, prefix="/metadata")
