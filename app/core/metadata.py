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

    for (_, value) in order.base_ingredients.items():
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

    for (_, value) in order.layers.items():
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
    ipfs_hash = pizza.assets["IPFS_HASH"]
    return RarePizzaMetadata(
        job_id=job_id,
        token_id=order.token_id,
        name=recipe.name,
        description="some description to be filled in later",
        rarity_level=recipe.rarity_level,
        random_seed=order.random_seed,
        image=f"ipfs://{ipfs_hash}",
        extension_uri=f"https://www.rarepizzas.com/pizzas/{ipfs_hash}/data",
        external_url=f"https://www.rarepizzas.com/pizzas/{ipfs_hash}",
        background_color="ffffff",
        baking_temp_in_celsius=order.instructions.baking_temp_in_celsius,
        baking_time_in_minutes=order.instructions.baking_time_in_minutes,
        ingredients=ingredients,
        attributes=[
            ERC721OpenSeaMetadataAttribute(trait_type="TODO", value="add some")
        ],
    )
