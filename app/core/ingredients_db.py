from typing import Dict, Any, Optional, Tuple
import os.path
import json

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from app.core.config import Settings

from app.models.recipe import *
from app.models.recipe import Rarity

settings = Settings()

# Make environment variables
TOPPING_PIXEL_SIZE = 1024
BASE_PIXEL_SIZE = 3072

__all__ = [
    "read_ingredients",
    "read_recipes",
    "fetch_sheet_data",
    "parse_ingredients",
    "parse_recipes",
    "save_recipe",
]

""" Simple USage:
    ingredients = read_ingredients()
    receipts = read_recipes(ingredients)
    save_json() --> data/recipes/
"""


def read_ingredients():

    values = fetch_sheet_data(
        settings.PIZZA_INGREDIENTS_SHEET, settings.TOPPINGS_RANGE_NAME
    )

    return parse_ingredients(values)


def read_recipes(ingredients: Dict[Any, ScopedIngredient]):

    values = fetch_sheet_data(
        settings.PIZZA_TYPES_SHEET, settings.PIZZA_TYPE_RANGE_NAME
    )

    return parse_recipes(values, ingredients)


def fetch_sheet_data(SHEET_NAME, RANGE_NAME):
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    #
    #
    # Token is manually generated and placed in the Data folder - Not very secure - quick hack
    #

    scopes = [settings.SCOPE]

    if os.path.exists(settings.TOKEN_PATH):
        print("Found AUTH token...")
        creds = Credentials.from_authorized_user_file(settings.TOKEN_PATH, scopes)
    # If there are no (valid) credentials available, let the user log in. BUT this will fail in Docker ENV
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                settings.CREDENTIALS_PATH, scopes
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(settings.TOKEN_PATH, "w") as token:
            token.write(creds.to_json())

    DIMENSION = "ROWS"  # default is ROWS
    # Better way to do this
    if RANGE_NAME is settings.PIZZA_TYPE_RANGE_NAME:
        DIMENSION = "COLUMNS"  # Need to get Columns

    service = build("sheets", "v4", credentials=creds)

    # Call the Sheets API
    # Get the Toppings
    sheet = service.spreadsheets()
    result = (
        sheet.values()
        .get(
            spreadsheetId=SHEET_NAME,
            range=RANGE_NAME,
            majorDimension=DIMENSION,
            valueRenderOption="FORMATTED_VALUE",
        )
        .execute()
    )

    values = result.get("values", [])

    return values


# parse the ingredients into a collection we can use to create a recipe
# this mapping is done to the Google Sheet - change the sheet - change this code
def parse_ingredients(sheet_data) -> Optional[Dict]:
    if not sheet_data:
        print("Error: We have a problem... No data found for Toppings.")
        return None

    ingredients = {}

    # first get the column headers from 1st row
    column_headers = []
    for name in sheet_data[0]:
        column_headers.append(name)

    current_ingredient_code = "000"
    current_rarity: Rarity = Rarity.common
    # Now get all the rows in the sheet
    for row in range(1, len(sheet_data)):
        # Only add the line if there is a numeric ID
        if len(sheet_data[row]) > 2:
            record_entry = {}
            for index in range(0, len(sheet_data[row])):
                # Put each attribute in a Key/Value pair for the row
                record_entry.update({column_headers[index]: sheet_data[row][index]})

            # Use the unique ID for the Key and the row Dictionary for the value
            # Easy to look up ingredients by unique id
            if sheet_data[row][0] and record_entry["on_disk"] == "Y":
                # Get the 3-digit ingredient code
                next_ingredient_code = sheet_data[row][0][0:3]

                if (
                    next_ingredient_code
                    and next_ingredient_code != current_ingredient_code
                ):
                    current_ingredient_code = next_ingredient_code
                    # Assign topping rarity here for all variants of an ingredient
                    # We do this here in order to track the ingredient code
                    if record_entry["topping rarity"]:
                        current_rarity = map_rarity(record_entry["topping rarity"])
                    else:
                        current_rarity = Rarity.undefined

                unique_id = sheet_data[row][0]
                ingredient: ScopedIngredient = parse_ingredient(record_entry)
                # Assign top level id and rarity to ingredient
                ingredient.ingredient.ingredient_rarity = current_rarity
                ingredient.ingredient.ingredient_id = current_ingredient_code
                ingredients.update({unique_id: ingredient})
            else:
                # Account for the occasional blank row - probably a cleaner way to do this...
                print("parse_ingredient: no unique id for row  " + str(row))
                # print(record_entry)

    # TODO - Make toppings_dict a bonafied toppings datatype
    return ingredients


def map_rarity(rarity_string) -> Rarity:
    """map strings from google sheet to Rrity enum"""

    if rarity_string == "common":
        return Rarity.common
    if rarity_string == "uncommon":
        return Rarity.uncommon
    if rarity_string == "rare":
        return Rarity.rare
    if rarity_string == "epic":
        return Rarity.epic
    if rarity_string == "grail":
        return Rarity.grail
    if rarity_string is None:
        return Rarity.undefined

    # shouldn't get here
    return Rarity.undefined


# parse the pizza types into a collection we can use to drive random recipe making
# this mapping is done to the Google Sheet - change the sheet - change this code
# Using COLUMNS here
def parse_recipes(
    values, ingredients: Dict[Any, ScopedIngredient]
) -> Optional[Dict[Any, Recipe]]:
    if not values:
        print("Error: We have a problem... No data found for Pizza Types.")
        return None

    recipes = {}
    columns = {}
    for val in values:
        if val[0]:
            # taking the 1st element in the column - it containes the pizza type names
            type_name = val[0]
            columns.update({type_name: val})
        else:
            # Account for the occasional blank row - probably a cleaner way to do this...
            print("parse_recipes: no id.")

    # Now we have a Dict of Columns - pizza type string : raw column data
    pizza_types = list(columns.keys())
    for header in pizza_types:
        data = columns[header]
        recipe: Recipe = parse_column(data, ingredients)
        recipes.update({header: recipe})

    return recipes


