#!/usr/bin/env python

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from math import ceil
import os
import json

from app.models.recipe import Classification
from app.models.recipe import scatter_to_string
from app.models.prep import (
    KitchenOrder,
    MadeIngredient,
    ShuffledLayer,
    MadeIngredientPrep,
)

from app.core.config import Settings

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw


current = os.path.dirname(os.path.realpath(__file__))
settings = Settings()

DATA_FONT_SIZE = 48
WATERMARK_FILE = "pizza_watermark.png"


@dataclass
class SimpleRenderer:
    def render_pizza(self, order: KitchenOrder) -> Image:
        """render the pizza out to the file systme using natron"""

        current_directory = os.path.dirname(__file__)
        images_db = os.path.split(current_directory)[0] + "/../../ingredients-db"

        # BASE
        base = Image.new(mode="RGB", size=(3072, 3072), color=(125, 125, 125))
        # iterate through each the base ingredients and render
        for (_, ingredient) in order.base_ingredients.items():
            filename = ingredient.ingredient.image_uris["filename"]
            file = os.path.join(images_db, filename)
            print("pasting: " + filename)
            try:
                image = Image.open(file)

                prep = ingredient.instances[0]
                w = int(image.width * prep.scale)
                h = int(image.height * prep.scale)
                newsize = (w, h)
                image = image.resize(newsize, Image.BICUBIC)
                x = int((base.width - image.width) / 2)
                y = int((base.height - image.height) / 2)

                base.paste(image, (x, y), image)
            except Exception as e:
                print("skipping image... can't find " + filename)

        # TOPPINGS
        toppings = Image.new(mode="RGBA", size=(3072, 3072))
        image_cache = {}
        for (_, ingredient) in order.layers.items():
            filename = ingredient.ingredient.image_uris["filename"]
            file = os.path.join(images_db, filename)
            print("pasting: " + filename)

            for i in range(0, len(ingredient.instances)):
                prep = ingredient.instances[i]
                if prep.image_uri:
                    filename = prep.image_uri
                    # creating a simple image cache - seems to speed this up and it matters when running hundreds of recipes
                    if filename in image_cache.keys():
                        image = image_cache[filename]
                    else:
                        file = os.path.join(images_db, filename)
                        try:
                            image = Image.open(file).convert("RGBA")
                            image_cache.update({filename: image})
                        except Exception as e:
                            print("skipping image... can't find " + filename)

                print("pasting: " + filename)
                # Cale image based on 1024 pixel dimension
                n = int(1024 * prep.scale)
                newsize = (n, n)
                scaled = image.resize(newsize, Image.BICUBIC)
                # place image in canvas and adjust for new width and height - centered
                x = int(prep.translation[0] - (newsize[0] / 2))
                y = int(prep.translation[1] - (newsize[0] / 2))

                # rotate around the center
                rot = int(prep.rotation)
                rotated = scaled.rotate(
                    rot,
                    Image.NEAREST,
                    center=(scaled.width / 2, scaled.height / 2),
                    expand=1,
                )

                # Transalate due to differeent coordinate spaces - 0,0 is top left for PIL, bottom left for Natron
                half = int(3072 / 2)
                if y > half:
                    y = y - ((y - half) * 2) - n
                else:
                    y = y + ((half - y) * 2) - n

                toppings.paste(rotated, (x, y), rotated)

        # mimic the global scale bump performed in Natron
        s = int(3072 * 0.75)
        bump = (s, s)
        toppings = toppings.resize(bump, Image.BICUBIC)
        x = (base.width - toppings.width) / 2  # -128
        y = (base.height - toppings.height) / 2  # -128

        base.paste(toppings, (int(x), int(y)), toppings)

        # LASTCHANCES
        for (_, ingredient) in order.lastchances.items():
            filename = ingredient.ingredient.image_uris["filename"]
            file = os.path.join(images_db, filename)
            print("pasting: " + filename)
            try:
                image = Image.open(file)

                prep = ingredient.instances[0]
                w = int(image.width * prep.scale)
                h = int(image.height * prep.scale)
                newsize = (w, h)
                image = image.resize(newsize, Image.BICUBIC)
                x = int((base.width - image.width) / 2)
                y = int((base.height - image.height) / 2)

                base.paste(image, (x, y), image)
            except Exception as e:
                print("skipping image... can't find " + filename)

        self.draw_watermark(base, order)

        print("WE done")

        return base

    def draw_watermark(self, base: Image, order: KitchenOrder):
        """draw a watermark on the pizza"""
        print("draw_watermark")

        draw = ImageDraw.Draw(base)

        current_directory = os.path.dirname(__file__)
        font_path = (
            os.path.split(current_directory)[0] + "/../../fonts/Roboto-Medium.ttf"
        )

        font = ImageFont.truetype(font_path, DATA_FONT_SIZE)
        base_ingredients = ""
        for ingredient in order.base_ingredients.values():
            i = ingredient.ingredient
            base_ingredients += i.unique_id + " " + i.name + " " + i.category + "\n"
        layer_ingredients = ""
        for ingredient in order.layers.values():
            i = ingredient.ingredient
            scatter_type = ingredient.scatter_type
            layer_ingredients += (
                i.unique_id
                + " "
                + i.name
                + " - "
                + i.category
                + " - scatter_type: "
                + scatter_to_string(scatter_type)
                + "\n"
            )
        lastchances_ingredients = ""
        for ingredient in order.lastchances.values():
            i = ingredient.ingredient
            lastchances_ingredients += (
                i.unique_id + " " + i.name + " - " + i.category + "\n"
            )
        pizza_data = (
            "Pizza_id: "
            + str(order.token_id)
            + "\n"
            + "Recipe_id: "
            + str(order.recipe_id)
            + "\n"
            + "Pizza_type: "
            + str(order.name)
            + "\n"
            + "Random_seed: "
            + str(order.random_seed)
            + "\n\n"
            + "Base_layers:\n"
            + base_ingredients
            + "\n"
            + "Layers:\n"
            + layer_ingredients
            + "\n"
            + "Lastchances:\n"
            + lastchances_ingredients
        )
        draw.text((10, 10), pizza_data, fill="white", font=font, align="left")

        # add watermark
        current_directory = os.path.dirname(__file__)
        watermark_path = (
            os.path.split(current_directory)[0] + "/../../data/" + WATERMARK_FILE
        )
        watermark_image = Image.open(watermark_path)
        n = int(watermark_image.width * 0.75)
        newsize = (n, n)
        watermark_image = watermark_image.resize(newsize, Image.BICUBIC)
        # bottom right corner for 4k image
        x = 3072 - watermark_image.width
        y = 3072 - watermark_image.height
        base.paste(watermark_image, (x, y), watermark_image)
