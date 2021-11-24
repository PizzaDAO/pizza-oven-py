from typing import Dict, Tuple, List, Optional

from pydantic.networks import ascii_domain_regex
from app.models.recipe import (
    Classification,
    Recipe,
    INGREDIENT_KEY,
    RecipeInstructions,
    ScatterType,
    ScopedIngredient,
    Classification,
    classification_as_string,
    scatter_to_string,
)
from app.models.prep import (
    KitchenOrder,
    MadeIngredient,
    MadeIngredientPrep,
    MadeInstructions,
)

from app.core.random_num import (
    Counter,
    deterministic_shuffle,
    get_random,
    get_random_deterministic_uint256,
    select_value,
)
import json
from app.core.scatter import FiveSpot, Grid, Hero, RandomScatter, SpokeCluster, TreeRing
from app.core.utils import clamp, to_hex
from app.core.ingredients_db import get_variants_for_ingredient, read_ingredients
from app.core.rarity import select_from_variants, ingredient_with_rarity
from app.core.repository import get_oven_params

from app.core.config import OvenToppingParams, Settings

__all__ = ["reduce"]

settings = Settings()


def reduce(
    recipe: Recipe, token_id: int, random_seed: Optional[int] = None
) -> KitchenOrder:
    """
    reduce the range values of a recipe to scalar values.
    expects the token id to be provided
    expects a 32 bit unsigned integer as a random number
    """
    selected_base_ingredients: Dict[INGREDIENT_KEY, MadeIngredient] = {}
    reduced_layers: Dict[INGREDIENT_KEY, MadeIngredient] = {}

    # TODO: TESTING get a random seed, if none exists
    if random_seed is None:
        print("WARNING! using random number from the operating system")
        random_seed = get_random()

    nonce = Counter(random_seed % 17)
    deterministic_seed = get_random_deterministic_uint256(random_seed, nonce)

    order_instructions = select_ingredient_count(
        deterministic_seed, nonce, recipe.instructions
    )
    print(f"creating kitchen order for recipe: {recipe.name}")
    print(f"random_seed base-10: {random_seed}")
    print(f"random_seed base-16: {to_hex(random_seed)}")
    print(f"deterministic_seed base-10: {deterministic_seed}")
    print(f"deterministic_seed base-16: {to_hex(deterministic_seed)}")
    print("instructions:")
    print(order_instructions)

    oven_params = get_oven_params()

    # BASE INGREDIENTS
    # TODO: respect the ingredient count selected in the assignment above
    # for (key, value) in recipe.base_ingredients.items():
    # reduced_base[key] = select_prep(deterministic_seed, nonce, value)
    # sort the base dict into categories that we can select from
    base_ingredients = sort_dict(recipe.base_ingredients)
    # map the ingredient categories to the MadeInstructions counts
    base_ingredient_counts = {
        "box": order_instructions.box_count,
        "paper": order_instructions.paper_count,
        "crust": order_instructions.crust_count,
        "sauce": order_instructions.sauce_count,
        "cheese": order_instructions.cheese_count,
    }
    selected_base_ingredients = select_ingredients(
        random_seed, nonce, base_ingredient_counts, base_ingredients, oven_params
    )

    # LAYER INGREDIENTS
    # TODO: respect the ingredient count selected in the assignment above
    # for (key, value) in recipe.layers.items():
    # reduced_layers[key] = select_prep(deterministic_seed, nonce, value)
    sorted_layer_dict = sort_dict(recipe.layers)
    # map the ingredient categories to the MadeInstructions counts
    layer_count_dict = {"topping": order_instructions.topping_count}
    reduced_layers = select_ingredients(
        random_seed, nonce, layer_count_dict, sorted_layer_dict, oven_params
    )

    # LASTCHANCE INGREDIENTS
    # decide whether or not there will be a lastchance
    # some recipes have only a couple, and one will get select often, making a lot of pies with the same lastchance
    # throttle the chances for a lastchance with a rarity value
    reduced_lastchances = {}
    chance_for_lastchance = select_value(random_seed, nonce, (0, 100))
    # if the random number is under the defined percentege its a go - lastchance added
    if chance_for_lastchance < oven_params.lastchance_occurance_percentage:
        sorted_lastchances_dict = sort_dict(recipe.lastchances)
        lastchance_count_dict = {"lastchance": order_instructions.lastchance_count}
        reduced_lastchances = select_ingredients(
            random_seed,
            nonce,
            lastchance_count_dict,
            sorted_lastchances_dict,
            oven_params,
        )

    # SHUFFLER - pull out all the instances into  buffer that we can shuffle for depth swap
    # shuffled_instances = []
    # for (_, ingredient) in reduced_layers.items():
    #     shuffled_instances += ingredient.instances

    # A list of all the instances - shuffled
    # shuffled_instances = deterministic_shuffle(shuffled_instances)

    return KitchenOrder(
        token_id=token_id,
        name=recipe.name,
        random_seed=to_hex(random_seed),
        recipe_id=recipe.unique_id,
        base_ingredients=selected_base_ingredients,
        layers=reduced_layers,
        lastchances=reduced_lastchances,
        instances=[],  # empty array since switched back to single ing layers
        instructions=order_instructions,
    )


