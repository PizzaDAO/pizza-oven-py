from typing import Dict, Any, Optional, Tuple, List
import os.path
import json

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from app.core.config import Settings

from app.models.recipe import *
from app.models.recipe import Rarity
from app.models.auth_tokens import GSheetsToken

from app.core.repository import get_gsheets_token, set_gsheets_token

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
    "save_ingredients",
    "get_variants_for_ingredient",
]

""" Simple USage:
    ingredients = read_ingredients()
    receipts = read_recipes(ingredients)
    save_json() --> data/recipes/
"""

# A dictionary for storing Box and Paper ingredients
box_paper_dict: Dict[str, ScopedIngredient] = {}


def read_ingredients():
    print("read_ingredients")
    values = fetch_sheet_data(
        settings.PIZZA_INGREDIENTS_SHEET, settings.TOPPINGS_RANGE_NAME
    )

    return parse_ingredients(values)


def read_recipes(ingredients: Dict[Any, ScopedIngredient]):
    print("read_recipes")
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

    print(f"fetch_sheet_data {SHEET_NAME} {RANGE_NAME}")

    scopes = [settings.SCOPE]

    # try to fetch the auth token from the data store before
    # trying to get it from the file system
    # this code is a bit hacky and is done to maintain compatibility
    creds = None

    internal_gsheets_creds = get_gsheets_token()
    if internal_gsheets_creds is not None:
        print("found cached Gsheets auth credentials in the datastore")
        creds = Credentials(
            token=internal_gsheets_creds.token,
            refresh_token=internal_gsheets_creds.refresh_token,
            token_uri=internal_gsheets_creds.token_uri,
            client_id=internal_gsheets_creds.client_id,
            client_secret=internal_gsheets_creds.client_secret,
            scopes=internal_gsheets_creds.scopes,
            expiry=internal_gsheets_creds.expiry.replace(tzinfo=None),
        )

    if creds is not None:
        print("refreshing cached Gsheets auth token using the refresh token")
        try:
            creds.refresh(Request())
        except Exception as error:
            print(error)

    if (creds is None or not creds.valid) and os.path.exists(
        settings.GOOGLE_SHEETS_TOKEN_PATH
    ):
        print(
            "Gsheet Auth not found or invalid in server instance, falling back to file system"
        )
        creds = Credentials.from_authorized_user_file(
            settings.GOOGLE_SHEETS_TOKEN_PATH, scopes
        )

        if creds is not None:
            print("refreshing cached Gsheets auth token using the refresh token")
            try:
                creds.refresh(Request())
            except Exception as error:
                print(error)

    # If there are no (valid) credentials available, let the user log in.
    # BUT this will fail in Docker ENV
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("refreshing gsheets auth token using the refresh token")
            try:
                creds.refresh(Request())
            except Exception as error:
                print(error)
                return
        else:
            print("trying to refresh auth token with installed app flow")
            flow = InstalledAppFlow.from_client_secrets_file(
                settings.GOOGLE_SHEETS_CREDENTIALS_PATH, scopes
            )
            creds = flow.run_local_server(port=0)

    if creds and creds.valid:
        print("updating credentials")
        # Save the credentials for the next run
        internal_creds = GSheetsToken(
            token=creds.token,
            refresh_token=creds.refresh_token,
            token_uri=creds.token_uri,
            client_id=creds.client_id,
            client_secret=creds.client_secret,
            scopes=creds.scopes,
            expiry=creds.expiry.replace(tzinfo=None),
        )
        set_gsheets_token(internal_creds)
        try:
            with open(settings.GOOGLE_SHEETS_TOKEN_PATH, "w") as token:
                token.write(creds.to_json())
        except:
            print("could not write to google sheet token: read only filesystem")

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
        print(
            "parse_ingredients: Error: We have a problem... No data found for Toppings."
        )
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
        # Only add the line if there are at least 16 cells - BRITTLE look out for DB changes
        if len(sheet_data[row]) >= 16:
            record_entry = {}
            for index in range(0, len(sheet_data[row])):
                # Put each attribute in a Key/Value pair for the row
                record_entry.update({column_headers[index]: sheet_data[row][index]})

            # Use the unique ID for the Key and the row Dictionary for the value
            # Easy to look up ingredients by unique id
            if sheet_data[row][0] and record_entry["on_disk"] == "Y":
                # check to see if the png is in ingredients-db folder
                filename = record_entry["filename_paste"] + ".png"
                absolute_filepath = os.path.join(
                    settings.LOCAL_INGREDIENTS_DB_PATH, filename
                )
                if not os.path.exists(absolute_filepath):
                    print(f"Missing image for ingredient: {absolute_filepath}")

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

                # Pull out the Box and Paper ingredients for later
                if unique_id[0] == "0":
                    box_paper_dict.update({unique_id: ingredient})
        else:
            print(
                "Wrong number of cells in row... Maybe missing a period in row "
                + sheet_data[row][0]
            )
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
        # Check to see if there is a name on the first cell
        # Of the recipe sheet is changed, this can fail - currently have "." in the first cell of the sheet to compare against
        if len(val[0]) > 1:
            # taking the 1st element in the column - it containes the pizza type names
            type_name = val[0]
            columns.update({type_name: val})
        else:
            # Account for the occasional blank row - probably a cleaner way to do this...
            print("parse_recipes: no id found - most likely a blank column")

    # Now we have a Dict of Columns - pizza type string : raw column data
    pizza_types = list(columns.keys())
    recipe_id = 0
    for header in pizza_types:
        data = columns[header]
        recipe: Recipe = parse_column(recipe_id, data, ingredients)

        # Add the Box and Paper ingredients to the base_ingredient Dict
        recipe.base_ingredients.update(box_paper_dict)

        recipes.update({header: recipe})
        recipe_id += 1

    return recipes


