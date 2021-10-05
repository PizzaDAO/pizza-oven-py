from enum import Enum, IntFlag
from typing import Dict, Tuple, List

from app.models.base import Base

__all__ = [
    "RecipeInstructions",
    "IngredientScope",
    "Classification",
    "NutritionMetadata",
    "Ingredient",
    "ScopedIngredient",
    "Recipe",
    "ScatterType",
    "classification_as_string",
    "classification_from_string",
]

# these types will probably change, just abstracting them for now
INGREDIENT_KEY = str
ATTRIBUTE_KEY = str
IMAGEURI_KEY = str
MIN = float
MAX = float


class Classification(Enum):
    """all of the different types"""

    box = 1
    paper = 2
    crust = 3
    sauce = 4
    cheese = 5
    topping = 6
    extras = 7


def classification_as_string(classification: Classification) -> str:
    c = "base"
    if classification == Classification.box:
        c = "box"
    if classification == Classification.paper:
        c = "paper"
    if classification == Classification.crust:
        c = "crust"
    if classification == Classification.sauce:
        c = "sauce"
    if classification == Classification.cheese:
        c = "cheese"
    if classification == Classification.topping:
        c = "topping"
    if classification == Classification.extras:
        c = "extras"
    return c


def classification_from_string(category: str) -> Classification:
    classification = Classification.box

    if "topping" in category:
        classification = Classification.topping
    if category == "paper":
        classification = Classification.paper
    if category == "crust":
        classification = Classification.crust
    if category == "sauce":
        classification = Classification.sauce
    if category == "cheese":
        classification = Classification.cheese
    return classification


class ScatterType(IntFlag):
    """all of the different types"""

    none = 0
    random = 1
    spiral = 2
    spoke = 4
    gaussian = 8
    circle = 16
    fibonacci = 32
    mandelbrot = 64
    julia = 128


class RecipeInstructions(Base):
    """pizza level instructions for seeding the RNG"""

    crust_count: int
    sauce_count: Tuple[MIN, MAX]
    cheese_count: Tuple[MIN, MAX]
    topping_count: Tuple[MIN, MAX]
    extras_count: Tuple[MIN, MAX]
    baking_temp_in_celsius: Tuple[MIN, MAX]
    baking_time_in_minutes: Tuple[MIN, MAX]


class IngredientScope(Base):
    """rendering ranges for seeding the RNG"""

    scatter_types: List[ScatterType]
    emission_count: Tuple[MIN, MAX]  # - [25.0,50.0]
    emission_density: Tuple[MIN, MAX]  # - [0.10,0.99]
    particle_scale: Tuple[MIN, MAX]  # - [0.05,0.15]
    rotation: Tuple[MIN, MAX]  # - [-3.14159,3.14159]


class NutritionMetadata(Base):
    """Metadata for ingredient nutritional information"""

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
    scope: IngredientScope


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
    layers: Dict[INGREDIENT_KEY, ScopedIngredient]
    """collection of layers ingredients that coule be used"""
    instructions: RecipeInstructions
