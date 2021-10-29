from typing import List, Dict
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
    category_count: List[Dict] = []

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
        """ Add topping catgory count if not exists, otherwise increment count """
        if value.ingredient.category not in map(
            lambda c: c["trait_type"], category_count
        ):
            category_count.append(
                dict(
                    display_type="boost_number",
                    trait_type=value.ingredient.category,
                    value=1,
                )
            )
        else:
            for item in category_count:
                if item["trait_type"] == value.ingredient.category:
                    item["value"] += 1
        attributes.append(
            ERC721OpenSeaMetadataAttribute(
                trait_type=value.ingredient.category,
                value=value.ingredient.name,
            )
        )
    print(boost_attributes)
    ipfs_hash = pizza.assets["IPFS_HASH"]
    metadata = RarePizzaMetadata(
        job_id=job_id,
        token_id=order.token_id,
        name=f"Rare Pizza #{order.token_id}",
        description=f"A delicious {recipe.name} pizza. That's amore!",
        rarity_level=recipe.rarity_level,
        random_seed=order.random_seed,
        image=f"ipfs://{ipfs_hash}",
        extension_uri=f"https://www.rarepizzas.com/pizzas/{order.token_id}/data",
        external_url=f"https://www.rarepizzas.com/pizzas/{order.token_id}",
        background_color="ffffff",
        baking_temp_in_celsius=order.instructions.baking_temp_in_celsius,
        baking_time_in_minutes=order.instructions.baking_time_in_minutes,
        ingredients=ingredients,
        attributes=list(chain(attributes, boost_attributes, category_count)),
    )
    print(metadata.attributes)
    return metadata
