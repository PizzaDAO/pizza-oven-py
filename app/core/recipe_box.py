import hashlib
from os import listdir
from os.path import isfile, join
import json
from typing import Dict, Optional

from app.models.recipe import *

from app.core.random_num import get_random, pop_random, set_hash

lOCAL_RECIPES_PATH = "data/recipes/"
recipes_dict = {}
recipe_names = []


def make_recipe() -> Recipe:

    # TODO: deterministically derive the ingredients for the recipe
    # based ona random seed
    return sample(1)


def make_deter_recipe(seed: str, pizza_type: str = None) -> Recipe:
    """Make a deterministic recipe from seed provided
    given this seed, the pie should be the same every time"""

    if len(recipe_names) == 0:
        load_recipes()

    # get the hash array set up for random numbers
    set_hash(seed)

    new_recipe = determine_attributes(pizza_type)

    return new_recipe


def load_recipes():
    """Load all the json recipes generated from the spreadsheets from /data folder"""

    print("loading recipe files")
    # check contents of data/recipes folder
    file_list = []
    try:
        file_list = [
            f
            for f in listdir(lOCAL_RECIPES_PATH)
            if isfile(join(lOCAL_RECIPES_PATH, f))
        ]
    except Exception:
        print("Can't get list of recipe files")
    finally:
        for file in file_list:
            try:
                f = open(lOCAL_RECIPES_PATH + file)
                contents = json.load(f)
                name = _remove_exts(file)
                recipes_dict.update({name: contents})
                f.close()

                recipe_names.append(name)
            except:
                print("Ignoring this file: " + file)


def determine_attributes(pizza_type: str = None) -> Recipe:
    """Go through the base and layer dicts in the selected recipe
    and make a random/deterministic selection for each ingredient category"""

    # TODO add probabilistic distribution curves to adjust rarity across ingredient selection

    pizza_index = 0
    # First get the JSON recipe for a pizza
    if pizza_type is None:
        # choose a random recipe
        rand = pop_random()
        pizza_index = rand % len(recipe_names)
        # Rarity alert - all options have equal probability

    else:
        # make a recipe for the requested pizza type
        try:
            pizza_index = recipe_names.index(pizza_type)
        except:
            # TEMPORARILY make a random pue if the pizza type is not valid
            # need a better way to track pizza types by id
            print(pizza_type + " is not a valid pizza type - Random Pies will be made")

    pizza_to_make = recipe_names[pizza_index]

    print("Pizza type: " + pizza_to_make)

    # convert the json to a Recipes object
    json = recipes_dict[pizza_to_make]

    recipe = Recipe.parse_obj(json)

    # BASE INGREDIENTS
    base_ingredients = select_base_ingredients(recipe.base_ingredients)

    recipe.base_ingredients = base_ingredients

    # TOPPINGS AND LAYERS
    # Determine how many layers and toppings the pizza will have
    # This is a temporary solution
    max = 3
    topping_count = (pop_random() % max) + 1  # at least one topping

    layer_ingredients = select_layer_ingredients(recipe.layers, topping_count)

    recipe.layers = layer_ingredients

    return recipe


def select_base_ingredients(source_dict: dict) -> dict:
    """Sort a dict by categories so we can make a random selection from the list"""
    sorted_dict = {}
    for scoped in source_dict:
        scoped_ing: ScopedIngredient = source_dict[scoped]
        category = scoped_ing.ingredient.category
        # Split up the base ingredients dict into lists for each category - makes selecting easier
        if category not in sorted_dict.keys():
            sorted_dict[category] = list()

        sorted_dict[category].append(
            scoped_ing
        )  # key=category : val=list of ScopedIngredients

    # now pick a random selection from each category
    selection_dict = {}
    for item in sorted_dict:
        max = len(sorted_dict[item])
        random = pop_random()
        index = random % max  # Rarity Alert - all options have equal probability
        scoped_chosen: ScopedIngredient = sorted_dict[item][index]

        selection_dict.update({scoped_chosen.ingredient.unique_id: scoped_chosen})

        print(
            "For the "
            + item
            + " we chose "
            + scoped_chosen.ingredient.name
            + "  "
            + scoped_chosen.ingredient.unique_id
        )

    return selection_dict


