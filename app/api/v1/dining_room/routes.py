from fastapi import APIRouter

from . import recipe

router = APIRouter()

router.include_router(recipe.router, prefix="/diningroom")
