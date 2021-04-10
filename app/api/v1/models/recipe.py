from enum import Enum
from dataclasses import dataclass
from typing import Any, Dict, List, NamedTuple, Optional, Tuple

from .base import Base

__all__ = [
    "Instructions",
    "Classification",
    "Ingredient",
    "PreppedIngredient",
    "Recipe",
    "RecipeRequest",
    "RecipeResponse",
]

# these types will probably change, just abstracting them for now
INGREDIENT_KEY = str
ATTRIBUTE_KEY = str
IMAGEURI_KEY = str
MIN = float
MAX = float


@dataclass
class Instructions:
    """pizza level instructions for seeding the RNG"""

    sauce_count: Tuple[MIN, MAX]  # - 1
    cheese_count: Tuple[MIN, MAX]  # - 2
    topping_count: Tuple[MIN, MAX]  # - 3
    special_count: Tuple[MIN, MAX]  # - 1
    # can add rules like "vegetarian", "meat lovers" etc.


@dataclass
class IngredientPrep:
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


@dataclass
class Ingredient:
    """metadata for the ingredient"""

    unique_id: int  # - 0001
    name: str  # - "Pepperoni"
    rarity_level: int  # - 1
    classification: Classification  # - topping
    category: str  # - "meat"
    # {scent: "smells funny", sodium: "high"}
    attributes: Dict[ATTRIBUTE_KEY, str]
    image_uris: Dict[IMAGEURI_KEY, str]  # {large: "path/to/it.png"}


class PreppedIngredient(NamedTuple):
    """struct for serializing the ingredient and its prep instructions"""

    ingredient: Ingredient
    prep: IngredientPrep


@dataclass
class Recipe:
    """a recipe includes all of the static information necessary
    to generate a kitchen order"""

    unique_id: int  # - 1
    name: str  # - "super rare"
    rarity_level: float  # - 4
    base_ingredients: Dict[INGREDIENT_KEY, PreppedIngredient]
    """collection of base ingredients that coule be used"""
    toppings: Dict[INGREDIENT_KEY, PreppedIngredient]
    """collection of toppings ingredients that coule be used"""
    instructions: Instructions


class RecipeRequest(Base):
    """an inbound recipe request"""

    recipe: Recipe


class RecipeResponse(Base):
    """an outbound recipe response"""

    recipe: Recipe


def sample(recipe_id: int) -> Recipe:
    """just a sample"""
    return Recipe(
        unique_id=recipe_id,
        name="super rare pizza",
        rarity_level=4,
        base_ingredients={
            "SOME_KEY": PreppedIngredient(
                ingredient=Ingredient(
                    unique_id=1,
                    name="gluten-free",
                    rarity_level=1,
                    classification=Classification.crust,
                    category="crust",
                    attributes={},
                    image_uris={},
                ),
                prep=IngredientPrep(
                    emission_count=(25.0, 50.0),
                    emission_density=(0.10, 0.15),
                    particle_scale=(0.05, 0.15),
                    rotation=(-3.14159, 3.14159),
                ),
            )
        },
        toppings={
            "SOME_KEY": PreppedIngredient(
                ingredient=Ingredient(
                    unique_id=1,
                    name="Pepperoni",
                    rarity_level=1,
                    classification=Classification.topping,
                    category="meat",
                    attributes={},
                    image_uris={},
                ),
                prep=IngredientPrep(
                    emission_count=(25.0, 50.0),
                    emission_density=(0.10, 0.15),
                    particle_scale=(0.05, 0.15),
                    rotation=(-3.14159, 3.14159),
                ),
            )
        },
        instructions=Instructions(
            sauce_count=(1, 1),
            cheese_count=(1, 2),
            topping_count=(2, 10),
            special_count=(1, 3),
        ),
    )
