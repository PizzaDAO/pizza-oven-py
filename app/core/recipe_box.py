from app.models.recipe import *

from app.core.random import get_random


def make_recipe() -> Recipe:

    # TODO: deterministically derive the ingredients for the recipe
    # based ona random seed
    return sample(1)


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