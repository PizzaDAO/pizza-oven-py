from typing import List  # , Dict
from itertools import chain
from random import choices

from app.models.recipe import *
from app.models.prep import *
from app.models.pizza import (
    RarePizzaMetadata,
    HotPizza,
    IngredientMetadata,
    NutritionMetadata,
    ERC721OpenSeaMetadataAttribute,
    # ERC721OpenSeaMetadataBoostAttribute,
)


def make_description(recipe, base, layers):
    """
    make the description that shows up in the token metadata
    """

    def crust(base):
        """crust description"""
        if base.ingredient.unique_id == "":
            return f"An {base.ingredient.pretty_name}"

        return f"A {base.ingredient.pretty_name}"

    def sauce(sauce):
        """sauce description"""
        if sauce.ingredient.pretty_name.lower() != "variant":
            return f" with {sauce.ingredient.pretty_name}"

        return f""

    def cheese(cheese):
        """cheese description"""
        if cheese.ingredient.unique_id == "3200":
            return f". Topped with "

        return f", covered with {base['cheese0'].ingredient.pretty_name}. Topped with "

    desc = f"A delicious {recipe} pizza."
    desc += f" {crust(base['crust0'])}{sauce(base['sauce0'])}"
    desc += cheese(base["cheese0"])

    # handle toppings
    toppings = layers.items()
    numToppings = len(toppings)
    # iterate over each of the toppings
    for i, key in enumerate(layers.keys()):
        # exclude variant's from the description
        if layers[key].ingredient.pretty_name.lower() != "variant":
            desc += layers[key].ingredient.pretty_name
            # handle the end of the sentence
            if i == numToppings - 2:
                desc += ", and "
            elif i == numToppings - 1:
                desc += "."
            else:
                desc += ", "

    # append box and paper

    def team():
        return choices(["That's Amore!", "Molto Bene!"])[0]

    def paper(paper):
        """paper description"""
        if paper == "Plain":
            return "Plain Paper"
        else:
            return f"{paper} Paper"

    # handle the box description
    if base["box0"].ingredient.unique_id == "0030":
        desc += f" Sorry, we ran out of boxes. Placed on {paper(base['paper0'].ingredient.pretty_name)}. {team()}"
    elif base["box0"].ingredient.unique_id == "0040":
        desc += f" All carefully packed in an {base['box0'].ingredient.pretty_name} Box"
        desc += f" with {paper(base['paper0'].ingredient.pretty_name)}! {team()}"
    else:
        desc += f" All carefully packed in a {base['box0'].ingredient.pretty_name} Box"
        desc += f" with {paper(base['paper0'].ingredient.pretty_name)}! {team()}"

    # done
    return desc


def to_blockchain_metadata(
    job_id: str, recipe: Recipe, order: KitchenOrder, pizza: HotPizza
) -> RarePizzaMetadata:
    """
    create metadata from the recipe, order, and pizza render to make blockchain metadata
    """
    ingredients: List[IngredientMetadata] = []
    attributes: List[ERC721OpenSeaMetadataAttribute] = []
    toppings: List[str] = []
    # boost_attributes: List[ERC721OpenSeaMetadataBoostAttribute] = []
    # category_count: List[Dict] = []

    attributes.append(
        ERC721OpenSeaMetadataAttribute(
            trait_type="Pizza Recipe",
            value=recipe.name,
        )
    )

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
        if str(value.ingredient.topping_class).lower() != "variant":
            attributes.append(
                ERC721OpenSeaMetadataAttribute(
                    trait_type=value.ingredient.topping_class,
                    value=value.ingredient.pretty_name,
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
        if str(value.ingredient.topping_class).lower() != "variant":
            attributes.append(
                ERC721OpenSeaMetadataAttribute(
                    trait_type=value.ingredient.topping_class,
                    value=value.ingredient.pretty_name,
                )
            )
        """ Add topping catgory count if not exists, otherwise increment count """
        # if value.ingredient.category not in map(
        #    lambda c: c["trait_type"], category_count
        # ):
        #    category_count.append(
        #        dict(
        #            display_type="boost_number",
        #            trait_type=value.ingredient.category,
        #            value=1,
        #        )
        #    )
        # else:
        #    for item in category_count:
        #        if item["trait_type"] == value.ingredient.category:
        #            item["value"] += 1
        # attributes.append(
        #    ERC721OpenSeaMetadataAttribute(
        #        trait_type=value.ingredient.category,
        #        value=value.ingredient.name,
        #    )
        # )
    # print(boost_attributes)
    print(order.base_ingredients.keys())
    print(order.layers.keys())

    # make the token description
    desc = make_description(recipe.name, order.base_ingredients, order.layers)

    # make the metadata object
    ipfs_hash = pizza.assets["IPFS_HASH"]
    metadata = RarePizzaMetadata(
        job_id=job_id,
        token_id=order.token_id,
        name=f"Rare Pizza #{order.token_id}",
        description=desc,
        rarity_level=recipe.rarity_level,
        random_seed=order.random_seed,
        image=f"ipfs://{ipfs_hash}",
        extension_uri=f"https://www.rarepizzas.com/pizzas/{order.token_id}/data",
        external_url=f"https://www.rarepizzas.com/pizzas/{order.token_id}",
        background_color="ffffff",
        baking_temp_in_celsius=order.instructions.baking_temp_in_celsius,
        baking_time_in_minutes=order.instructions.baking_time_in_minutes,
        ingredients=ingredients,
        attributes=attributes,
        # attributes=list(chain(attributes, boost_attributes, category_count)),
    )
    print(metadata.attributes)
    return metadata
