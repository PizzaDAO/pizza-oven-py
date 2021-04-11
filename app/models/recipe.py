from enum import Enum
from typing import Any, Dict, List, Tuple

from .base import Base

__all__ = [
    "RecipeInstructions",
    "IncredientScope",
    "Classification",
    "Ingredient",
    "ScopedIngredient",
    "Recipe",
]

# these types will probably change, just abstracting them for now
INGREDIENT_KEY = str
ATTRIBUTE_KEY = str
IMAGEURI_KEY = str
MIN = float
MAX = float


class RecipeInstructions(Base):
    """pizza level instructions for seeding the RNG"""

    sauce_count: Tuple[MIN, MAX]  # - 1
    cheese_count: Tuple[MIN, MAX]  # - 2
    topping_count: Tuple[MIN, MAX]  # - 3
    special_count: Tuple[MIN, MAX]  # - 1
    # can add rules like "vegetarian", "meat lovers" etc.


class IncredientScope(Base):
    """rendering ranges for seeding the RNG"""

    emission_count: Tuple[MIN, MAX]  # - [25.0,50.0]
    emission_density: Tuple[MIN, MAX]  # - [0.10,0.99]
    particle_scale: Tuple[MIN, MAX]  # - [0.05,0.15]
    rotation: Tuple[MIN, MAX]  # - [-3.14159,3.14159]


class Classification(Enum):
    """all of the different types"""

    box = 1
    paper = 2
    crust = 3
    sauce = 4
    cheese = 5
    topping = 6
    special = 7


class Ingredient(Base):
    """metadata for the ingredient"""

    unique_id: str  # - 0001
    index: int  # 1
    name: str  # - "Pepperoni"
    rarity_level: int  # - 1
    classification: Classification  # - topping
    category: str  # - "meat"
    # {scent: "smells funny", sodium: "high"}
    attributes: Dict[ATTRIBUTE_KEY, str]
    nutrition: Dict[ATTRIBUTE_KEY, float]
    image_uris: Dict[IMAGEURI_KEY, str]  # {large: "path/to/it.png"}


class ScopedIngredient(Base):
    """struct for serializing the ingredient and its prep instructions"""

    ingredient: Ingredient
    scope: IncredientScope


class Recipe(Base):
    """a recipe includes all of the static information necessary
    to generate a kitchen order"""

    unique_id: int  # - 1
    name: str  # - "super rare"
    rarity_level: float  # - 4
    base_ingredients: Dict[INGREDIENT_KEY, ScopedIngredient]
    """collection of base ingredients that coule be used"""
    toppings: Dict[INGREDIENT_KEY, ScopedIngredient]
    """collection of toppings ingredients that coule be used"""
    instructions: RecipeInstructions
