from typing import Dict, Tuple
from app.models.recipe import (
    Recipe,
    INGREDIENT_KEY,
    RecipeInstructions,
    ScopedIngredient,
)
from app.models.prep import (
    KitchenOrder,
    MadeIngredient,
    MadeIngredientPrep,
    MadeInstructions,
)

from app.core.random import (
    get_random,
    get_random_deterministic,
    clamp,
    to_hex,
    from_hex,
)

__all__ = ["reduce"]


def reduce(recipe: Recipe) -> KitchenOrder:
    """reduce the range values of a recipe to scalar values"""
    reduced_base: Dict[INGREDIENT_KEY, MadeIngredient] = {}
    reduced_toppings: Dict[INGREDIENT_KEY, MadeIngredient] = {}

    # get a random seed
    # since the recipe already received verifiable randomness
    # we use some entropy from the operating system
    random_seed = get_random(32)
    counter = random_seed
    deterministic_seed = get_random_deterministic(from_hex(recipe.random_seed), counter)

    # TODO: select ingredient count first and then only add the ingredients that are selected

    for (key, value) in recipe.base_ingredients.items():
        reduced_base[key] = select_prep(deterministic_seed, counter, value)

    for (key, value) in recipe.toppings.items():
        reduced_toppings[key] = select_prep(deterministic_seed, counter, value)

    return KitchenOrder(
        unique_id=0,  # TODO: database primary key?
        name=recipe.name,
        random_seed=to_hex(random_seed),
        recipe_id=recipe.unique_id,
        base_ingredients=reduced_base,
        toppings=reduced_toppings,
        instructions=select_ingredient_count(
            deterministic_seed, counter, recipe.instructions
        ),
    )


def select_prep(seed: int, counter: int, scope: ScopedIngredient) -> MadeIngredient:
    """select the scalar values for the ingredient"""
    return MadeIngredient(
        ingredient=scope.ingredient,
        prep=MadeIngredientPrep(
            emission_count=select_value(seed, counter, scope.scope.emission_count),
            emission_density=select_value(seed, counter, scope.scope.emission_density),
            particle_scale=select_value(seed, counter, scope.scope.particle_scale),
            rotation=select_value(seed, counter, scope.scope.rotation),
        ),
    )


def select_ingredient_count(
    seed: int, counter: int, scope: RecipeInstructions
) -> MadeInstructions:
    """select the scalar values for the kitchen order"""
    return MadeInstructions(
        sauce_count=select_value(seed, counter, scope.sauce_count),
        cheese_count=select_value(seed, counter, scope.cheese_count),
        topping_count=select_value(seed, counter, scope.topping_count),
        special_count=select_value(seed, counter, scope.special_count),
        baking_temp_in_celsius=select_value(
            seed, counter, scope.baking_temp_in_celsius
        ),
        baking_time_in_minutes=select_value(
            seed, counter, scope.baking_time_in_minutes
        ),
    )


def select_value(seed: int, counter: int, bounds: Tuple[float, float]) -> float:
    counter += 1
    return clamp(get_random_deterministic(seed, counter), bounds[0], bounds[1])
