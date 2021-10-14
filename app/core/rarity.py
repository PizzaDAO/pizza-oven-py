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

    variants = sort_by_rarity(variants)

    freq = makeDistribution(variants)

    # select the variants based on scope count
    instance_count = round(select_value(random_seed, nonce, scope.scope.emission_count))

    instances = []
    for i in range(instance_count):
        index = random_weighted_index(random_seed, nonce, i, freq)

        instances.append(variants[index])

    return instances


def makeDistribution(options: List[ScopedIngredient]):
    """Create a list of relative weight values"""
    freq = []
    weight_sum = 0
    for item in options:
        weight_sum += weight_for_rarity(item.ingredient.variant_rarity)

    if weight_sum == 0:
        print(
            "Possible missing rarity assignments for this variant group - check google sheet"
        )
        return [1] * len(options)

    for item in options:
        weight_percent = 100 * (
            weight_for_rarity(item.ingredient.variant_rarity) / weight_sum
        )
        freq.append(weight_percent)

    return freq


def sort_by_rarity(variant_list: List[ScopedIngredient]):
    """Sort a list by rarity - ascending in rarity - last is most rare"""
    # getting length of list of tuples
    length = len(variant_list)
    for i in range(0, length):

        for j in range(0, length - i - 1):
            rarity1 = weight_for_rarity(variant_list[j].ingredient.variant_rarity)
            rarity2 = weight_for_rarity(variant_list[j + 1].ingredient.variant_rarity)
            if rarity2 > rarity1:
                temp = variant_list[j]
                variant_list[j] = variant_list[j + 1]
                variant_list[j + 1] = temp

    return variant_list


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

    max = prefix[max_count - 1]

    rand = get_random_deterministic_uint256(random_seed, nonce, str(personalization))
    r = rand % max

    # Find index of ceiling of r in prefix array
    indexc = findCeil(prefix, r, 0, max_count - 1)

    return indexc


# Utility function to find ceiling of r in arr[l..h]
def findCeil(arr, r, l, h):

    while l < h:
        mid = l + ((h - l) >> 1)
        # Same as mid = (l+h)/2
        if r > arr[mid]:
            l = mid + 1
        else:
            h = mid

    if arr[l] >= r:
        return l
    else:
        return -1
