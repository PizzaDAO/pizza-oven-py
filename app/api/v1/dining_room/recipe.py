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
        name="My Cool First Super Rare Pizza Test",
        rarity_level=4,
        base_ingredients={
            "box": ScopedIngredient(
                ingredient=Ingredient(
                    unique_id="0000",
                    index=0,
                    name="Cardboard Pizza Box",
                    rarity_level=1,
                    classification=Classification.box,
                    category="cardboard",
                    attributes={"state": "open", "material": "cardboard"},
                    nutrition={
                        "servings": 1,
                        "calories": 150,
                    },
                    image_uris={
                        "filename": "0000-box-cardboard.png",
                        "output_mask": "rarepizza-#####-box.png",
                    },
                ),
                scope=IncredientScope(
                    emission_count=(1.0, 1.0),
                    emission_density=(1.0, 1.0),
                    particle_scale=(0.975, 0.975),
                    rotation=(0.00, 0.00),
                ),
            ),
            "paper": ScopedIngredient(
                ingredient=Ingredient(
                    unique_id="0500",
                    index=1,
                    name="Classic Red checker Wax Paper",
                    rarity_level=1,
                    classification=Classification.paper,
                    category="red-checker",
                    attributes={"state": "greasy", "material": "wax"},
                    nutrition={
                        "servings": 1,
                        "calories": 150,
                    },
                    image_uris={
                        "filename": "0500-waxpaper-redchecker.png",
                        "output_mask": "rarepizza-#####-paper.png",
                    },
                ),
                scope=IncredientScope(
                    emission_count=(1.0, 1.0),
                    emission_density=(1.0, 1.0),
                    particle_scale=(0.975, 0.975),
                    rotation=(0.00, 0.00),
                ),
            ),
            "crust": ScopedIngredient(
                ingredient=Ingredient(
                    unique_id="1000",
                    index=2,
                    name="New York Style Thin Crust",
                    rarity_level=1,
                    classification=Classification.crust,
                    category="thin",
                    attributes={"state": "overcooked", "material": "traditional"},
                    nutrition={
                        "servings": 8,
                        "calories": 250,
                        "cholesterol": 0,
                        "fat": 4.5,
                        "sodium": 170,
                        "carbs": 27,
                        "protien": 5,
                        "vitamins": 0,
                    },
                    image_uris={
                        "filename": "1000-crust-thin.png",
                        "output_mask": "rarepizza-#####-crust.png",
                    },
                ),
                scope=IncredientScope(
                    emission_count=(1.0, 1.0),
                    emission_density=(1.0, 1.0),
                    particle_scale=(1.0, 1.0),
                    rotation=(0.00, 0.00),
                ),
            ),
        },
        toppings={
            "sauce": ScopedIngredient(
                ingredient=Ingredient(
                    unique_id="2000",
                    index=0,
                    name="Traditional Tomato Sauce",
                    rarity_level=1,
                    classification=Classification.sauce,
                    category="traditional",
                    attributes={"state": "thick", "material": "tomato"},
                    nutrition={
                        "servings": 8,
                        "calories": 250,
                        "cholesterol": 0,
                        "fat": 4.5,
                        "sodium": 170,
                        "carbs": 27,
                        "protien": 5,
                        "vitamins": 0,
                    },
                    image_uris={
                        "filename": "2000-sauce-tomato.png",
                        "output_mask": "rarepizza-#####-topping-%s.png",
                    },
                ),
                scope=IncredientScope(
                    emission_count=(1.0, 1.0),
                    emission_density=(1.0, 1.0),
                    particle_scale=(1.0, 1.0),
                    rotation=(0.00, 0.00),
                ),
            ),
            "cheese": ScopedIngredient(
                ingredient=Ingredient(
                    unique_id="3000",
                    index=1,
                    name="Traditional Mozzarella",
                    rarity_level=1,
                    classification=Classification.cheese,
                    category="traditional",
                    attributes={"state": "aged", "vintage": "2007"},
                    nutrition={
                        "servings": 8,
                        "calories": 250,
                        "cholesterol": 0,
                        "fat": 4.5,
                        "sodium": 170,
                        "carbs": 27,
                        "protien": 5,
                        "vitamins": 0,
                    },
                    image_uris={
                        "filename": "3000-cheese-mozzarella.png",
                        "output_mask": "rarepizza-#####-topping-%s.png",
                    },
                ),
                scope=IncredientScope(
                    emission_count=(1.0, 1.0),
                    emission_density=(1.0, 1.0),
                    particle_scale=(1.0, 1.0),
                    rotation=(0.00, 0.00),
                ),
            ),
            "topping-1": ScopedIngredient(
                ingredient=Ingredient(
                    unique_id="4000",
                    index=2,
                    name="Pepperoni",
                    rarity_level=1,
                    classification=Classification.topping,
                    category="meat",
                    attributes={"state": "cured", "method": "corned"},
                    nutrition={
                        "servings": 8,
                        "calories": 250,
                        "cholesterol": 0,
                        "fat": 4.5,
                        "sodium": 170,
                        "carbs": 27,
                        "protien": 5,
                        "vitamins": 0,
                    },
                    image_uris={
                        "filename": "4000-topping-meat-pepperoni.png",
                        "output_mask": "rarepizza-#####-topping-%s.png",
                    },
                ),
                scope=IncredientScope(
                    emission_count=(1.0, 20.0),
                    emission_density=(0.1, 0.8),
                    particle_scale=(0.1, 0.22),
                    rotation=(-180.0, 180.0),
                ),
            ),
            "topping-2": ScopedIngredient(
                ingredient=Ingredient(
                    unique_id="5000",
                    index=3,
                    name="Tomato",
                    rarity_level=1,
                    classification=Classification.topping,
                    category="fruit",
                    attributes={"state": "fresh"},
                    nutrition={
                        "servings": 8,
                        "calories": 250,
                        "cholesterol": 0,
                        "fat": 4.5,
                        "sodium": 170,
                        "carbs": 27,
                        "protien": 5,
                        "vitamins": 0,
                    },
                    image_uris={
                        "filename": "5000-topping-fruit-tomato.png",
                        "output_mask": "rarepizza-#####-topping-%s.png",
                    },
                ),
                scope=IncredientScope(
                    emission_count=(1.0, 20.0),
                    emission_density=(0.1, 0.8),
                    particle_scale=(0.1, 0.22),
                    rotation=(-180.0, 180.0),
                ),
            ),
        },
        instructions=RecipeInstructions(
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
    # TODO: things like database lookups, etc. to get the recipe

    data = sample(recipe_id)
    json = jsonable_encoder(data)
    return JSONResponse(content=json)
