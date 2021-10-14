from typing import Dict, List, Tuple, Optional

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

    box_count: SCALAR = 1
    paper_count: SCALAR = 1
    crust_count: SCALAR = 1
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
    image_uri: Optional[str]
    """path to ingredient image"""


class ShuffledLayer(Base):
    """struct for layers of depth swapped ingredient instances"""

    token_id: int
    index: SCALAR
    count: SCALAR
    instances: List[MadeIngredientPrep]
    output_mask: Optional[str]


class MadeIngredient(Base):
    """struct for serializing the ingredient and its prep instructions"""

    ingredient: Ingredient
    count: SCALAR
    instances: List[MadeIngredientPrep]


class KitchenOrder(Base):
    """a recipe includes all of the static information necessary
    to tell the renderer what to do"""

    token_id: int
    """the token id for which this order is made"""
    name: str
    random_seed: str
    """The random seed that was used to generate the order"""
    recipe_id: int
    """The original recipe that was made"""

    base_ingredients: Dict[INGREDIENT_KEY, MadeIngredient]
    """collection of base ingredients that coule be used"""
    layers: Dict[INGREDIENT_KEY, MadeIngredient]
    """collection of layers ingredients that will be used"""
    specials: Optional[Dict[INGREDIENT_KEY, MadeIngredient]]
    """collection of special ingredients that will be used"""
    instances: List[MadeIngredientPrep]
    """shuffled list of all instances - provides depth in arrangements"""
    instructions: MadeInstructions
