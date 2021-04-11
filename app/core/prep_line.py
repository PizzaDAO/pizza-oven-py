from typing import Dict, Tuple
from ..models.recipe import Recipe, INGREDIENT_KEY, RecipeInstructions, ScopedIngredient
from ..models.prep import (
    KitchenOrder,
    MadeIngredient,
    MadeIngredientPrep,
    MadeInstructions,
)

from .random import get_random, get_random_deterministic


def reduce(recipe: Recipe) -> KitchenOrder:
    """reduce the range values of a recipe to scalar values"""
    reduced_base: Dict[INGREDIENT_KEY, MadeIngredient] = {}
    reduced_toppings: Dict[INGREDIENT_KEY, MadeIngredient] = {}

    # get a random seed
    seed = get_random()
    counter = 0

    for (key, value) in recipe.base_ingredients.items():
        reduced_base[key] = select_prep(seed, counter, value)

    for (key, value) in recipe.toppings.items():
        reduced_toppings[key] = select_prep(seed, counter, value)

    return KitchenOrder(
        unique_id=get_random(32),
        name=recipe.name,
        random_seed=seed,
        recipe_id=recipe.unique_id,
        base_ingredients=reduced_base,
        toppings=reduced_toppings,
        instructions=select_ingredient_count(seed, counter, recipe.instructions),
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
    )


def select_value(seed: int, counter: int, bounds: Tuple[float, float]) -> float:
    counter += 1
    return clamp(get_random_deterministic(seed, counter), bounds[0], bounds[1])


def clamp(entropy: int, start: float, end: float) -> float:
    """naive implementation of a range bound"""
    print("numbers:::")
    print(entropy)
    print(start)
    print(end)
    if end == 0.0:
        return 0.0
    modulo = float(entropy) % end
    if modulo < start:
        return start
    return modulo


def to_hex(base_10: int) -> str:
    in_hex = format(base_10, "02X")
    if len(in_hex) % 2:
        in_hex = "0" + in_hex
    return in_hex
