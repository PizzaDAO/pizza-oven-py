import json

from app.models.recipe import Recipe
from app.models.prep import KitchenOrder
from app.models.pizza import HotPizza, RarePizzaMetadata

from app.core.recipe_box import sample
from app.core.ipfs_adapter import IPFSSession, PinataPy
from app.core.config import IPFSMode, Settings

__all__ = [
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


def get_recipe(recipe_id: int) -> Recipe:
    # TODO: real things
    return sample(recipe_id)


def set_recipe(recipe: Recipe) -> str:
    json_string = recipe.json()
    with IPFSSession(settings.IPFS_NODE_API) as session:
        return session.pin_json(json_string)


def get_kitchen_order(kitchen_order_id: int) -> KitchenOrder:
    pass


def set_kitchen_order(order: KitchenOrder) -> str:
    json_string = order.json()
    with IPFSSession(settings.IPFS_NODE_API) as session:
        return session.pin_json(json_string)


def get_pizza(pizza_id: int) -> HotPizza:
    pass


def set_pizza(pizza: HotPizza) -> str:
    json_string = pizza.json()
    with IPFSSession(settings.IPFS_NODE_API) as session:
        return session.pin_json(json_string)


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
