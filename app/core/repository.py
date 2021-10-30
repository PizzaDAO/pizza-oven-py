import json
import sys
import os
from typing import Optional, List
from os import listdir
from os.path import isfile, join
from collections.abc import MutableMapping

from app.models.order import OrderPizzaResponse
from app.models.render_task import RenderTask, TaskStatus

from app.models.auth_tokens import ChainlinkToken, GSheetsToken
from app.models.recipe import Recipe
from app.models.prep import KitchenOrder
from app.models.pizza import HotPizza, RarePizzaMetadata

from app.core.ipfs_adapter import IPFSSession, PinataPy
from app.core.config import IPFSMode, Settings, OvenToppingParams
from app.core.storage import *

__all__ = [
    "get_oven_params",
    "set_oven_params",
    "get_render_task",
    "pluck_render_tasks",
    "find_render_task",
    "set_render_task",
    "set_gsheets_token",
    "get_gsheets_token",
    "get_chainlink_token",
    "set_chainlink_token",
    "get_order_response",
    "set_order_response",
    "get_recipe",
    "set_recipe",
    "get_kitchen_order_from_data_directory",
    "get_kitchen_order",
    "set_kitchen_order",
    "get_pizza",
    "set_pizza",
    "set_pizza_image",
    "set_image_alpha",
    "get_metadata_from_ipfs",
    "get_metadata_from_storage",
    "set_metadata",
]

settings = Settings()


def get_oven_params() -> OvenToppingParams:
    try:
        with get_storage(DataCollection.oven_params) as storage:
            result = storage.get({"document_id": "oven_params"})
            # If we can't get OvenToppingParams just return default - one might not be stored locally?
            if not result:
                # print("Returning a default OvenToppingParams object")
                return OvenToppingParams()
            else:
                return OvenToppingParams(**result)
    except Exception as error:
        print(sys.exc_info())
        print(error)
        print("returning default")
        return OvenToppingParams()


def set_oven_params(oven_params: OvenToppingParams):
    try:
        with get_storage(DataCollection.oven_params) as storage:
            return storage.set(
                {"document_id": "oven_params", "auth": oven_params.dict()},
                "oven_params",
            )
    except Exception as error:
        print(sys.exc_info())
        raise error


# these api's are stored on the file system or in firebase, or in ipfs


def get_render_task(job_id: str) -> Optional[RenderTask]:
    try:
        with get_storage(DataCollection.render_task) as storage:
            result = storage.get({"job_id": job_id})
            if result is not None:
                return RenderTask(**result)
    except Exception as error:
        print(sys.exc_info())
        print(error)

    return None


def pluck_render_tasks() -> List[RenderTask]:
    print("plucking render tasks")
    render_tasks: List[RenderTask] = []

    found_tasks = find_render_task({"status": TaskStatus.new.name})
    print(f"found {len(found_tasks)} new tasks")
    for task in found_tasks:
        if task.should_restart(settings.RENDER_TASK_RESTART_TIMEOUT_IN_MINUTES):
            print(f"{task.job_id} - new, should restgart")
            render_tasks.append(task)

    found_tasks = find_render_task({"status": TaskStatus.started.name})
    print(f"found {len(found_tasks)} started tasks")
    for task in found_tasks:
        if task.should_restart(settings.RENDER_TASK_RESTART_TIMEOUT_IN_MINUTES):
            print(f"{task.job_id} - timed out, should restart")
            render_tasks.append(task)

    found_tasks = find_render_task({"status": TaskStatus.error.name})
    print(f"found {len(found_tasks)} errored tasks")
    for task in found_tasks:
        if task.should_restart(settings.RENDER_TASK_RESTART_TIMEOUT_IN_MINUTES):
            print(f"{task.job_id} - errored, should restart")
            render_tasks.append(task)

    print(f"returning {len(render_tasks)} candidates")
    return render_tasks


def find_render_task(filter: MutableMapping) -> List[RenderTask]:
    try:
        with get_storage(DataCollection.render_task) as storage:
            render_tasks: List[RenderTask] = []
            result = storage.find(filter)
            for item in result:
                render_tasks.append(RenderTask(**item))
            return render_tasks
    except Exception as error:
        print(sys.exc_info())
        print(error)
        return []


