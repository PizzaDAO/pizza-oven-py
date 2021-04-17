from enum import Enum
from typing import Dict, Tuple

from app.models.base import Base

__all__ = [
    "RecipeInstructions",
    "IncredientScope",
    "Classification",
    "NutritionMetadata",
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

    sauce_count: Tuple[MIN, MAX]
    cheese_count: Tuple[MIN, MAX]
    topping_count: Tuple[MIN, MAX]
    special_count: Tuple[MIN, MAX]
    baking_temp_in_celsius: Tuple[MIN, MAX]
    baking_time_in_minutes: Tuple[MIN, MAX]


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


class NutritionMetadata(Base):
    servings: float
    calories: float
    fat: float
    cholesterol: float
    sodium: float
    potassium: float
    carbohydrates: float
    protein: float


class Ingredient(Base):
    """metadata for the ingredient"""

    # TODO: add artist attribution fields

    unique_id: str  # - 0001
    index: int  # 1
    name: str  # - "Pepperoni"
    rarity_level: int  # - 1
    classification: Classification  # - topping
    category: str
    """
    categories can be used to group elements together 
    so that only one of each category will show up on a pizza
    for isntance, multiple things may be in the pepperoni category
    but only one pepperoni will show up on a pizza
    """
    # things like: {scent: "smells funny", sodium: "high"}
    attributes: Dict[ATTRIBUTE_KEY, str]
    """attributes that should show up in the token metadata"""
    nutrition: NutritionMetadata
    image_uris: Dict[IMAGEURI_KEY, str]
    """collection of paths to image uri's"""


class ScopedIngredient(Base):
    """struct for serializing the ingredient and its prep instructions"""

    ingredient: Ingredient
    scope: IncredientScope


class Recipe(Base):
    """a recipe includes all of the static information necessary
    to generate a kitchen order"""

    unique_id: int  # - 1
    name: str
    """
    Name of the pizza.  This can be randomly generated & will show up in metadata
    """
    random_seed: str
    """The random seed that was used to generate the order"""
    rarity_level: float  # - 4
    base_ingredients: Dict[INGREDIENT_KEY, ScopedIngredient]
    """collection of base ingredients that coule be used as part of a kitchen order"""
    toppings: Dict[INGREDIENT_KEY, ScopedIngredient]
    """collection of toppings ingredients that coule be used"""
    instructions: RecipeInstructions
