from typing import Dict, List, Tuple

from app.models.base import Base

from app.models.recipe import Ingredient, INGREDIENT_KEY

__all__ = [
    "MadeInstructions",
    "MadeIngredientPrep",
    "MadeIngredient",
    "KitchenOrder",
]

SCALAR = float


class MadeInstructions(Base):
    """pizza level instructions seeded by the RNG """

    crust_count: SCALAR
    sauce_count: SCALAR
    cheese_count: SCALAR
    topping_count: SCALAR
    extras_count: SCALAR
    baking_temp_in_celsius: SCALAR
    baking_time_in_minutes: SCALAR


class MadeIngredientPrep(Base):
    """rendering instructions seeded by the RNG"""

    translation: Tuple[SCALAR, SCALAR]
    """the position of the instance as cartesian coordinates"""
    rotation: SCALAR
    """the rotation of the instance as degrees"""
    scale: SCALAR
    """the scale of the instance as fraction e.g. (-1,1)"""


class MadeIngredient(Base):
    """struct for serializing the ingredient and its prep instructions"""

    ingredient: Ingredient
    count: SCALAR
    instances: List[MadeIngredientPrep]


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
    layers: Dict[INGREDIENT_KEY, MadeIngredient]
    """collection of layers ingredients that will ber used"""
    instructions: MadeInstructions
