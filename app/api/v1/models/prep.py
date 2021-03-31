from dataclasses import dataclass
from typing import Dict, List, NamedTuple

from .base import Base

from .recipe import Ingredient, INGREDIENT_KEY, Recipe, Classification

__all__ = [
    "MadeInstructions",
    "MadeIngredientPrep",
    "MadeIngredient",
    "KitchenOrder",
    "KitchenOrderRequest",
    "KitchenOrderResponse",
]

SCALAR = float


@dataclass
class MadeInstructions:
    """pizza level instructions seeded by the RNG """

    sauce_count: SCALAR
    cheese_count: SCALAR
    topping_count: SCALAR
    special_count: SCALAR


@dataclass
class MadeIngredientPrep:
    """rendering instructions seeded by the RNG"""

    emission_count: SCALAR
    emission_density: SCALAR
    particle_scale: SCALAR
    rotation: SCALAR


class MadeIngredient(NamedTuple):
    """struct for serializing the ingredient and its prep instructions"""

    ingredient: Ingredient
    prep: MadeIngredientPrep


@dataclass
class KitchenOrder:
    """a recipe includes all of the static information necessary
    to tell the renderer what to do"""

    unique_id: int
    name: str
    random_seed: str
    """The random seed that was used to generate the order"""
    recipe_id: int
    """The original recipe that was made"""

    base_ingredients: Dict[INGREDIENT_KEY, MadeIngredient]
    """collection of base ingredients that coule be used"""
    toppings: Dict[INGREDIENT_KEY, MadeIngredient]
    """collection of toppings ingredients that will ber used"""
    instructions: MadeInstructions


class KitchenOrderRequest(Base):
    """an inbound order request"""

    order: KitchenOrder


class KitchenOrderResponse(Base):
    """an outbound order response"""

    order: KitchenOrder


def sample(recipe: Recipe) -> KitchenOrder:
    """just a sample"""
    return KitchenOrder(
        unique_id=345,
        name=recipe.name,
        random_seed="0xAb4",
        recipe_id=recipe.unique_id,
        base_ingredients={
            "SOME_KEY": MadeIngredient(
                ingredient=Ingredient(
                    unique_id=1,
                    name="gluten-free",
                    rarity_level=1,
                    classification=Classification.crust,
                    category="crust",
                    attributes={},
                    image_uris={},
                ),
                prep=MadeIngredientPrep(
                    emission_count=26.0,
                    emission_density=0.12,
                    particle_scale=0.12,
                    rotation=1.234,
                ),
            )
        },
        toppings={
            "SOME_KEY": MadeIngredient(
                ingredient=Ingredient(
                    unique_id=1,
                    name="Pepperoni",
                    rarity_level=1,
                    classification=Classification.topping,
                    category="meat",
                    attributes={},
                    image_uris={},
                ),
                prep=MadeIngredientPrep(
                    emission_count=26.0,
                    emission_density=0.12,
                    particle_scale=0.12,
                    rotation=1.234,
                ),
            )
        },
        instructions=MadeInstructions(
            sauce_count=1,
            cheese_count=1,
            topping_count=2,
            special_count=1,
        ),
    )
