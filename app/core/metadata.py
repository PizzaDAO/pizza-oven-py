from typing import List
from itertools import chain

from app.models.recipe import *
from app.models.prep import *
from app.models.pizza import (
    RarePizzaMetadata,
    HotPizza,
    IngredientMetadata,
    NutritionMetadata,
    ERC721OpenSeaMetadataAttribute,
    ERC721OpenSeaMetadataBoostAttribute,
)


def to_blockchain_metadata(
    job_id: str, recipe: Recipe, order: KitchenOrder, pizza: HotPizza
) -> RarePizzaMetadata:
    """create metadata from the recipe, order, and pizza render to make blockchain metadata"""
    ingredients: List[IngredientMetadata] = []
    attributes: List[ERC721OpenSeaMetadataAttribute] = []
    boost_attributes: List[ERC721OpenSeaMetadataBoostAttribute] = []

    for (_, value) in order.base_ingredients.items():
        ingredients.append(
            IngredientMetadata(
                name=value.ingredient.name,
                rarity=value.ingredient.ingredient_rarity,
                classification=value.ingredient.classification.name,
                category=value.ingredient.category,
                nutrition=value.ingredient.nutrition,
                attributes=[
                    ERC721OpenSeaMetadataAttribute(
                        trait_type=value.ingredient.classification.name,
                        value=value.ingredient.name,
                    )
                ],
            )
        )
        attributes.append(
            ERC721OpenSeaMetadataAttribute(
                trait_type=value.ingredient.category,
                value=value.ingredient.name,
            )
        )

    for (_, value) in order.layers.items():
        ingredients.append(
            IngredientMetadata(
                name=value.ingredient.name,
                rarity=value.ingredient.ingredient_rarity,
                classification=value.ingredient.classification.name,
                category=value.ingredient.category,
                nutrition=value.ingredient.nutrition,
                attributes=[
                    ERC721OpenSeaMetadataAttribute(
                        trait_type=value.ingredient.classification.name,
                        value=value.ingredient.name,
                    )
                ],
            )
        )
        attributes.append(
            ERC721OpenSeaMetadataAttribute(
                trait_type=value.ingredient.category,
                value=value.ingredient.name,
            )
        )
    boost_attributes.append(
        ERC721OpenSeaMetadataBoostAttribute(
            display_type="boost_number",
            trait_type=recipe.name,
            value=recipe.rarity_level,
        )
    )
    print(boost_attributes)
    ipfs_hash = pizza.assets["IPFS_HASH"]
    metadata = RarePizzaMetadata(
        job_id=job_id,
        token_id=order.token_id,
        name=f"Rare Pizza #{order.token_id}",
        description=f"A delicious {recipe.name[:-5]} pizza. That's amore!",
        rarity_level=recipe.rarity_level,
        random_seed=order.random_seed,
        image=f"ipfs://{ipfs_hash}",
        extension_uri=f"https://www.rarepizzas.com/pizzas/{order.token_id}/data",
        external_url=f"https://www.rarepizzas.com/pizzas/{order.token_id}",
        background_color="ffffff",
        baking_temp_in_celsius=order.instructions.baking_temp_in_celsius,
        baking_time_in_minutes=order.instructions.baking_time_in_minutes,
        ingredients=ingredients,
        attributes=list(chain(attributes, boost_attributes)),
    )
    print(metadata.attributes)
    return metadata
