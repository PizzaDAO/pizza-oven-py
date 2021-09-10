import os.path
import json

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from app.core.config import Settings

from app.models.recipe import *

settings = Settings()
ingredients_dict = {}
recipe_dict = {}

""" Simple USage:
    read_ingredients()
    read_recipes()
    save_json() --> data/recipes/
"""


def read_ingredients():

    values = fetch_sheet_data(
        settings.PIZZA_INGREDIENTS_SHEET, settings.TOPPINGS_RANGE_NAME
    )

    dict = parse_ingredients(values)

    return dict


def read_recipes():

    values = fetch_sheet_data(
        settings.PIZZA_TYPES_SHEET, settings.PIZZA_TYPE_RANGE_NAME
    )

    dict = parse_recipes(values)

    return dict


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
        .get(spreadsheetId=SHEET_NAME, range=RANGE_NAME, majorDimension=DIMENSION)
        .execute()
    )

    values = result.get("values", [])

    return values


# parse the ingredients into a collection we can use to create a recipe
# this mapping is done to the Google Sheet - change the sheet - change this code
def parse_ingredients(values):
    if not values:
        print("Error: We have a problem... No data found for Toppings.")
    else:
        # first get the column headers from 1st row
        attr_names = []
        for name in values[0]:
            attr_names.append(name)
        # Now get all the rows in the sheet
        for r in range(1, len(values)):
            # for r in range(1, 4):
            # Only add the line if there is a numeric ID
            if len(values[r]) > 2:
                row = {}
                for i in range(0, len(values[r])):
                    # Put each attribute in a Key/Value pair for the row
                    row.update({attr_names[i]: values[r][i]})
                # Use the unique ID for the Key and the row Dictionary for the value
                # Easy to look up ingredients by unique id
                try:
                    unique_id = values[r][0]
                except:
                    # Account for the occasional blank row - probably a cleaner way to do this...
                    pass
                finally:
                    ing: ScopedIngredient = parse_ingredient(row)
                    ingredients_dict.update({unique_id: ing})

    # TODO - Make toppings_dict a bonafied toppings datatype
    return ingredients_dict


# parse the pizza types into a collection we can use to drive random recipe making
# this mapping is done to the Google Sheet - change the sheet - change this code
# Using COLUMNS here
def parse_recipes(values):
    if not values:
        print("Error: We have a problem... No data found for Pizza Types.")
    else:
        columns = {}
        for val in values:
            try:
                # taking the 1st element in the column - it containes the pizza type names
                type_name = val[0]
            except:
                # Account for the occasional blank row - probably a cleaner way to do this...
                pass
            finally:
                columns.update({type_name: val})

    # Now we have a Dict of Columns - pizza type string : raw column data
    pizza_types = list(columns.keys())
    for header in pizza_types:
        data = columns[header]
        recipe: Recipe = parse_column(data)
        save_json(recipe)
        recipe_dict.update({header: recipe})

    return recipe_dict


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

    classification = Classification.box

    ingredient = Ingredient(
        unique_id=row["unique_id"],
        index=1,
        name=row["topping"],
        rarity_level=1,
        classification=classification,
        category=row["category"],
        attributes={},
        nutrition=nutrition,
        image_uris=[],
    )

    scoped = ScopedIngredient(
        ingredient=ingredient,
        scope=IngredientScope(
            scatter_types=[],
            emission_count=[25.0, 50.0],
            emission_density=[0.10, 0.99],
            particle_scale=[0.05, 0.15],
            rotation=[-3.14159, 3.14159],
        ),
    )

    return scoped


def parse_id(text) -> str:
    words = text.split("-")
    id_string = words[0]

    return id_string


def parse_column(raw_column) -> Recipe:
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

            try:
                ing: ScopedIngredient = ingredients_dict[unique_id]
            except:
                print("This ingredient doesn't exist")
                print("looking for: " + unique_id)

            finally:
                category = ing.ingredient.category

                # Basic seperation of ingredients into base and layered lists
                if category in base_categories:
                    base_dict.update({unique_id: ing})
                else:
                    layers_dict.update({unique_id: ing})

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
            sauce_count=[0.0, 1.0],
            cheese_count=[0.0, 1.0],
            topping_count=[0.0, 1.0],
            extras_count=[0.0, 1.0],
            baking_temp_in_celsius=[0.0, 1.0],
            baking_time_in_minutes=[0.0, 1.0],
        ),
    )

    return recipe


def save_json(recipe: Recipe):
    # Pretty Print JSON
    json_formatted_str = json.loads(recipe.json())

    filename = recipe.name + ".json"
    path = "data/recipes/" + filename

    with open(path, "w") as outfile:
        json.dump(json_formatted_str, outfile, indent=4)