def parse_ingredient(row) -> ScopedIngredient:
    """parse ScopedIngredient from a row in the database"""

    category = parse_first_word(row["category"])
    classification = classification_from_string(category)

    image_uri = row["filename_paste"] + ".png"
    mask = "rarepizza-#####-" + category  # Will be overwritten by Renderer
    variant_rarity = map_rarity(row["variant rarity"])
    variant_id = row["unique_id"][3:4]

    nutrition = parse_nutrition(row)

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

    if has_value("min_per", row) and has_value("max_per", row):
        scope.emission_count = (float(row["min_per"]), float(row["max_per"]))

    if has_value("rotation", row):
        r_min = float(row["rotation"]) * -1
        r_max = float(row["rotation"])
        scope.rotation = (r_min, r_max)
    else:
        scope.rotation = (-180, 180)

    if has_value("inches", row):
        inches = float(row["inches"])

        if has_value("inch_variance", row):
            inch_variance = float(row["inch_variance"])

            base_categories = ["box", "paper", "crust", "sauce", "cheese"]
            special_categories = ["lastchance"]
            # need to pull out primary category - the first word before the first dash
            primary_category = parse_first_word(row["category"])
            if (
                primary_category in base_categories
                or primary_category in special_categories
            ):
                scope.particle_scale = get_scale_values(
                    inches, inch_variance, BASE_PIXEL_SIZE
                )
                # force no scatter type here fir base and lastchance
                scope.scatter_types = [ScatterType.none]
            else:
                scope.particle_scale = get_scale_values(
                    inches, inch_variance, TOPPING_PIXEL_SIZE
                )

    return scope


def has_value(label: str, row) -> bool:
    if label in row.keys():
        if row[label].replace(".", "", 1).isdigit():
            return True

    return False


def get_scale_values(inches, variance, pixel_size) -> Tuple[float, float]:
    min_size = inches - variance
    max_size = inches + variance
    # toppings are 1024x1024, pies 3072x3072 and 18” so the math is (size/6)*1024
    min_scale = min_size / (18 / (3072 / pixel_size))
    max_scale = max_size / (18 / (3072 / pixel_size))

    return (min_scale, max_scale)


def parse_first_word(text) -> str:
    words = text.split("-")
    id_string = words[0]

    return id_string


def parse_column(
    recipe_id: int, raw_column, ingredients: Dict[Any, ScopedIngredient]
) -> Recipe:
    """parse all the options"""
    base_categories = ["box", "paper", "crust", "sauce", "cheese"]
    base_dict = {}
    layers_dict = {}
    lastchance_dict = {}
    for i in range(1, len(raw_column)):
        line = raw_column[i]

        # Hacky test to make sure we are not parsing a blank cell in the spreadsheet
        if "-" in line:
            # pull out the unique_id for each ingredient
            unique_id = parse_first_word(line)

            if ingredients.get(unique_id):
                ingredient = ingredients[unique_id]
                category = ingredient.ingredient.category

                # Basic seperation of ingredients into base and layered lists
                if ingredient.ingredient.classification == Classification.topping:
                    layers_dict.update({unique_id: ingredient})

                elif ingredient.ingredient.classification == Classification.lastchance:
                    lastchance_dict.update({unique_id: ingredient})

                elif category in base_categories:
                    base_dict.update({unique_id: ingredient})

            else:
                print(
                    "Recipe %s contains non-existant ingredient with id: %s"
                    % (raw_column[0], unique_id)
                )

    pie_type = raw_column[0]

    recipe = Recipe(
        unique_id=recipe_id,
        name=pie_type,
        rarity_level=3.0,
        base_ingredients=base_dict,
        layers=layers_dict,
        lastchances=lastchance_dict,
        # Where do recipe instructions come from??
        # Can this be optional for the Recipe, added later?
        instructions=RecipeInstructions(
            crust_count=1,
            sauce_count=[1, 1],
            cheese_count=[1, 1],
            topping_count=[
                settings.MIN_TOPPING_LAYER_COUNT,
                settings.MAX_TOPPING_LAYER_COUNT,
            ],
            lastchance_count=[0, 1],
            baking_temp_in_celsius=[395, 625],
            baking_time_in_minutes=[5, 10],
        ),
    )

    return recipe


