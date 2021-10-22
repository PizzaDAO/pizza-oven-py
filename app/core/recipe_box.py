from genericpath import exists
import hashlib
from os import listdir, path
from os.path import isfile, join, exists
import json
from typing import Dict, Optional, List, Tuple

from app.core.ingredients_db import *
from app.core.ingredients_db import save_ingredients
from app.models.recipe import *
from app.core.repository import get_recipe

lOCAL_RECIPES_PATH = "data/recipes/"
lOCAL_INGREDIENT_DB_PATH = "data/ingredients/"


def get_pizza_recipe(recipe_id: int) -> Recipe:
    """load recipes if needed, then return the recipe type requested"""

    recipe = get_recipe(recipe_id)
    if recipe is not None:
        print("recipe loaded from cache")
        return recipe

    # Make sure we previously loaded recipes files from /data/recipes
    (names, recipes) = load_recipes()

    # Default to random pie if no type supplied, or type is not found
    if recipe_id >= len(recipes):
        print(f"recipe_id: not found: {recipe_id}")
        pizza_type = "Random Pies"  # For now, default to a random pie
    else:
        pizza_type = names[recipe_id]
        print(f"recipe_id: {recipe_id} pizza_type: {pizza_type}")

    # convert the json to a Recipes object
    recipe_json = recipes[pizza_type]

    recipe = Recipe.parse_obj(recipe_json)

    print("recipe loaded from data folder (old method)")

    return recipe


def load_recipes() -> Tuple[List[str], Dict]:
    """Load all the json recipes generated from the spreadsheets from /data folder"""

    print("loading recipe files")
    # check contents of data/recipes folder
    file_list = []

    recipes_dict = {}
    recipe_names = []

    if not exists(lOCAL_RECIPES_PATH):
        ingredients = read_ingredients()

        if not path.exists(lOCAL_INGREDIENT_DB_PATH + "ingredient_db.json"):
            print("Loading and saving the ingredient db")
            save_ingredients(ingredients)

        recipes = read_recipes(ingredients)
        for _, recipe in recipes.items():
            save_recipe(recipe)

    try:
        file_list = [
            f
            for f in listdir(lOCAL_RECIPES_PATH)
            if isfile(join(lOCAL_RECIPES_PATH, f))
        ]
    except Exception as e:
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
            except Exception as e:
                print("Ignoring this file: " + file)

    return (recipe_names, recipes_dict)


def _remove_exts(string):

    if string.endswith(
        (".json", ".png", ".gif", ".jpg", ".bmp", ".jpeg", ".ppm", ".datauri")
    ):
        string = string[0 : string.rfind(".")]

    return string