def parse_ingredient(row) -> ScopedIngredient:
    """Most of these are placeholders for the moment - Only 3 values in Ingredient are added from the spreadsheets"""

    nutrition = NutritionMetadata(
        servings=1.0,
        calories=1.0,
        fat=1.0,
        cholesterol=1.0,
        sodium=1.0,
        potassium=1.0,
        carbohydrates=1.0,
        protein=1.0,
    )

    category = row["category"]
    classification = classification_from_string(category)

    image_uri = row["filename_paste"] + ".png"
    mask = "rarepizza-#####-" + category  # Will be overwritten by Renderer
    variant_rarity = map_rarity(row["variant rarity"])
    variant_id = row["unique_id"][3:4]
    ingredient = Ingredient(
        unique_id=row["unique_id"],
        ingredient_id="00",
        variant_id=variant_id,
        index=1,
        name=row["topping"],
        ingredient_rarity=Rarity.common,
        variant_rarity=variant_rarity,
        classification=classification,
        category=category,
        attributes={},
        nutrition=nutrition,
        image_uris={"filename": image_uri, "output_mask": mask},
    )

    # Create a default ScopedIngredient
    scoped = ScopedIngredient(
        ingredient=ingredient,
        scope=IngredientScope(
            scatter_types=[ScatterType.none],
            emission_count=[1.0, 24.0],
            emission_density=[0.10, 0.99],
            particle_scale=[0.2, 0.75],
            rotation=[-180, 180],
        ),
    )

    scoped.scope = parse_ranges(row, scoped.scope)

    return scoped


def parse_ranges(row, scope: IngredientScope) -> IngredientScope:
    # Add the scope options: on_disk(not used):inches:inch_variance:min_per:max_per:pie_count:scatters:description
    # Use if statements to defend against blank cells
    if "min_per" in row.keys() and "max_per" in row.keys():
        if row["min_per"].isnumeric() and row["max_per"].isnumeric():
            scope.emission_count = (float(row["min_per"]), float(row["max_per"]))

    # An ungly chain of IFs to make sure all the values are there before we operate
    if "inches" in row.keys():
        if row["inches"].isnumeric():
            inches = float(row["inches"])

            if "inch_variance" in row.keys():
                if row["inch_variance"].isnumeric():
                    inch_variance = float(row["inch_variance"])

                    base_categories = ["crust", "sauce", "cheese"]
                    if row["category"] in base_categories:
                        scope.particle_scale = get_scale_values(
                            inches, inch_variance, BASE_PIXEL_SIZE
                        )
                    else:
                        scope.particle_scale = get_scale_values(
                            inches, inch_variance, TOPPING_PIXEL_SIZE
                        )

    return scope


def get_scale_values(inches, variance, pixel_size) -> Tuple[float, float]:
    min_size = inches - variance
    max_size = inches + variance
    # toppings are 1024x1024, pies 3072x3072 and 18” so the math is (size/6)*1024
    min_scale = min_size / (18 / (3072 / pixel_size))
    max_scale = max_size / (18 / (3072 / pixel_size))

    return (min_scale, max_scale)


def parse_id(text) -> str:
    words = text.split("-")
    id_string = words[0]

    return id_string


def parse_column(raw_column, ingredients: Dict[Any, ScopedIngredient]) -> Recipe:
    """parse all the options"""
    base_categories = ["box", "paper", "crust", "sauce", "cheese"]
    # layer_categories = ["saver", "seasoning", "squirt", "topping"]
    base_dict = {}
    layers_dict = {}
    for i in range(1, len(raw_column)):
        line = raw_column[i]

        # Hacky test to make sure we are not parsing a blank cell in the spreadsheet
        if "-" in line:
            # pull out the unique_id for each ingredient
            unique_id = parse_id(line)

            if ingredients.get(unique_id):
                ingredient = ingredients[unique_id]
                category = ingredient.ingredient.category

                # Basic seperation of ingredients into base and layered lists
                if category in base_categories:
                    base_dict.update({unique_id: ingredient})
                else:
                    layers_dict.update({unique_id: ingredient})
            else:
                print("This ingredient doesn't exist")
                print("looking for: " + unique_id)

    pie_type = raw_column[0]

    recipe = Recipe(
        unique_id=1,
        name=pie_type,
        random_seed="0x99",
        rarity_level=3.0,
        base_ingredients=base_dict,
        layers=layers_dict,
        # Where do recipe instructions come from??
        # Can this be optional for the Recipe, added later?
        instructions=RecipeInstructions(
            crust_count=1,
            sauce_count=[1, 1],
            cheese_count=[1, 1],
            topping_count=[0, 8],
            extras_count=[0, 2],
            baking_temp_in_celsius=[395, 625],
            baking_time_in_minutes=[5, 10],
        ),
    )

    return recipe


def save_recipe(recipe: Recipe):
    # Pretty Print JSON
    json_formatted_str = json.loads(recipe.json())

    path = "data/recipes/"

    filename = recipe.name + ".json"
    absolute_filepath = os.path.join(path, filename)

    # create the directory if it doesnt exist
    if not os.path.exists("data/recipes"):
        os.makedirs(path)

    with open(absolute_filepath, "w") as outfile:
        json.dump(json_formatted_str, outfile, indent=4)
