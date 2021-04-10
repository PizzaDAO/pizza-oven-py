from fastapi import APIRouter

from . import bake
from . import prep

router = APIRouter()

router.include_router(prep.router, prefix="/kitchen")
router.include_router(bake.router, prefix="/oven")