def set_render_task(task: RenderTask) -> str:
    try:
        with get_storage(DataCollection.render_task) as storage:
            return storage.set(task.dict(), f"render_task-{task.job_id}")
    except Exception as error:
        print(sys.exc_info())
        raise error


def set_gsheets_token(auth_token: GSheetsToken) -> str:
    try:
        with get_storage(DataCollection.gsheets_tokens) as storage:
            return storage.set({"name": "gsheets", "auth": auth_token.dict()}, "sheets")
    except Exception as error:
        print(sys.exc_info())
        raise error


def get_gsheets_token() -> Optional[GSheetsToken]:
    try:
        with get_storage(DataCollection.gsheets_tokens) as storage:
            result = storage.get({"name": "gsheets"})
            return GSheetsToken(**result["auth"])
    except Exception as error:
        print(sys.exc_info())
        print(error)
        # if we get an error, try to return the default
        return None


def get_chainlink_token(inbound_token: str) -> Optional[ChainlinkToken]:
    try:
        with get_storage(DataCollection.chainlink_tokens) as storage:
            result = storage.get({"inbound_token": inbound_token})
            return ChainlinkToken(**result)
    except Exception as error:
        print(sys.exc_info())
        print(error)
        # if we get an error, try to return the default
        return ChainlinkToken()


def set_chainlink_token(auth_token: ChainlinkToken) -> str:
    try:
        with get_storage(DataCollection.chainlink_tokens) as storage:
            return storage.set(auth_token.dict(), f"chainlink_token-{auth_token.name}")
    except Exception as error:
        print(sys.exc_info())
        raise error


def get_order_response(job_id: str) -> Optional[OrderPizzaResponse]:
    try:
        with get_storage(DataCollection.order_responses) as storage:

            result = storage.get({"jobRunID": job_id})
            return OrderPizzaResponse(**result)
    except Exception as error:
        print(sys.exc_info())
        print(error)
        return None


def set_order_response(response: OrderPizzaResponse) -> str:
    try:
        with get_storage(DataCollection.order_responses) as storage:
            return storage.set(response.dict(), f"order_response-{response.jobRunID}")
    except Exception as error:
        print(sys.exc_info())
        raise error


def get_recipe(recipe_id: int) -> Optional[Recipe]:
    try:
        with get_storage(DataCollection.recipes) as storage:
            result = storage.get({"unique_id": recipe_id})
            return Recipe(**result)
    except Exception as error:
        print(sys.exc_info())
        print(error)
        return None


def set_recipe(recipe: Recipe) -> str:
    try:
        with get_storage(DataCollection.recipes) as storage:
            return storage.set(recipe.dict(), f"recipe-{recipe.unique_id}")
    except Exception as error:
        print(sys.exc_info())
        raise error


def get_kitchen_order_from_data_directory(kitchen_order_index: int) -> KitchenOrder:
    # todo: just read it from the data directory

    current_directory = os.path.dirname(__file__)
    orders_path = os.path.split(current_directory)[0] + settings.KO_STRESS_TEST_PATH
    file_list = []
    try:
        for f in listdir(orders_path):
            if isfile(join(orders_path, f)) and "json" in f:
                file_list.append(f)

    except Exception:
        print("Failed to locate stress test KitchenOrders!")
    finally:
        try:
            file = file_list[kitchen_order_index]
            f = open(orders_path + file)
            kitchen_order = KitchenOrder(**json.load(f))
            f.close()

            return kitchen_order

        except Exception as e:
            print("KO stress test: failed to open kitchen order")
            print(e)

    # should never get here
    return KitchenOrder()


# Everything below here is on IPFS


def get_kitchen_order(ipfs_hash: int) -> KitchenOrder:
    with IPFSSession(settings.IPFS_NODE_API) as session:
        return KitchenOrder(**json.load(session.get_json(ipfs_hash)))


