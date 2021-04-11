from typing import Any
from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from ....models.base import Base
from ....models.recipe import *
from ..tags import ORDER

router = APIRouter()


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


@router.get("/{recipe_id}", response_model=RecipeResponse, tags=[ORDER])
def recipe(recipe_id: int) -> Any:
    """
    Order a recipe from the kitchen (by id)
    """
    # TODO: things like database lookups, etc.

    data = sample(recipe_id)
    json = jsonable_encoder(data)
    return JSONResponse(content=json)
