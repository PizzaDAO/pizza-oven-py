from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional

from app.models.recipe import Classification, Recipe
from app.models.prep import KitchenOrder, MadeIngredient
from app.models.pizza import HotPizza, RarePizzaMetadata

from .recipe_box import sample


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
