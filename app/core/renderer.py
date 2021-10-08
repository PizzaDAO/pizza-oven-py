#!/usr/bin/env python

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from math import ceil
import os
import subprocess
import json

from app.models.recipe import Classification, classification_as_string
from app.models.prep import KitchenOrder, MadeIngredient, ShuffledLayer
from app.models.pizza import HotPizza
from app.core.config import Settings

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

current = os.path.dirname(os.path.realpath(__file__))
settings = Settings()

DEV_MODE = True
DATA_FONT_SIZE = 64
WATERMARK_FILE = "pizza_watermark.png"


class BoxRenderer:
    """Render Boxes"""

    def __init__(self):
        pass

    def render(self, executable_path, project_path, data_path, frame):
        print(f"BoxRenderer:render {data_path}")
        os.environ["BOX_DATA_PATH"] = data_path
        try:
            result = subprocess.run(
                [
                    f"{executable_path}/NatronRenderer",
                    "-l",
                    f"{current}/natron/box.py",
                    f"{project_path}/box.ntp",
                    f"{frame}",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            print(f"stderr: {result.stderr}")
            print(f"stdout: {result.stdout}")
        except subprocess.CalledProcessError as e:
            print(f"BoxRenderer exited with error code: {e.returncode}")
            print(e)


class PaperRenderer:
    """Render Paper"""

    def __init__(self):
        pass

    def render(self, executable_path, project_path, data_path, frame):
        print(f"PaperRenderer:render {data_path}")
        os.environ["PAPER_DATA_PATH"] = data_path
        try:
            result = subprocess.run(
                [
                    f"{executable_path}/NatronRenderer",
                    "-l",
                    f"{current}/natron/paper.py",
                    f"{project_path}/waxpaper.ntp",
                    f"{frame}",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            print(f"stderr: {result.stderr}")
            print(f"stdout: {result.stdout}")
        except subprocess.CalledProcessError as e:
            print(f"PaperRenderer exited with error code: {e.returncode}")
            print(e)


class CrustRenderer:
    """Render Crust"""

    def __init__(self):
        pass

    def render(self, executable_path, project_path, data_path, frame):
        print(f"CrustRenderer:render {data_path}")
        os.environ["CRUST_DATA_PATH"] = data_path
        try:
            result = subprocess.run(
                [
                    f"{executable_path}/NatronRenderer",
                    "-l",
                    f"{current}/natron/crust.py",
                    f"{project_path}/crust.ntp",
                    f"{frame}",
                ],
                check=True,
                capture_output=True,
                text=True
                # stdout=subprocess.PIPE,
                # stderr=subprocess.STDOUT,
            )
            print(f"stderr: {result.stderr}")
            print(f"stdout: {result.stdout}")
        except subprocess.CalledProcessError as e:
            print(f"CrustRenderer exited with error code: {e.returncode}")
            print(e)


class SauceRenderer:
    """Render sauces"""

    def __init__(self):
        pass

    def render(self, executable_path, project_path, data_path, frame):
        print(f"SauceRenderer:render {data_path}")
        os.environ["SAUCE_DATA_PATH"] = data_path
        try:
            result = subprocess.run(
                [
                    f"{executable_path}/NatronRenderer",
                    "-l",
                    f"{current}/natron/sauce.py",
                    f"{project_path}/sauce.ntp",
                    f"{frame}",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            print(f"stderr: {result.stderr}")
            print(f"stdout: {result.stdout}")
        except subprocess.CalledProcessError as e:
            print(f"SauceRenderer exited with error code: {e.returncode}")
            print(e)


class CheeseRenderer:
    """Render cheeses"""

    def __init__(self):
        pass

    def render(self, executable_path, project_path, data_path, frame):
        print(f"CheeseRenderer:render {data_path}")
        os.environ["CHEESE_DATA_PATH"] = data_path
        try:
            result = subprocess.run(
                [
                    f"{executable_path}/NatronRenderer",
                    "-l",
                    f"{current}/natron/cheese.py",
                    f"{project_path}/cheese.ntp",
                    f"{frame}",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            print(f"stderr: {result.stderr}")
            print(f"stdout: {result.stdout}")
        except subprocess.CalledProcessError as e:
            print(f"CheeseRenderer exited with error code: {e.returncode}")
            print(e)


class ToppingRenderer:
    """Render toppings"""

    def __init__(self):
        pass

    def render(self, executable_path, project_path, data_path, frame):
        print(f"ToppingRenderer:render {data_path}")
        os.environ["TOPPING_DATA_PATH"] = data_path

        try:
            result = subprocess.run(
                [
                    f"{executable_path}/NatronRenderer",
                    "-l",
                    f"{current}/natron/topping.py",
                    f"{project_path}/topping.ntp",
                    f"{frame}",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            print(f"stderr: {result.stderr}")
            print(f"stdout: {result.stdout}")
        except subprocess.CalledProcessError as e:
            print(f"ToppingRenderer exited with error code: {e.returncode}")
            print(e)


class ExtraRenderer:
    """Render extras"""

    def __init__(self):
        pass

    def render(self, executable_path, project_path, data_path, frame):
        print(f"ExtraRenderer:render {data_path}")
        os.environ["EXTRA_DATA_PATH"] = data_path
        try:
            result = subprocess.run(
                [
                    f"{executable_path}/NatronRenderer",
                    "-l",
                    f"{current}/natron/extra.py",
                    f"{project_path}/extra.ntp",
                    f"{frame}",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            print(f"stderr: {result.stderr}")
            print(f"stdout: {result.stdout}")
        except subprocess.CalledProcessError as e:
            print(f"ExtraRenderer exited with error code: {e.returncode}")
            print(e)


@dataclass
class Renderer:
    """render the kitchen order"""

    natron_path: str = field(default=settings.DEFAULT_NATRON_EXECUTABLE_PATH)
    project_path: str = field(default=settings.DEFAULT_NATRON_PROJECT_PATH)
    frame: str = field(default="00000")

    rendered_files: Dict[str, str] = field(default_factory=lambda: {})

    order: Optional[KitchenOrder] = field(default=None)

    def cache_ingredient(self, ingredient: MadeIngredient) -> str:
        """Cache the ingredient data so that natron can pick it up."""
        # create a .cache directory
        cache_dir = os.path.join(
            self.project_path,
            "../.cache/",
        )
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

        file_path = os.path.join(
            cache_dir, f"ingredient-{ingredient.ingredient.unique_id}.json"
        )

        # cache out the ingredient so it can be picked up by natron
        with open(file_path, "w") as ingredient_file:
            ingredient_file.write(ingredient.json())

        return file_path

    def cache_layer(self, layer: ShuffledLayer) -> str:
        """Cache the ingredient data so that natron can pick it up."""
        # create a .cache directory
        cache_dir = os.path.join(
            self.project_path,
            "../.cache/",
        )
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

        file_path = os.path.join(
            cache_dir, f"layer-{layer.token_id}_{layer.index}.json"
        )

        # cache out the ingredient so it can be picked up by natron
        with open(file_path, "w") as layer_file:
            layer_file.write(layer.json())

        return file_path

    def draw_watermark(self, base: Image, order: KitchenOrder):
        """draw a watermark on the pizza"""
        print("draw_watermark")
        draw = ImageDraw.Draw(base)
        font_path = os.path.join(self.project_path, "../fonts/Roboto-Medium.ttf")
        print(font_path)
        font = ImageFont.truetype(font_path, DATA_FONT_SIZE)
        base_ingredients = ""
        for ingredient in order.base_ingredients.values():
            i = ingredient.ingredient
            base_ingredients += i.unique_id + " " + i.name + " " + i.category + "\n"
        layer_ingredients = ""
        for ingredient in order.layers.values():
            i = ingredient.ingredient
            layer_ingredients += i.unique_id + " " + i.name + " - " + i.category + "\n"
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
        )
        draw.text((10, 10), pizza_data, fill="white", font=font, align="left")

        # add watermark
        watermark_path = os.path.join(self.project_path, "../data/" + WATERMARK_FILE)
        watermark_image = Image.open(watermark_path)
        # bottom right corner for 4k image
        x = 4096 - watermark_image.width
        y = 4096 - watermark_image.height
        base.paste(watermark_image, (x, y), watermark_image)

    def flatten_image(self, layers: List[str], order: KitchenOrder) -> str:
        """flatten the image layers into a single image and return its filename"""

        print("flatten_image")
        print(layers)

        output_dir = os.path.join(
            self.project_path,
            "../output/",
        )
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        images: List[Image.Image] = []
        for layer in layers:
            print(f"opening: {layer}")
            file = os.path.join(output_dir, layer)

            # if we can't find a file, just skip it.
            # can lead to incomplete pizzas
            if not os.path.exists(file):
                print(f"output file not found: {file}")
                continue

            image = Image.open(file)
            images.append(image)

        base = images[0]
        for image in images:
            base.paste(image, (0, 0), image)

        # TODO: make env variable to toggle this on/off
        if DEV_MODE:
            self.draw_watermark(base, order)

        # Give the final output a unique filename: ORDER-ID_PIZZA-TYPE-NAME_RANDOM-SEED.png
        unique_filename = (
            str(order.token_id)
            + "_"
            + order.name
            + "_"
            + str(order.random_seed + ".png")
        )

        base.save(os.path.join(output_dir, unique_filename))

        return unique_filename

    def render_pizza(self, job_id: str, order: KitchenOrder) -> HotPizza:
        """render the pizza out to the file systme using natron"""
        print("render_pizza")
        rendered_layer_files: List[str] = []

        base_layer_index = 0

        # iterate through each the base ingredients and render
        for (_, ingredient) in order.base_ingredients.items():
            result = self.render_ingredient(base_layer_index, ingredient)
            rendered_layer_files.append(result)
            base_layer_index += 1

        topping_layer_index = 0

        # Make sure there is an output folder to write to
        output_dir = os.path.join(
            self.project_path,
            "../output/",
        )
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        #
        # SINGLE IGREDIENT TOPPING LAYERS
        #
        # # iterate through each of the layers and render
        # for (_, ingredient) in order.layers.items():
        #     print(
        #         "WILL RENDER THIS MANY "
        #         + ingredient.ingredient.name
        #         + ": "
        #         + str(ingredient.count)
        #     )
        #     result = self.render_ingredient(topping_layer_index, ingredient)
        #     rendered_layer_files.append(result)
        #     topping_layer_index += 1

        # Iterate through shuffled instances to create layers of 30 items
        #
        # BATCHING
        #
        max_instances = 30
        instance_count = ceil(len(order.instances))
        layer_count = ceil(instance_count / max_instances)

        for index in range(layer_count):
            if instance_count - (index * max_instances) < max_instances:
                batch_count = instance_count % max_instances
            else:
                batch_count = max_instances

            sliceObj = slice(0, batch_count)
            batch = order.instances[sliceObj]

            # Create a ShuffledLayer
            shuffle_layer = ShuffledLayer(
                token_id=order.token_id,
                index=index,
                count=batch_count,
                instances=batch,
            )
            result = self.render_instances(topping_layer_index, shuffle_layer)
            rendered_layer_files.append(result)
            topping_layer_index += 1

        # render any special ingredients
        #       for (key, ingredient) in order.special.items():
        #           result = self.render_ingredient(ingredient)
        #           if not result:
        #               print(f"error rendering special {ingredient.ingredient.name}")
        #               break

        # combiner all the images together
        output_file = self.flatten_image(rendered_layer_files, order)

        output_dir = os.path.join(
            self.project_path,
            "../output/",
        )

        # TODO: more things like hook up the return values
        # and pass the rendering back to the caller
        # note the IPFS id probably isnt populated in this function but instead by the caller
        return HotPizza(
            unique_id=job_id,
            order_id=order.token_id,
            recipe_id=order.recipe_id,
            assets={
                "BLOB": "the binary representation of the pizza",
                "IMAGE_PATH": os.path.join(output_dir, output_file),
                "IPFS_HASH": "filled_in_by_calling_set_metadata",
            },
        )

    def render_instances(self, layer_index: int, layer: ShuffledLayer) -> str:
        # Build the output filename and save it allong with the cached Ingredient
        print("render_shuffled_layer")
        category = classification_as_string(
            Classification.topping
        )  # TEMP default to "topping"
        output_filename = f"{self.frame}-instances-{category}-{layer_index}.png"
        layer.output_mask = output_filename

        data_path = self.cache_layer(layer)

        # Using topping renderer as default here - should be layer specific?
        # Possibly requires input from Natron dev
        ToppingRenderer().render(
            self.natron_path, self.project_path, data_path, self.frame
        )

        return output_filename

    def render_ingredient(self, layer_index: int, ingredient: MadeIngredient) -> str:
        """render the ingredient"""

        print(f"render_ingredient: {ingredient.ingredient.classification.name}")
        # Build the output filename and save it allong with the cached Ingredient
        category = classification_as_string(ingredient.ingredient.classification)
        output_filename = (
            f"{self.frame}-{category}-{ingredient.ingredient.name}-{layer_index}.png"
        )
        ingredient.ingredient.image_uris["output_mask"] = output_filename

        data_path = self.cache_ingredient(ingredient)

        if ingredient.ingredient.classification == Classification.box:
            BoxRenderer().render(
                self.natron_path, self.project_path, data_path, self.frame
            )

        if ingredient.ingredient.classification == Classification.paper:
            PaperRenderer().render(
                self.natron_path, self.project_path, data_path, self.frame
            )

        if ingredient.ingredient.classification == Classification.crust:
            CrustRenderer().render(
                self.natron_path, self.project_path, data_path, self.frame
            )

        if ingredient.ingredient.classification == Classification.sauce:
            SauceRenderer().render(
                self.natron_path, self.project_path, data_path, self.frame
            )

        if ingredient.ingredient.classification == Classification.cheese:
            CheeseRenderer().render(
                self.natron_path, self.project_path, data_path, self.frame
            )
        if ingredient.ingredient.classification == Classification.topping:
            ToppingRenderer().render(
                self.natron_path, self.project_path, data_path, self.frame
            )
        if ingredient.ingredient.classification == Classification.extras:
            ExtraRenderer().render(
                self.natron_path, self.project_path, data_path, self.frame
            )

        return output_filename


if __name__ == "__main__":
    """invoke the rendering steps via the command line"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Render components using Natron",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-f",
        "--frame",
        metavar="<fame>",
        default=settings.DEFAULT_NATRON_FRAME,
        type=int,
        help="The frame to render",
    )

    parser.add_argument(
        "-n",
        "--natron-path",
        metavar="<natron>",
        default=settings.DEFAULT_NATRON_EXECUTABLE_PATH,
        type=str,
        help="The folder where NatronRenderer exists",
    )

    parser.add_argument(
        "-p",
        "--project-path",
        metavar="<project>",
        default=settings.DEFAULT_NATRON_PROJECT_PATH,
        type=str,
        help="The folder where project files exist",
    )

    parser.add_argument(
        "-r",
        "--recipe-path",
        metavar="<project>",
        type=str,
        help="The absolute path to a recipe file. ignored if kitchen order is specified",
    )

    parser.add_argument(
        "-k",
        "--kitchen-order-path",
        metavar="<project>",
        type=str,
        help="The absolute path to a kitchen order",
    )

    args = parser.parse_args()

    # TODO:
    # if args.recipe_path is not None:
    #     with open(args.recipe_path) as json_file:
    #         recipe = Recipe(**json.load(json_file))
    #         kitchen_order = prep_line.reduce(recipe)
    #         Renderer(args.natron_path, args.project_path, args.frame).render_pizza(
    #             kitchen_order
    #         )

    if args.kitchen_order_path is not None:
        with open(args.kitchen_order_path) as json_file:
            kitchen_order = KitchenOrder(**json.load(json_file))
            Renderer(args.natron_path, args.project_path, args.frame).render_pizza(
                "some-job-id", kitchen_order
            )

    # TODO: load the recipe, parse it, and render
