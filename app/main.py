from logging import getLogger
from typing import Optional
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.v1.routes import get_routes
from app.core.config import Settings

logger = getLogger(__name__)


def print_settings(settings: Settings):
    print(f"API_MODE                                - {settings.API_MODE}")
    print(f"STORAGE_MODE                            - {settings.STORAGE_MODE}")
    print(f"ETHEREUM_MODE                           - {settings.ETHEREUM_MODE}")
    print(f"IPFS_MODE                               - {settings.IPFS_MODE}")
    print(
        f"RENDER_TASK_TIMEOUT_IN_MINUTES          - {settings.BLOCKCHAIN_RESPONSE_TIMEOUT_IN_S}"
    )
    print(f"API_V1_STR                              - {settings.API_V1_STR}")
    print(f"PIZZA_TYPES_SHEET                       - {settings.PIZZA_TYPES_SHEET}")
    print(f"PIZZA_TYPE_RANGE_NAME                   - {settings.PIZZA_TYPE_RANGE_NAME}")
    print(
        f"PIZZA_INGREDIENTS_SHEET                 - {settings.PIZZA_INGREDIENTS_SHEET}"
    )
    print(
        f"INTERMEDIATE_FOLDER_PATH                - {settings.INTERMEDIATE_FOLDER_PATH}"
    )
    print(f"OUTPUT_FOLDER_PATH                      - {settings.OUTPUT_FOLDER_PATH}")
    print(f"lOCAL_RECIPES_PATH                      - {settings.lOCAL_RECIPES_PATH}")
    print(
        f"lOCAL_INGREDIENT_DB_MANIFEST_PATH       - {settings.lOCAL_INGREDIENT_DB_MANIFEST_PATH}"
    )
    print(
        f"LOCAL_INGREDIENT_DB_MANIFEST_FILENAME   - {settings.LOCAL_INGREDIENT_DB_MANIFEST_FILENAME}"
    )
    print(
        f"LOCAL_INGREDIENTS_DB_PATH               - {settings.LOCAL_INGREDIENTS_DB_PATH}"
    )


def get_app(settings: Optional[Settings] = None) -> FastAPI:
    if not settings:
        settings = Settings()

    web_app = FastAPI(
        title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
    )

    logger.error(f"Starting API in {settings.API_MODE} mode")

    print_settings(settings)

    # Set all CORS enabled origins
    if settings.BACKEND_CORS_ORIGINS:
        web_app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    routes = get_routes(settings)
    web_app.include_router(routes, prefix=settings.API_V1_STR)

    return web_app


# assign the application
app = get_app()


@app.on_event("shutdown")
def on_shutdown() -> None:
    # Ensure a clean shutdown of any background threads or processes
    pass


if __name__ == "__main__":
    # IMPORTANT: This should only be used to debug the application.
    # For normal execution, run `make start`.
    #
    # To make this work, the PYTHONPATH must be set to the root directory, e.g.
    # `PYTHONPATH=. poetry run python ./app/main.py`
    # See the VSCode launch configuration for detail.
    import uvicorn
    import argparse

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-p",
        "--port",
        default=8000,
        type=int,
        help="The port to listen on",
    )
    args = parser.parse_args()
    print("running uvicorn in development mode")
    uvicorn.run(app, host="0.0.0.0", port=args.port)
