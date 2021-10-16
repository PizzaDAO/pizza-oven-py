from typing import Dict, Tuple, List
from app.models.prep import KitchenOrder
from app.core.ingredients_db import read_ingredients
from app.core.scatter import Grid, RandomScatter, Scatter, TreeRing
from app.models.recipe import Ingredient, Recipe, RecipeInstructions, ScatterType

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
from app.core.scatter import Grid, RandomScatter, TreeRing
from app.core.utils import clamp, to_hex, from_hex


def get_kitchen_order(unique_id: str):

    ingredients = read_ingredients()

    variants: list = []
    target_id = unique_id[0:3]
    for key in ingredients.keys():
        # Get the 3-digit ingredient code
        current_code = key[0:3]
        if int(current_code) > 399:
            if current_code == target_id:
                ingredient = {key: (3, RandomScatter)}
                variants.append(ingredient)

    ko = make_order(variants, ingredients)

    return ko


def make_order(variants, ingredients):

    box_id = "0000"
    box = ingredients[box_id]
    paper_id = "0500"
    paper = ingredients[paper_id]
    crust_id = "1000"
    crust = ingredients[crust_id]
    sauce_id = "2000"
    sauce = ingredients[sauce_id]
    cheese_id = "3000"
    cheese = ingredients[cheese_id]

    base_ingredients = {
        "box": box,
        "paper": paper,
        "crust": crust,
        "sauce": sauce,
        "cheese": cheese,
    }

    layer_ingredients = {}
    for item in variants:
        id = list(item.keys())
        key = id[0]
        value = ingredients[key]
        layer_ingredients.update({key: value})

    recipe_instructions = RecipeInstructions(
        crust_count=1,
        sauce_count=[1, 1],
        cheese_count=[1, 1],
        topping_count=[0, 8],
        extras_count=[0, 2],
        baking_temp_in_celsius=[395, 625],
        baking_time_in_minutes=[5, 10],
    )

    recipe = Recipe(
        unique_id=9999,
        name="custom Kitchen Order",
        random_seed="123456",
        rarity_level=0,
        base_ingredients=base_ingredients,  # Dict[INGREDIENT_KEY, ScopedIngredient],
        layers=layer_ingredients,  # Dict[INGREDIENT_KEY, ScopedIngredient],
        instructions=recipe_instructions,
    )

    kitchen_order = manual_reduce(recipe, variants)

    return kitchen_order


def manual_reduce(recipe: Recipe, ingredient_options: List) -> KitchenOrder:
    """reduce the range values of a recipe to scalar values"""
    reduced_base: Dict[INGREDIENT_KEY, MadeIngredient] = {}
    reduced_layers: Dict[INGREDIENT_KEY, MadeIngredient] = {}

    # get a random seed
    # since the recipe already received verifiable randomness
    # we use some entropy from the operating system
    random_seed = get_random(32)
    nonce = Counter(random_seed)
    deterministic_seed = get_random_deterministic_uint256(random_seed, nonce)

    for ing in recipe.base_ingredients.keys():
        prepped = select_prep(random_seed, nonce, recipe.base_ingredients[ing])
        reduced_base.update({ing: prepped})

    for ing in recipe.layers.keys():
        id = recipe.layers[ing].ingredient.unique_id

        for item in ingredient_options:
            item_id = list(item.keys())
            key = item_id[0]
            if key == id:
                vals = list(item.values())
                option_tuple = vals[0]

        prepped = make_prep(random_seed, nonce, recipe.layers[id], option_tuple)
        # prepped = select_prep(random_seed, nonce, recipe.layers[id])
        reduced_layers.update({id: prepped})

    # SHUFFLER - pull out all the instances into  buffer that we can shuffle for depth swap
    shuffled_instances = []
    for (_, ingredient) in reduced_layers.items():
        shuffled_instances += ingredient.instances

    # A list of all the instances - shuffled
    shuffled_instances = deterministic_shuffle(shuffled_instances)

    made_instructions = MadeInstructions(
        crust_count=1,
        sauce_count=1,
        cheese_count=1,
        topping_count=len(reduced_layers),
        extras_count=0,
        baking_temp_in_celsius=450,
        baking_time_in_minutes=450,
    )
    # Easy to reead filneame
    # key = list(ingredient_options[0].keys())
    # id = item_id[0]
    # name = recipe.layers[id].ingredient.name
    # easy = f"rarrepizza-{name}-{id}"

    return KitchenOrder(
        token_id="1111",  # TODO: database primary key?
        name=recipe.name,
        random_seed=to_hex(random_seed),
        recipe_id=recipe.unique_id,
        base_ingredients=reduced_base,
        layers=reduced_layers,
        instaces=shuffled_instances,
        instructions=made_instructions,
        instances=shuffled_instances,
    )


def make_prep(
    seed: int, nonce: Counter, scope: ScopedIngredient, options: Tuple
) -> MadeIngredient:
    """select the scalar values for the ingredient"""

    ingredient_list = [scope] * options[0]

    scatter_type = ScatterType.random
    if options[1] == RandomScatter:
        scatter_type = ScatterType.random
        instances = RandomScatter(seed, nonce).evaluate(ingredient_list)
    if options[1] == Grid:
        scatter_type = ScatterType.grid
        instances = Grid(seed, nonce).evaluate(ingredient_list)
    if options[1] == TreeRing:
        scatter_type = ScatterType.treering
        instances = TreeRing(seed, nonce).evaluate(ingredient_list)

    return MadeIngredient(
        ingredient=scope.ingredient,
        count=len(instances),
        instances=instances,
        scatter_type=scatter_type,
    )


def select_prep(seed: int, nonce: Counter, scope: ScopedIngredient) -> MadeIngredient:
    """select the scalar values for the ingredient"""

    scale = scope.scope.particle_scale[0]
    instances = [
        MadeIngredientPrep(
            translation=(0.0, 0.0),
            rotation=0.0,
            scale=scale,
            image_uri=scope.ingredient.image_uris["filename"],
        )
    ]

    return MadeIngredient(
        ingredient=scope.ingredient,
        count=len(instances),
        instances=instances,
        scatter_type=ScatterType.random,
    )