def save_recipe(recipe: Recipe):
    # Pretty Print JSON
    json_formatted_str = json.loads(recipe.json())

    filename = recipe.name + ".json"
    absolute_filepath = os.path.join(settings.lOCAL_RECIPES_PATH, filename)

    # create the directory if it doesnt exist
    if not os.path.exists(settings.lOCAL_RECIPES_PATH):
        print(f"save_recipe: making directory: {absolute_filepath}")
        os.makedirs(settings.lOCAL_RECIPES_PATH)

    print(f"save_recipe: {absolute_filepath}")
    with open(absolute_filepath, "w") as outfile:
        json.dump(json_formatted_str, outfile, indent=4)


def save_ingredients(ingredient_dict):

    list = []
    for k, v in ingredient_dict.items():
        list.append(json.loads(v.json()))

    absolute_filepath = os.path.join(
        settings.lOCAL_INGREDIENT_DB_MANIFEST_PATH,
        settings.LOCAL_INGREDIENT_DB_MANIFEST_FILENAME,
    )

    # create the directory if it doesnt exist
    if not os.path.exists(settings.lOCAL_INGREDIENT_DB_MANIFEST_PATH):
        print(f"save_ingredients: making directory: {absolute_filepath}")
        os.makedirs(settings.lOCAL_INGREDIENT_DB_MANIFEST_PATH)

    print(f"save_ingredients: {absolute_filepath}")
    with open(absolute_filepath, "w") as outfile:
        json.dump(list, outfile, indent=4)


def get_variants_for_ingredient(ingredient_id: str) -> List:
    # load the ingredients JSON and pull out the variants

    variants: List[ScopedIngredient] = []
    path = os.path.join(
        settings.lOCAL_INGREDIENT_DB_MANIFEST_PATH,
        settings.LOCAL_INGREDIENT_DB_MANIFEST_FILENAME,
    )
    try:
        f = open(path)
        contents = json.load(f)
        for item in contents:
            scoped = ScopedIngredient.parse_obj(item)
            if scoped.ingredient.ingredient_id == ingredient_id:
                variants.append(scoped)
        f.close()

    except Exception as error:
        print(
            f"get_variants_for_ingredient: Error variants of {ingredient_id} at path: {path}"
        )
        print(error)

    return variants


def parse_nutrition(row) -> NutritionMetadata:
    # NUTRITIONAL DATA
    if has_value("serving_size", row):
        data = NutritionMetadata(
            serving_size=row["serving_size"],
            mass=row["mass"],
            calories=row["calories"],
            vitamin_c=row["vitamin_c"],
            magnesium=row["magnesium"],
            vitamin_b5=row["vitamin_b5"],
            vitamin_d=row["vitamin_d"],
            vitamin_b7=row["vitamin_b7"],
            height=row["height"],
            moisture=row["moisture"],
            potassium=row["potassium"],
            cholesterol=row["cholesterol"],
            vitamin_a=row["vitamin_a"],
            dietary_fiber=row["dietary_fiber"],
            vitamin_b6=row["vitamin_b6"],
            sugar=row["sugar"],
            protein=row["protein"],
            iron=row["iron"],
            complex_carb=row["complex_carb"],
            selenium=row["selenium"],
            vitamin_k=row["vitamin_k"],
            vitamin_b12=row["vitamin_b12"],
            calories_from_fat=row["calories_from_fat"],
            vitamin_e=row["vitamin_e"],
            zinc=row["zinc"],
            saturated_fat=row["saturated_fat"],
            iodine=row["iodine"],
            trans_fat=row["trans_fat"],
            sodium=row["sodium"],
            monosaturated_fat=row["monosaturated_fat"],
            calcium=row["calcium"],
            riboflavin=row["riboflavin"],
            thiamin=row["thiamin"],
            folate=row["folate"],
            added_sugar=row["added_sugar"],
            chromium=row["chromium"],
            manganese=row["manganese"],
        )
    else:
        data = NutritionMetadata(
            serving_size=0,
            mass=0,
            calories=0,
            vitamin_c=0,
            magnesium=0,
            vitamin_b5=0,
            vitamin_d=0,
            vitamin_b7=0,
            height=0,
            moisture=0,
            potassium=0,
            cholesterol=0,
            vitamin_a=0,
            dietary_fiber=0,
            vitamin_b6=0,
            sugar=0,
            protein=0,
            iron=0,
            complex_carb=0,
            selenium=0,
            vitamin_k=0,
            vitamin_b12=0,
            calories_from_fat=0,
            vitamin_e=0,
            zinc=0,
            saturated_fat=0,
            iodine=0,
            trans_fat=0,
            sodium=0,
            monosaturated_fat=0,
            calcium=0,
            riboflavin=0,
            thiamin=0,
            folate=0,
            added_sugar=0,
            chromium=0,
            manganese=0,
        )

    return data