def select_layer_ingredients(source_dict: dict, count: int = 1) -> dict:
    """layers and toppings are slightly different because we have a random number of them
    and we don't necessarily use all the categories"""

    layers_dict = {}
    for scoped in source_dict:
        scoped_layer: ScopedIngredient = source_dict[scoped]
        category = scoped_layer.ingredient.category
        # Split up the layer ingredients dict into lists for each category - makes selecting easier
        if category not in layers_dict.keys():
            layers_dict[category] = list()

        layers_dict[category].append(scoped_layer)

    selection_layers_dict = {}
    for i in range(0, count):
        # randomly select a topping type - can result in duplicate topping types
        topping_types = list(layers_dict.keys())  # The list of topping types
        rand_index = pop_random() % len(topping_types)
        type_name = topping_types[rand_index]
        ingredients_list = layers_dict[type_name]  # list of ScopedIngredients
        # now choose from the list of a specific topping category
        max = len(ingredients_list)
        random = pop_random()
        index = random % max  # Rarity Alert - all options have equal probability

        scoped_ing_chosen: ScopedIngredient = ingredients_list[index]

        selection_layers_dict.update(
            {scoped_ing_chosen.ingredient.unique_id: scoped_ing_chosen}
        )

        print(
            "For a topping we chose "
            + scoped_ing_chosen.ingredient.name
            + "   "
            + scoped_ing_chosen.ingredient.unique_id
        )

    return selection_layers_dict


def _remove_exts(string):

    if string.endswith(
        (".json", ".png", ".gif", ".jpg", ".bmp", ".jpeg", ".ppm", ".datauri")
    ):
        string = string[0 : string.rfind(".")]

    return string


