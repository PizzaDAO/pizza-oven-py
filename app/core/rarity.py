from typing import Dict, Tuple, List, Optional
from app.models.recipe import (
    Rarity,
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


__all__ = ["select_from_variants"]

# Probabilistic distribution weights
def weight_for_rarity(rarity: Rarity) -> int:
    if rarity == Rarity.common:
        return 550
    if rarity == Rarity.uncommon:
        return 340
    if rarity == Rarity.rare:
        return 100
    if rarity == Rarity.grail:
        return 10

    return 0


def select_from_variants(
    random_seed: int,
    nonce: Counter,
    variants: List[ScopedIngredient],
    scope: ScopedIngredient,
) -> List[ScopedIngredient]:
    """given a list of variants, deterministically select a series based on weights"""

    variants = sort_by_rarity(variants, "variant")

    freq = makeDistribution(variants)

    # select the variants based on scope count
    instance_count = round(select_value(random_seed, nonce, scope.scope.emission_count))

    instances = []
    for i in range(instance_count):
        index = random_weighted_index(random_seed, nonce, i, freq)

        instances.append(variants[index])

    return instances


def ingredient_with_rarity(
    random_seed: int, nonce: Counter, ingredients: List[ScopedIngredient]
) -> ScopedIngredient:

    sorted = sort_by_rarity(ingredients, "topping")

    freq = makeDistribution(sorted)

    index = random_weighted_index(random_seed, nonce, 1, freq)

    return sorted[index]


def makeDistribution(options: List[ScopedIngredient]):
    """Create a list of relative weight values"""
    freq = []
    weight_sum = 0
    missing_rarity = False
    for item in options:
        weight = weight_for_rarity(item.ingredient.variant_rarity)
        if weight == 0:
            weight = weight_for_rarity(
                Rarity.common
            )  # can't be zero - default to common
            missing_rarity = True
        weight_sum += weight

    if missing_rarity:
        print(
            f"Possibly missing rarity assignments for {options[0].ingredient.unique_id}"
        )

    for item in options:
        weight = weight_for_rarity(item.ingredient.variant_rarity)
        if weight == 0:
            weight = weight_for_rarity(Rarity.common)
        weight_percent = 100 * (weight / weight_sum)
        freq.append(weight_percent)

    return freq


def sort_by_rarity(option_list: List[ScopedIngredient], sort_type: str):
    """Sort a list by rarity - ascending in rarity - last is most rare"""
    # getting length of list of tuples
    length = len(option_list)
    for i in range(0, length):
        for j in range(0, length - i - 1):
            if sort_type == "variant":
                rarity1 = weight_for_rarity(option_list[j].ingredient.variant_rarity)
                rarity2 = weight_for_rarity(
                    option_list[j + 1].ingredient.variant_rarity
                )
            else:
                rarity1 = weight_for_rarity(option_list[j].ingredient.ingredient_rarity)
                rarity2 = weight_for_rarity(
                    option_list[j + 1].ingredient.ingredient_rarity
                )
            if rarity2 > rarity1:
                temp = option_list[j]
                option_list[j] = option_list[j + 1]
                option_list[j + 1] = temp

    return option_list


def random_weighted_index(
    random_seed: int, nonce: Counter, personalization: int, freq: List
) -> int:
    """given the frequency distribution list, pick an index in this list"""
    max_count = len(freq)

    # Create and fill prefix array
    prefix = [0] * max_count
    prefix[0] = freq[0]
    for i in range(max_count):
        prefix[i] = prefix[i - 1] + freq[i]

    # Raondomly choose an index given the length of the variant list
    max = prefix[max_count - 1]
    rand = get_random_deterministic_uint256(random_seed, nonce, str(personalization))
    rand_val = rand % max

    # Map the randomly chosen index to a probability distribution detailed by prefix list created above
    rarified_index = map_to_probability(prefix, rand_val, max_count - 1)

    return rarified_index


# Utility function to find ceiling of r in arr[l..h]
def map_to_probability(probability_list, rand_val, max_index):
    """Map the chosen index to a list of probabilites based on weights"""

    index = 0

    while index < max_index:
        middle = index + ((max_index - index) >> 1)

        if rand_val > probability_list[middle]:
            index = middle + 1
        else:
            max_index = middle

    if probability_list[index] >= rand_val:
        return index
    else:
        return -1
