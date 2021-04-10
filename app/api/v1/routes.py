from fastapi import APIRouter
from app.core.config import ApiMode, Settings
from . import common
from . import dining_room
from . import kitchen


def get_routes(settings: Settings) -> APIRouter:
    api_router = APIRouter()

    # demonstrate switch based on settings config
    if settings.API_MODE == ApiMode.development:
        # set any routes that are special to development
        # such as a local filesystem/datastore accessor
        pass
    elif settings.API_MODE == ApiMode.production:
        # set any routes that are special to production
        # such as a remote datastore accessor
        pass
    else:
        raise ValueError(f"Unknown API mode: {settings.API_MODE}")

    api_router.include_router(common.router)
    api_router.include_router(dining_room.router)
    api_router.include_router(kitchen.router)

    return api_router
