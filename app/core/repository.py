from app.models.recipe import Recipe
from app.models.prep import KitchenOrder
from app.models.pizza import HotPizza, RarePizzaMetadata

from app.core.recipe_box import sample

__all__ = [
    "get_recipe",
    "set_recipe",
    "get_kitchen_order",
    "set_kitchen_order",
    "get_pizza",
    "set_pizza",
    "get_metadata",
    "set_metadata",
]


def get_recipe(recipe_id: int) -> Recipe:
    # TODO: real things
    return sample(recipe_id)


def set_recipe(recipe: Recipe) -> bool:
    return True


def get_kitchen_order(kitchen_order_id: int) -> KitchenOrder:
    pass


def set_kitchen_order(order: KitchenOrder) -> bool:
    return True


def get_pizza(pizza_id: int) -> HotPizza:
    pass


def set_pizza(pizza: HotPizza) -> bool:
    return True


def get_metadata(hash: str) -> RarePizzaMetadata:
    pass


def set_metadata(metadata: RarePizzaMetadata) -> str:
    return "j7g53hygfweb6y8jgnur39"
