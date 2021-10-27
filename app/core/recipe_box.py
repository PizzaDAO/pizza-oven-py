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

from app.core.config import ApiMode, Settings

settings = Settings()

RANDOM_RECIPE_ID = 0


def get_pizza_recipe(recipe_id: int) -> Optional[Recipe]:
    """load recipes if needed, then return the recipe type requested"""

    recipe = get_recipe(recipe_id)
    if recipe is not None:
        print("recipe loaded from cache")
        return recipe

    print("recipe not found, returning the random pie")
    recipe = get_recipe(RANDOM_RECIPE_ID)
    return recipe


def load_recipes() -> Tuple[List[str], Dict]:
    """Load all the json recipes generated from the spreadsheets from /data folder"""

    print("loading recipe files")
    # check contents of data/recipes folder
    file_list = []

    recipes_dict = {}
    recipe_names = []

    # if it doesnt exist try to load it
    if not exists(settings.lOCAL_RECIPES_PATH):
        ingredients = read_ingredients()

        print("Loading and saving the ingredient db")
        save_ingredients(ingredients)

        recipes = read_recipes(ingredients)
        for _, recipe in recipes.items():
            save_recipe(recipe)

    try:
        file_list = [
            f
            for f in listdir(settings.lOCAL_RECIPES_PATH)
            if isfile(join(settings.lOCAL_RECIPES_PATH, f))
        ]
    except Exception as error:
        print("Can't get list of recipe files")
    finally:
        for file in file_list:
            try:
                f = open(path.join(settings.lOCAL_RECIPES_PATH, file))
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
