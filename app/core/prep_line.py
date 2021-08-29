from typing import Dict, Tuple
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

from app.core.random import (
    Counter,
    get_random,
    get_random_deterministic_uint256,
    select_value,
)
from app.core.scatter import RandomScatter
from app.core.utils import clamp, to_hex, from_hex

__all__ = ["reduce"]


def reduce(recipe: Recipe) -> KitchenOrder:
    """reduce the range values of a recipe to scalar values"""
    reduced_base: Dict[INGREDIENT_KEY, MadeIngredient] = {}
    reduced_layers: Dict[INGREDIENT_KEY, MadeIngredient] = {}

    # get a random seed
    # since the recipe already received verifiable randomness
    # we use some entropy from the operating system
    random_seed = get_random(32)
    nonce = Counter(random_seed)
    deterministic_seed = get_random_deterministic_uint256(
        from_hex(recipe.random_seed), nonce
    )

    ingredient_count = select_ingredient_count(
        deterministic_seed, nonce, recipe.instructions
    )

    # TODO: respect the ingredient count selected in the assignment above
    for (key, value) in recipe.base_ingredients.items():
        reduced_base[key] = select_prep(deterministic_seed, nonce, value)

    # TODO: respect the ingredient count selected in the assignment above
    for (key, value) in recipe.layers.items():
        reduced_layers[key] = select_prep(deterministic_seed, nonce, value)

    return KitchenOrder(
        unique_id=0,  # TODO: database primary key?
        name=recipe.name,
        random_seed=to_hex(random_seed),
        recipe_id=recipe.unique_id,
        base_ingredients=reduced_base,
        layers=reduced_layers,
        instructions=ingredient_count,
    )


def select_prep(seed: int, nonce: Counter, scope: ScopedIngredient) -> MadeIngredient:
    """select the scalar values for the ingredient"""

    # TODO: bitwise determine which scatters are valid
    # an select the one to use

    if scope.scope.scatter_types[0] == ScatterType.none:
        instances = [MadeIngredientPrep(translation=(0.0, 0.0), rotation=0.0, scale=1)]
    else:
        instances = RandomScatter(seed, nonce).evaluate(scope.scope)

    return MadeIngredient(
        ingredient=scope.ingredient,
        count=len(instances),
        instances=instances,
    )


def select_ingredient_count(
    seed: int, nonce: Counter, scope: RecipeInstructions
) -> MadeInstructions:
    """select the scalar values for the kitchen order"""

    # TODO
    return MadeInstructions(
        sauce_count=select_value(seed, nonce, scope.sauce_count),
        cheese_count=select_value(seed, nonce, scope.cheese_count),
        topping_count=select_value(seed, nonce, scope.topping_count),
        extras_count=select_value(seed, nonce, scope.extras_count),
        baking_temp_in_celsius=select_value(seed, nonce, scope.baking_temp_in_celsius),
        baking_time_in_minutes=select_value(seed, nonce, scope.baking_time_in_minutes),
    )
