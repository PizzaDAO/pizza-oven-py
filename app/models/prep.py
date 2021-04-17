from typing import Dict, List

from .base import Base

from .recipe import Ingredient, INGREDIENT_KEY

__all__ = [
    "MadeInstructions",
    "MadeIngredientPrep",
    "MadeIngredient",
    "KitchenOrder",
]

SCALAR = float


class MadeInstructions(Base):
    """pizza level instructions seeded by the RNG """

    sauce_count: SCALAR
    cheese_count: SCALAR
    topping_count: SCALAR
    special_count: SCALAR
    baking_temp_in_celsius: SCALAR
    baking_time_in_minutes: SCALAR


class MadeIngredientPrep(Base):
    """rendering instructions seeded by the RNG"""

    emission_count: SCALAR
    emission_density: SCALAR
    particle_scale: SCALAR
    rotation: SCALAR


class MadeIngredient(Base):
    """struct for serializing the ingredient and its prep instructions"""

    ingredient: Ingredient
    prep: MadeIngredientPrep


class KitchenOrder(Base):
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
