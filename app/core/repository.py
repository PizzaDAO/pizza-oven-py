import json
import sys
from typing import Optional
from app.models.order import OrderPizzaResponse
from app.models.render_task import RenderTask

from app.models.chainlink_token import ChainlinkToken
from app.models.recipe import Recipe
from app.models.prep import KitchenOrder
from app.models.pizza import HotPizza, RarePizzaMetadata

from app.core.ipfs_adapter import IPFSSession, PinataPy
from app.core.config import IPFSMode, Settings
from app.core.storage import *

__all__ = [
    "get_render_task",
    "set_render_task",
    "get_chainlink_token",
    "set_chainlink_token",
    "get_order_response",
    "set_order_response",
    "get_recipe",
    "set_recipe",
    "get_kitchen_order",
    "set_kitchen_order",
    "get_pizza",
    "set_pizza",
    "set_pizza_image",
    "get_metadata",
    "set_metadata",
]

settings = Settings()

# these api's are stored on the file system or in firebase, or in ipfs


def get_render_task(job_id: str) -> Optional[RenderTask]:
    try:
        with get_storage(DataCollection.render_task) as storage:
            result = storage.get({"job_id": job_id})
            return RenderTask(**result)
    except Exception as error:
        print(sys.exc_info())
        print(error)
        return None


def set_render_task(task: RenderTask) -> str:
    try:
        with get_storage(DataCollection.render_task) as storage:
            return storage.set(task.dict(), f"render_task-{task.job_id}")
    except Exception as error:
        print(sys.exc_info())
        raise error


def get_chainlink_token(inbound_token: str) -> Optional[ChainlinkToken]:
    try:
        with get_storage(DataCollection.chainlink_tokens) as storage:
            result = storage.get({"inbound_token": inbound_token})
            return ChainlinkToken(**result)
    except Exception as error:
        print(sys.exc_info())
        print(error)
        return None


def set_chainlink_token(name: str, inbound_token: str, outbound_token) -> str:
    try:
        token = ChainlinkToken(
            inbound_token=inbound_token, outbound_token=outbound_token
        )
        with get_storage(DataCollection.chainlink_tokens) as storage:
            return storage.set(token.dict(), f"chainlink_token-{name}")
    except Exception as error:
        print(sys.exc_info())
        raise error


def get_order_response(job_id: str) -> Optional[OrderPizzaResponse]:
    try:
        with get_storage(DataCollection.order_responses) as storage:
            result = storage.get({"job_id": job_id})
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


# Everything below here is on IPFS


def get_kitchen_order(ipfs_hash: int) -> KitchenOrder:
    with IPFSSession(settings.IPFS_NODE_API) as session:
        return KitchenOrder(**json.load(session.get_json(ipfs_hash)))


def set_kitchen_order(order: KitchenOrder) -> str:
    json_string = order.json()
    print("set_kitchen_order:")
    print(json_string)

    if settings.IPFS_MODE == IPFSMode.remote:
        print("pinning using local node")
        with IPFSSession(settings.IPFS_NODE_API) as session:
            return session.pin_json(order.dict())
    elif settings.IPFS_MODE == IPFSMode.pinata:
        print("pinning using pinata")
        return PinataPy(
            settings.PINATA_API_KEY, settings.PINATA_API_SECRET
        ).pin_json_to_ipfs(json_string)["IpfsHash"]
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
        ).pin_json_to_ipfs(json_string)["IpfsHash"]
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


def get_metadata(ipfs_hash: str) -> RarePizzaMetadata:
    with IPFSSession(settings.IPFS_NODE_API) as session:
        return RarePizzaMetadata(**json.load(session.get_json(ipfs_hash)))


def set_metadata(metadata: RarePizzaMetadata) -> str:
    json_string = metadata.json()
    print("set_metadata:")
    print(json_string)

    if settings.IPFS_MODE == IPFSMode.remote:
        print("pinning using local node")
        with IPFSSession(settings.IPFS_NODE_API) as session:
            return session.pin_json(metadata.dict())
    elif settings.IPFS_MODE == IPFSMode.pinata:
        print("pinning using pinata")
        return PinataPy(
            settings.PINATA_API_KEY, settings.PINATA_API_SECRET
        ).pin_json_to_ipfs(json_string)["IpfsHash"]
    else:
        print("pinning not implemented")
        return ""