def revise_kitchen_order(kitchen_order: KitchenOrder) -> KitchenOrder:
    """A funciton to revise NutritionData for a given kitchen order"""

    ingredients = read_ingredients()

    for k, v in kitchen_order.base_ingredients.items():
        print(f"base_ingredients revising: {k}")
        print(v.ingredient)
        base: ScopedIngredient = ingredients[v.ingredient.unique_id]
        v.ingredient.nutrition = base.ingredient.nutrition

    for k, v in kitchen_order.layers.items():
        print(f"layers revising: {k}")
        print(v.ingredient)
        layer: ScopedIngredient = ingredients[v.ingredient.unique_id]
        v.ingredient.nutrition = layer.ingredient.nutrition

    for k, v in kitchen_order.lastchances.items():
        print(f"lastchances revising: {k}")
        print(v.ingredient)
        lastchance: ScopedIngredient = ingredients[v.ingredient.unique_id]
        v.ingredient.nutrition = lastchance.ingredient.nutrition

    return kitchen_order


def select_ingredients(
    deterministic_seed,
    nonce,
    count_dict,
    ingredient_dict,
    oven_params: OvenToppingParams,
) -> dict:
    reduced_dict = {}
    ordered_dict = {}
    # keep track of the chosen ingredient IDs so we don't chose duplicates
    # also use this list to order layers on the pie, lower IDs below higher IDs
    chosen_ids = []
    for key in count_dict:
        if key in ingredient_dict.keys():
            # This is the number of ingredient layers for this particular layer
            made_count = int(count_dict[key])
            for i in range(0, made_count):
                # select an ingredient based on rarity
                values = list(ingredient_dict[key])
                ingredient = ingredient_with_rarity(deterministic_seed, nonce, values)
                identifier = key + str(i)
                # Only add an ingredient once - if its already in the dict, don't add it
                # This prevents a single ingredient being picked multiple times
                ingredient_id = ingredient.ingredient.unique_id
                if ingredient_id not in chosen_ids:
                    reduced_dict[identifier] = select_prep(
                        deterministic_seed, nonce, ingredient, oven_params
                    )
                    chosen_ids.append(ingredient_id)

                    print(
                        "We chose %s(%s) for the %s"
                        % (reduced_dict[identifier].ingredient.name, ingredient_id, key)
                    )
            # Re-order the layer dict, sorted by ingredient ID - lower on the bottom
            # rememeber: reduced_dict contains key/value pairs in the form of "topping0":MadeIngredient
            # so we have to pull out the ingredient IDs from value pairs to re-order the layer stack

            # sort the list of chosen IDs
            chosen_ids.sort()
            for id in chosen_ids:
                layer_tuple = get_tuple_with_id(id, reduced_dict)
                if layer_tuple:
                    key = layer_tuple[0]
                    val = layer_tuple[1]
                    ordered_dict.update({key: val})

    return ordered_dict


def get_tuple_with_id(
    unique_id: str, source_dict: Dict[str, MadeIngredient]
) -> Optional[Tuple[str, MadeIngredient]]:
    """convenience method to return a layer tuple with a specific ingredient ID"""
    for (_, ingredient) in source_dict.items():
        if unique_id == ingredient.ingredient.unique_id:
            return (_, ingredient)
    return None


def sort_dict(ingredient_dict) -> dict:
    """a method to sort through ingredients in a recipe layer(Base, Layer, Lastchances)
    and seperate the ingredients into lists by classification"""
    sorted_dict: Dict[str, List[ScopedIngredient]] = {}
    for scoped in ingredient_dict:
        scoped_ing: ScopedIngredient = ingredient_dict[scoped]
        classification = classification_as_string(scoped_ing.ingredient.classification)
        id = scoped_ing.ingredient.unique_id
        # Find toppings not variants - these end in a "0"
        if id[-1] == "0":
            if classification not in sorted_dict.keys():
                sorted_dict[classification] = []
            sorted_dict[classification].append(
                scoped_ing
            )  # key=classification : val=list of ScopedIngredients

    return sorted_dict


