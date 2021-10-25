from fastapi import APIRouter

from . import admin
from . import bake
from . import prep
from . import metadata
from . import tests

router = APIRouter()

router.include_router(admin.router, prefix="/admin")
router.include_router(prep.router, prefix="/kitchen")
router.include_router(tests.router, prefix="/tests")
router.include_router(bake.router, prefix="/oven")
router.include_router(metadata.router, prefix="/metadata")
