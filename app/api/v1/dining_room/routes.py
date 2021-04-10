from fastapi import APIRouter

from . import order
from . import recipe

router = APIRouter()

router.include_router(order.router, prefix="/diningroom")
router.include_router(recipe.router, prefix="/recipe")