def set_kitchen_order(order: KitchenOrder) -> str:
    json_string = order.json()
    print(
        f"set_kitchen_order: token_id: {order.token_id} random_seed: {order.random_seed}"
    )

    if settings.IPFS_MODE == IPFSMode.remote:
        print("pinning using local node")
        with IPFSSession(settings.IPFS_NODE_API) as session:
            return session.pin_json(order.dict())
    elif settings.IPFS_MODE == IPFSMode.pinata:
        print("pinning using pinata")
        return PinataPy(
            settings.PINATA_API_KEY, settings.PINATA_API_SECRET
        ).pin_json_to_ipfs(order.dict())["IpfsHash"]
    else:
        print("pinning not implemented")
        return ""


def get_pizza(ipfs_hash: int) -> HotPizza:
    with IPFSSession(settings.IPFS_NODE_API) as session:
        return HotPizza(**json.load(session.get_json(ipfs_hash)))


def set_pizza(pizza: HotPizza) -> str:
    json_string = pizza.json()
    print("set_pizza:")
    print(json_string)

    if settings.IPFS_MODE == IPFSMode.remote:
        print("pinning using local node")
        with IPFSSession(settings.IPFS_NODE_API) as session:
            return session.pin_json(pizza.dict())
    elif settings.IPFS_MODE == IPFSMode.pinata:
        print("pinning using pinata")
        return PinataPy(
            settings.PINATA_API_KEY, settings.PINATA_API_SECRET
        ).pin_json_to_ipfs(pizza.dict())["IpfsHash"]
    else:
        print("pinning not implemented")
        return ""


def set_pizza_image(pizza: HotPizza) -> str:
    file_path = pizza.assets["IMAGE_PATH"]
    if settings.IPFS_MODE == IPFSMode.remote:
        print("pinning using local node")
        with IPFSSession(settings.IPFS_NODE_API) as session:
            return session.pin_resource(file_path)
    elif settings.IPFS_MODE == IPFSMode.pinata:
        print("pinning using pinata")
        return PinataPy(
            settings.PINATA_API_KEY, settings.PINATA_API_SECRET
        ).pin_file_to_ipfs(file_path)["IpfsHash"]
    else:
        print("pinning not implemented")
        return ""


def set_image_alpha(pizza: HotPizza) -> str:
    file_path = pizza.assets["ALPHA_PATH"]
    if settings.IPFS_MODE == IPFSMode.remote:
        print("pinning using local node")
        with IPFSSession(settings.IPFS_NODE_API) as session:
            return session.pin_resource(file_path)
    elif settings.IPFS_MODE == IPFSMode.pinata:
        print("pinning using pinata")
        return PinataPy(
            settings.PINATA_API_KEY, settings.PINATA_API_SECRET
        ).pin_file_to_ipfs(file_path)["IpfsHash"]
    else:
        print("pinning not implemented")
        return ""


def get_metadata_from_ipfs(ipfs_hash: str) -> RarePizzaMetadata:
    with IPFSSession(settings.IPFS_NODE_API) as session:
        return RarePizzaMetadata(**json.load(session.get_json(ipfs_hash)))


def get_metadata_from_storage(job_id: str) -> Optional[RarePizzaMetadata]:
    try:
        with get_storage(DataCollection.metadata) as storage:

            result = storage.get({"job_id": job_id})
            return RarePizzaMetadata(**result)
    except Exception as error:
        print(sys.exc_info())
        print(error)
        return None


def set_metadata(metadata: RarePizzaMetadata) -> str:
    json_string = metadata.json()
    print("set_metadata:")
    print(json_string)

    # metadata is set both in storage and in the blockchain

    try:
        with get_storage(DataCollection.metadata) as storage:
            storage.set(metadata.dict(), f"metadata-{metadata.job_id}")
    except Exception as error:
        print(sys.exc_info())
        # raise error
        # continue since ipfs is more important

    if settings.IPFS_MODE == IPFSMode.remote:
        print("pinning using local node")
        with IPFSSession(settings.IPFS_NODE_API) as session:
            return session.pin_json(metadata.dict())
    elif settings.IPFS_MODE == IPFSMode.pinata:
        print("pinning using pinata")
        return PinataPy(
            settings.PINATA_API_KEY, settings.PINATA_API_SECRET
        ).pin_json_to_ipfs(metadata.dict())["IpfsHash"]
    else:
        print("pinning not implemented")
        return ""
