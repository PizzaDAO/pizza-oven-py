from concurrent.futures import ProcessPoolExecutor
from logging import getLogger
from typing import Optional
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.v1.dining_room.dining_setup import setup
from app.api.v1.routes import get_routes
from app.core.config import ApiMode, Settings
from app.core.order_task import run_render_jobs

logger = getLogger(__name__)

settings = Settings()


def print_settings(_settings: Settings):
    print(f"API_MODE                                - {_settings.API_MODE}")
    print(f"STORAGE_MODE                            - {_settings.STORAGE_MODE}")
    print(f"ETHEREUM_MODE                           - {_settings.ETHEREUM_MODE}")
    print(f"IPFS_MODE                               - {_settings.IPFS_MODE}")
    print(
        f"RENDER_TASK_RESTART_TIMEOUT_IN_MINUTES  - {_settings.RENDER_TASK_RESTART_TIMEOUT_IN_MINUTES}"
    )
    print(
        f"DINING_SETUP_SHOULD_EXEC_ON_STARTUP     - {_settings.DINING_SETUP_SHOULD_EXEC_ON_STARTUP}"
    )
    print(
        f"RERUN_SHOULD_EXECUTE_ON_STARTUP         - {_settings.RERUN_SHOULD_EXECUTE_ON_STARTUP}"
    )
    print(
        f"RERUN_SHOULD_RENDER_TASKS_RECUSRIVELY   - {_settings.RERUN_SHOULD_RENDER_TASKS_RECUSRIVELY}"
    )
    print(
        f"RERUN_JOB_STAGGERED_START_DELAY_IN_S    - {_settings.RERUN_JOB_STAGGERED_START_DELAY_IN_S}"
    )
    print(
        f"RERUN_JOB_EXECUTION_TIMEOUT_IN_MINS     - {_settings.RERUN_JOB_EXECUTION_TIMEOUT_IN_MINS}"
    )
    print(
        f"RERUN_MAX_CONCURRENT_RESCHEDULED_TASKS  - {_settings.RERUN_MAX_CONCURRENT_RESCHEDULED_TASKS}"
    )
    print(f"API_V1_STR                              - {_settings.API_V1_STR}")
    print(f"PIZZA_TYPES_SHEET                       - {_settings.PIZZA_TYPES_SHEET}")
    print(
        f"PIZZA_TYPE_RANGE_NAME                     - {_settings.PIZZA_TYPE_RANGE_NAME}"
    )
    print(
        f"PIZZA_INGREDIENTS_SHEET                 - {_settings.PIZZA_INGREDIENTS_SHEET}"
    )
    print(
        f"INTERMEDIATE_FOLDER_PATH                - {_settings.INTERMEDIATE_FOLDER_PATH}"
    )
    print(f"OUTPUT_FOLDER_PATH                      - {_settings.OUTPUT_FOLDER_PATH}")
    print(f"lOCAL_RECIPES_PATH                      - {_settings.lOCAL_RECIPES_PATH}")
    print(
        f"lOCAL_INGREDIENT_DB_MANIFEST_PATH       - {_settings.lOCAL_INGREDIENT_DB_MANIFEST_PATH}"
    )
    print(
        f"LOCAL_INGREDIENT_DB_MANIFEST_FILENAME   - {_settings.LOCAL_INGREDIENT_DB_MANIFEST_FILENAME}"
    )
    print(
        f"LOCAL_INGREDIENTS_DB_PATH               - {_settings.LOCAL_INGREDIENTS_DB_PATH}"
    )


def get_app(_settings: Optional[Settings] = None) -> FastAPI:
    if not _settings:
        _settings = Settings()

    web_app = FastAPI(
        title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
    )

    logger.error(f"Starting API in {settings.API_MODE} mode")

    print_settings(_settings)

    # Set all CORS enabled origins
    if settings.BACKEND_CORS_ORIGINS:
        web_app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    routes = get_routes(_settings)
    web_app.include_router(routes, prefix=settings.API_V1_STR)

    return web_app


# assign the application
app = get_app()


@app.on_event("startup")
async def startup():
    if settings.DINING_SETUP_SHOULD_EXEC_ON_STARTUP:
        print("running dining setup on startup")
        setup()

    # in production mode, schedule the render jobs
    if settings.RERUN_SHOULD_EXECUTE_ON_STARTUP:
        print("running render jobs on startup")
        run_render_jobs(settings.RERUN_JOB_STAGGERED_START_DELAY_IN_S)


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