def select_prep(
    seed: int, nonce: Counter, scope: ScopedIngredient, oven_params: OvenToppingParams
) -> MadeIngredient:
    """select the scalar values for the ingredient"""
    # now create a list of instances made of all the variants for a given ingredient
    id = scope.ingredient.ingredient_id
    # A list of ingredients filtered as variants available for a topping - with rarity
    variant_list = get_variants_for_ingredient(id)
    # select a random number of instances from the chosen list of variants
    selected_variants = select_from_variants(seed, nonce, variant_list, scope)

    if scope.scope.scatter_types[0] == ScatterType.none:
        # This a a base layer or lastchance, so there should only be one selected variant
        scatter_type = ScatterType.none
        rotation = 0
        scale = 1.0
        translation = (0.0, 0.0)
        ingredient = scope
        if len(selected_variants) >= 1:
            ingredient = selected_variants[0]
            scale = ingredient.scope.particle_scale[0]
            rotation = round(select_value(seed, nonce, ingredient.scope.rotation))

        instances = [
            MadeIngredientPrep(
                translation=translation,
                rotation=rotation,
                scale=scale,
                image_uri=ingredient.ingredient.image_uris["filename"],
            )
        ]

    if scope.ingredient.classification == Classification.topping:

        # The number of instances we have to scatter
        num_of_instances = len(selected_variants)

        instances = []
        # Make sure we have instances to actually scatter
        if num_of_instances > 0:
            # choose a scatter typee, partially influenced by the instance count
            scatter_type = get_scatter_type(seed, nonce, num_of_instances, oven_params)

            # populate the scatter type with the selected_variants
            if scatter_type == ScatterType.random:
                instances = RandomScatter(seed, nonce, oven_params).evaluate(
                    selected_variants
                )
            if scatter_type == ScatterType.grid:
                instances = Grid(seed, nonce, oven_params).evaluate(selected_variants)
            if scatter_type == ScatterType.hero:
                instances = Hero(seed, nonce, oven_params).evaluate(selected_variants)
            if scatter_type == ScatterType.treering:
                instances = TreeRing(seed, nonce, oven_params).evaluate(
                    selected_variants
                )
            if scatter_type == ScatterType.fivespot:
                instances = FiveSpot(seed, nonce, oven_params).evaluate(
                    selected_variants
                )
            if scatter_type == ScatterType.spokecluster:
                instances = SpokeCluster(seed, nonce, oven_params).evaluate(
                    selected_variants
                )

    return MadeIngredient(
        ingredient=scope.ingredient,
        count=len(instances),
        instances=instances,
        scatter_type=scatter_type,
    )


def get_scatter_type(
    seed, nonce, num_of_instances: int, oven_params: OvenToppingParams
) -> ScatterType:
    scatter_type = ScatterType.random

    scatter_roll = select_value(seed, nonce, (0, 100))

    if num_of_instances == 1:
        scatter_type = ScatterType.hero

    elif (
        num_of_instances > 1
        and num_of_instances <= oven_params.scatter_small_count_threshold
    ):
        if scatter_roll < oven_params.small_tier_1:
            # 20% random
            scatter_type = ScatterType.random
        if (
            scatter_roll > oven_params.small_tier_1
            and scatter_roll < oven_params.small_tier_2
        ):
            # 40% Spokecluster
            scatter_type = ScatterType.spokecluster
        if scatter_roll > oven_params.small_tier_2:
            # 40% Random
            scatter_type = ScatterType.fivespot

    elif num_of_instances > oven_params.scatter_small_count_threshold:
        if scatter_roll < oven_params.large_tier_1:
            # 10% random
            scatter_type = ScatterType.random

        if (
            scatter_roll > oven_params.large_tier_1
            and scatter_roll < oven_params.large_tier_2
        ):
            # 30% Grid
            scatter_type = ScatterType.grid

        if (
            scatter_roll > oven_params.large_tier_2
            and scatter_roll < oven_params.large_tier_3
        ):
            # 30% random
            scatter_type = ScatterType.spokecluster

        if scatter_roll > oven_params.large_tier_3:
            # 30% Random
            scatter_type = ScatterType.treering

    return scatter_type


def select_ingredient_count(
    seed: int, nonce: Counter, scope: RecipeInstructions
) -> MadeInstructions:
    """select the scalar values for the kitchen order"""

    # TODO
    # rounding floats here
    # assuming the ranges will be supplied from Google Sheets in the pizza type sheet
    made = MadeInstructions(
        box_count=1,
        paper_count=1,
        crust_count=1,
        sauce_count=round(select_value(seed, nonce, scope.sauce_count), 0),
        cheese_count=round(select_value(seed, nonce, scope.cheese_count), 0),
        topping_count=round(select_value(seed, nonce, scope.topping_count), 0),
        lastchance_count=round(select_value(seed, nonce, scope.lastchance_count), 0),
        baking_temp_in_celsius=round(
            select_value(seed, nonce, scope.baking_temp_in_celsius), 0
        ),
        baking_time_in_minutes=round(
            select_value(seed, nonce, scope.baking_time_in_minutes), 0
        ),
    )

    return made
