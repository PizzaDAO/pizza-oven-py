from typing import Dict, Tuple, List, Optional
from app.models.recipe import (
    Recipe,
    INGREDIENT_KEY,
    RecipeInstructions,
    ScatterType,
    ScopedIngredient,
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
from app.core.scatter import Grid, RandomScatter, TreeRing
from app.core.utils import clamp, to_hex
from app.core.ingredients_db import get_variants_for_ingredient
from app.core.rarity import select_from_variants

__all__ = ["reduce"]


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
        random_seed, nonce, base_ingredient_counts, base_ingredients
    )

    # LAYER INGREDIENTS
    # TODO: respect the ingredient count selected in the assignment above
    # for (key, value) in recipe.layers.items():
    # reduced_layers[key] = select_prep(deterministic_seed, nonce, value)
    sorted_layer_dict = sort_dict(recipe.layers)
    # map the ingredient categories to the MadeInstructions counts
    layer_count_dict = {
        "topping": order_instructions.topping_count,
        "extras": order_instructions.extras_count,
    }
    reduced_layers = select_ingredients(
        random_seed, nonce, layer_count_dict, sorted_layer_dict
    )

    # SHUFFLER - pull out all the instances into  buffer that we can shuffle for depth swap
    shuffled_instances = []
    for (_, ingredient) in reduced_layers.items():
        shuffled_instances += ingredient.instances

    # A list of all the instances - shuffled
    shuffled_instances = deterministic_shuffle(shuffled_instances)

    return KitchenOrder(
        token_id=token_id,
        name=recipe.name,
        random_seed=to_hex(random_seed),
        recipe_id=recipe.unique_id,
        base_ingredients=selected_base_ingredients,
        layers=reduced_layers,
        instances=shuffled_instances,
        instructions=order_instructions,
    )


def select_ingredients(deterministic_seed, nonce, count_dict, ingredient_dict) -> dict:
    reduced_dict = {}
    for key in count_dict:
        if key in ingredient_dict.keys():
            made_count = int(
                count_dict[key]
            )  # This is the number of ingredient layers per pizza
            for i in range(0, made_count):
                # choose the ingredients
                options = ingredient_dict[key]
                opt_count = (float(len(options)), 0)
                selected_ind = int(select_value(deterministic_seed, nonce, opt_count))
                ingredient = ingredient_dict[key][selected_ind]  # MadeIngredient
                # need unique keys so we dont overwite toppings with multiple instances
                identifier = key + str(i)
                reduced_dict[identifier] = select_prep(
                    deterministic_seed, nonce, ingredient
                )

                print(
                    "We chose %s for the %s"
                    % (reduced_dict[identifier].ingredient.name, key)
                )

    return reduced_dict


def sort_dict(ingredient_dict) -> dict:
    sorted_dict: Dict[str, List[ScopedIngredient]] = {}
    for scoped in ingredient_dict:
        scoped_ing: ScopedIngredient = ingredient_dict[scoped]
        category = scoped_ing.ingredient.category
        # Topping sub-category temporary solution
        # because topping categories have their type in the name i.e. "meat" - we have to pull jus the first word
        category = category.split("-")[0]
        # Split up the base ingredients dict into lists for each category - makes selecting easier
        #
        # Parse ingredients - only using unique IDs ending in a 0
        #
        id = scoped_ing.ingredient.unique_id
        if id[-1] == "0":
            if category not in sorted_dict.keys():
                sorted_dict[category] = []
            sorted_dict[category].append(
                scoped_ing
            )  # key=category : val=list of ScopedIngredients

    return sorted_dict


def select_prep(seed: int, nonce: Counter, scope: ScopedIngredient) -> MadeIngredient:
    """select the scalar values for the ingredient"""

    # TODO: bitwise determine which scatters are valid
    # an select the one to use

    if scope.scope.scatter_types[0] == ScatterType.none:
        scatter_type = ScatterType.none
        scale = scope.scope.particle_scale[0]
        rotation = (round(select_value(seed, nonce, scope.scope.rotation), 0),)
        instances = [
            MadeIngredientPrep(
                translation=(0.0, 0.0),
                rotation=rotation,
                scale=scale,
                image_uri=scope.ingredient.image_uris["filename"],
            )
        ]

    # else:
    # instances = RandomScatter(seed, nonce).evaluate(scope)

    # Temporarily test the scattering - ScatterType not defined in database yet
    # If we have a topping here - scatter it
    #
    # Unless better solution from comment above
    if "topping" in scope.ingredient.category:
        # now create a list of instances made of all the variants for a given ingredient
        id = scope.ingredient.ingredient_id
        variant_list = get_variants_for_ingredient(id)

        if len(variant_list) > 1:
            selected_variants = select_from_variants(seed, nonce, variant_list, scope)
        else:
            selected_variants = variant_list

        # Then pick a scatter type
        scatter_type = ScatterType.random

        # populate the scatter type with the selected_variants
        if scatter_type == ScatterType.random:
            instances = RandomScatter(seed, nonce).evaluate(selected_variants)

        # instances = TreeRing(seed, nonce).evaluate(scope.scope)
        # instances = Grid(seed, nonce).evaluate(scope)
        # instances = RandomScatter(seed, nonce).evaluate(scope)

    return MadeIngredient(
        ingredient=scope.ingredient,
        count=len(instances),
        instances=instances,
        scatter_type=scatter_type,
    )


def select_ingredient_count(
    seed: int, nonce: Counter, scope: RecipeInstructions
) -> MadeInstructions:
    """select the scalar values for the kitchen order"""

    # TODO
    # rounding floats here
    # assuming the ranges will be supplied from Google Sheets in the pizza type sheet
    return MadeInstructions(
        box_count=1,
        paper_count=1,
        crust_count=1,
        sauce_count=round(select_value(seed, nonce, scope.sauce_count), 0),
        cheese_count=round(select_value(seed, nonce, scope.cheese_count), 0),
        topping_count=round(select_value(seed, nonce, scope.topping_count), 0),
        extras_count=round(select_value(seed, nonce, scope.extras_count), 0),
        baking_temp_in_celsius=round(
            select_value(seed, nonce, scope.baking_temp_in_celsius), 0
        ),
        baking_time_in_minutes=round(
            select_value(seed, nonce, scope.baking_time_in_minutes), 0
        ),
    )
