from fastapi import APIRouter

from . import order
from . import recipe
from . import dining_setup

router = APIRouter()

router.include_router(order.router, prefix="/diningroom")
router.include_router(recipe.router, prefix="/recipe")
router.include_router(dining_setup.router, prefix="/dining_setup")
