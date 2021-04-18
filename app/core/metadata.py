from typing import List

from app.models.recipe import *
from app.models.prep import *
from app.models.pizza import (
    RarePizzaMetadata,
    HotPizza,
    IngredientMetadata,
    NutritionMetadata,
    ERC721OpenSeaMetadataAttribute,
)


def to_blockchain_metadata(
    job_id: str, recipe: Recipe, order: KitchenOrder, pizza: HotPizza
) -> RarePizzaMetadata:

    ingredients: List[IngredientMetadata] = []

    for (key, value) in order.base_ingredients.items():
        ingredients.append(
            IngredientMetadata(
                name=value.ingredient.name,
                rarity=value.ingredient.rarity_level,
                classification=value.ingredient.classification.name,
                category=value.ingredient.category,
                nutrition=value.ingredient.nutrition,
                attributes=[
                    ERC721OpenSeaMetadataAttribute(trait_type="todo", value="add some")
                ],
            )
        )

    for (key, value) in order.layers.items():
        ingredients.append(
            IngredientMetadata(
                name=value.ingredient.name,
                rarity=value.ingredient.rarity_level,
                classification=value.ingredient.classification.name,
                category=value.ingredient.category,
                nutrition=value.ingredient.nutrition,
                attributes=[
                    ERC721OpenSeaMetadataAttribute(trait_type="todo", value="add some")
                ],
            )
        )

    return RarePizzaMetadata(
        order_id=job_id,
        name=recipe.name,
        description="some description",
        rarity_level=recipe.rarity_level,
        random_seed=recipe.random_seed,
        image=pizza.assets["IPFS_HASH"],
        extension_uri="https://some/external/path/to/supplemantary/things",
        external_url="https://www.rarepizzas.com/pizzas/some_token_id",
        background_color="ffffff",
        baking_temp_in_celsius=order.instructions.baking_temp_in_celsius,
        baking_time_in_minutes=order.instructions.baking_time_in_minutes,
        ingredients=ingredients,
        attributes=[
            ERC721OpenSeaMetadataAttribute(trait_type="todo", value="add some")
        ],
    )
