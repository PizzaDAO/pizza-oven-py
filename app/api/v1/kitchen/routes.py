from fastapi import APIRouter

from app.api.v1.kitchen import ingredient_test

from . import admin
from . import bake
from . import prep
from . import metadata
from . import ingredient_test

router = APIRouter()

router.include_router(admin.router, prefix="/admin")
router.include_router(prep.router, prefix="/kitchen")
router.include_router(ingredient_test.router, prefix="/kitchen")
router.include_router(bake.router, prefix="/oven")
router.include_router(metadata.router, prefix="/metadata")
