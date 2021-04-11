from typing import Any
from fastapi import APIRouter, Body
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from ..dining_room.recipe import RecipeRequest
from ....models.base import Base
from ....models.prep import *
from ....models.recipe import *
from ....core.prep_line import reduce

from ..tags import PREP

router = APIRouter()


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
            "Box": MadeIngredient(
                ingredient=Ingredient(
                    unique_id="0000",
                    index=1,
                    name="gluten-free",
                    rarity_level=1,
                    classification=Classification.box,
                    category=Classification.box.name,
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


@router.post("/preparePizza", response_model=KitchenOrderResponse, tags=[PREP])
def prepare_pizza(request: RecipeRequest = Body(...)) -> Any:
    """
    prepares a recipe for baking by reducing instruction ranges to scalars
    """

    data = reduce(request.recipe)
    json = jsonable_encoder(data)
    return JSONResponse(content=json)