def sample(recipe_id: int) -> Recipe:
    """just a sample"""
    return Recipe(
        unique_id=recipe_id,
        name="My Cool First Super Rare Pizza Test",
        random_seed=get_random(),
        rarity_level=4,
        base_ingredients={
            "box": ScopedIngredient(
                ingredient=Ingredient(
                    unique_id="0000",
                    index=0,
                    name="Cardboard Pizza Box",
                    rarity_level=1,
                    classification=Classification.box,
                    category="cardboard",
                    attributes={"state": "open", "material": "cardboard"},
                    nutrition=NutritionMetadata(
                        servings=1,
                        calories=150.0,
                        fat=0.0,
                        cholesterol=0.0,
                        sodium=0.7,
                        potassium=0.7,
                        carbohydrates=30.1,
                        protein=0.2,
                    ),
                    image_uris={
                        "filename": "0010-box-cardboard.png",
                        "output_mask": "rarepizza-#####-box-%s.png",
                    },
                ),
                scope=IngredientScope(
                    scatter_types=[ScatterType.none],
                    emission_count=(1.0, 1.0),
                    emission_density=(1.0, 1.0),
                    particle_scale=(0.975, 0.975),
                    rotation=(0.00, 0.00),
                ),
            ),
            "paper": ScopedIngredient(
                ingredient=Ingredient(
                    unique_id="0500",
                    index=1,
                    name="Classic Red checker Wax Paper",
                    rarity_level=1,
                    classification=Classification.paper,
                    category="red-checker",
                    attributes={"state": "greasy", "material": "wax"},
                    nutrition=NutritionMetadata(
                        servings=1,
                        calories=150.0,
                        fat=0.0,
                        cholesterol=0.0,
                        sodium=0.7,
                        potassium=0.7,
                        carbohydrates=30.1,
                        protein=0.2,
                    ),
                    image_uris={
                        "filename": "0500-paper-redchecker.png",
                        "output_mask": "rarepizza-#####-paper-%s.png",
                    },
                ),
                scope=IngredientScope(
                    scatter_types=[ScatterType.none],
                    emission_count=(1.0, 1.0),
                    emission_density=(1.0, 1.0),
                    particle_scale=(0.975, 0.975),
                    rotation=(0.00, 0.00),
                ),
            ),
            "crust": ScopedIngredient(
                ingredient=Ingredient(
                    unique_id="1000",
                    index=2,
                    name="New York Style Thin Crust",
                    rarity_level=1,
                    classification=Classification.crust,
                    category="thin",
                    attributes={"state": "overcooked", "material": "traditional"},
                    nutrition=NutritionMetadata(
                        servings=8,
                        calories=260.2,
                        fat=10.5,
                        cholesterol=23,
                        sodium=657.6,
                        potassium=166.14,
                        carbohydrates=30.1,
                        protein=11.5,
                    ),
                    image_uris={
                        "filename": "1000-crust-thin.png",
                        "output_mask": "rarepizza-#####-crust-%s.png",
                    },
                ),
                scope=IngredientScope(
                    scatter_types=[ScatterType.none],
                    emission_count=(1.0, 1.0),
                    emission_density=(1.0, 1.0),
                    particle_scale=(1.0, 1.0),
                    rotation=(0.00, 0.00),
                ),
            ),
        },
        layers={
            "sauce": ScopedIngredient(
                ingredient=Ingredient(
                    unique_id="2000",
                    index=0,
                    name="Traditional Tomato Sauce",
                    rarity_level=1,
                    classification=Classification.sauce,
                    category="traditional",
                    attributes={"state": "thin", "material": "tomato"},
                    nutrition=NutritionMetadata(
                        servings=8,
                        calories=80.5,
                        fat=0.7,
                        cholesterol=0.0,
                        sodium=1151.7,
                        potassium=900.4,
                        carbohydrates=17.7,
                        protein=3.5,
                    ),
                    image_uris={
                        "filename": "2000-sauce-tomato.png",
                        "output_mask": "rarepizza-#####-topping-%s.png",
                    },
                ),
                scope=IngredientScope(
                    scatter_types=[ScatterType.none],
                    emission_count=(1.0, 1.0),
                    emission_density=(1.0, 1.0),
                    particle_scale=(1.0, 1.0),
                    rotation=(0.00, 0.00),
                ),
            ),
            "cheese": ScopedIngredient(
                ingredient=Ingredient(
                    unique_id="3000",
                    index=1,
                    name="Traditional Mozzarella",
                    rarity_level=1,
                    classification=Classification.cheese,
                    category="traditional",
                    attributes={"state": "aged", "vintage": "2007"},
                    nutrition=NutritionMetadata(
                        servings=8,
                        calories=85.1,
                        fat=6.3,
                        cholesterol=22.4,
                        sodium=117.8,
                        potassium=21.5,
                        carbohydrates=0.6,
                        protein=6.3,
                    ),
                    image_uris={
                        "filename": "3000-cheese-mozzarella.png",
                        "output_mask": "rarepizza-#####-topping-%s.png",
                    },
                ),
                scope=IngredientScope(
                    scatter_types=[ScatterType.none],
                    emission_count=(1.0, 1.0),
                    emission_density=(1.0, 1.0),
                    particle_scale=(1.0, 1.0),
                    rotation=(0.00, 0.00),
                ),
            ),
            "topping-1": ScopedIngredient(
                ingredient=Ingredient(
                    unique_id="4000",
                    index=2,
                    name="Pepperoni",
                    rarity_level=1,
                    classification=Classification.topping,
                    category="meat",
                    attributes={"state": "cured", "method": "corned"},
                    nutrition=NutritionMetadata(
                        servings=8,
                        calories=138.3,
                        fat=12.2,
                        cholesterol=29.4,
                        sodium=493.1,
                        potassium=78.1,
                        carbohydrates=0.0,
                        protein=6.4,
                    ),
                    image_uris={
                        "filename": "4000-topping-meat-pepperoni.png",
                        "output_mask": "rarepizza-#####-topping-%s.png",
                    },
                ),
                scope=IngredientScope(
                    scatter_types=[ScatterType.random],
                    emission_count=(5.0, 29.0),
                    emission_density=(0.1, 0.8),
                    particle_scale=(0.19, 0.26),
                    rotation=(-180.0, 180.0),
                ),
            ),
            "topping-2": ScopedIngredient(
                ingredient=Ingredient(
                    unique_id="5000",
                    index=3,
                    name="Tomato",
                    rarity_level=1,
                    classification=Classification.topping,
                    category="fruit",
                    attributes={"state": "fresh"},
                    nutrition=NutritionMetadata(
                        servings=8,
                        calories=22.1,
                        fat=0.2,
                        cholesterol=0.0,
                        sodium=6.2,
                        potassium=291.5,
                        carbohydrates=4.8,
                        protein=1.1,
                    ),
                    image_uris={
                        "filename": "5000-topping-fruit-tomato.png",
                        "output_mask": "rarepizza-#####-topping-%s.png",
                    },
                ),
                scope=IngredientScope(
                    scatter_types=[ScatterType.random],
                    emission_count=(1.0, 20.0),
                    emission_density=(0.1, 0.8),
                    particle_scale=(0.1, 0.22),
                    rotation=(-180.0, 180.0),
                ),
            ),
            "topping-3": ScopedIngredient(
                ingredient=Ingredient(
                    unique_id="6000",
                    index=4,
                    name="Shrimp",
                    rarity_level=1,
                    classification=Classification.topping,
                    category="seafood",
                    attributes={"state": "fresh"},
                    nutrition=NutritionMetadata(
                        servings=8,
                        calories=22.1,
                        fat=0.2,
                        cholesterol=20002.4,
                        sodium=117.8,
                        potassium=21.5,
                        carbohydrates=0.8,
                        protein=6.3,
                    ),
                    image_uris={
                        "filename": "6000-topping-seafood-shrimp.png",
                        "output_mask": "rarepizza-#####-topping-%s.png",
                    },
                ),
                scope=IngredientScope(
                    scatter_types=[ScatterType.random],
                    emission_count=(1.0, 20.0),
                    emission_density=(0.1, 0.8),
                    particle_scale=(0.1, 0.22),
                    rotation=(-180.0, 180.0),
                ),
            ),
        },
        instructions=RecipeInstructions(
            sauce_count=(1, 1),
            cheese_count=(1, 2),
            topping_count=(2, 10),
            extras_count=(1, 3),
            baking_temp_in_celsius=(185, 210),
            baking_time_in_minutes=(15, 30),
        ),
    )
