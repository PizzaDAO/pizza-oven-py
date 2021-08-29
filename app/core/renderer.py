#!/usr/bin/env python

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import os
import subprocess
import json

from app.models.recipe import Classification
from app.models.prep import KitchenOrder, MadeIngredient
from app.models.pizza import HotPizza
from app.core.config import Settings

from PIL import Image

current = os.path.dirname(os.path.realpath(__file__))
settings = Settings()


class BoxRenderer:
    """Render Boxes"""

    def __init__(self):
        pass

    def render(self, executable_path, project_path, data_path, frame):
        # TODO: things like capture stdout or errors
        os.environ["BOX_DATA_PATH"] = data_path
        subprocess.check_call(
            [
                f"{executable_path}/NatronRenderer",
                "-l",
                f"{current}/natron/box.py",
                f"{project_path}/box.ntp",
                f"{frame}",
            ]
        )


class PaperRenderer:
    """Render Paper"""

    def __init__(self):
        pass

    def render(self, executable_path, project_path, data_path, frame):
        os.environ["PAPER_DATA_PATH"] = data_path
        subprocess.check_call(
            [
                f"{executable_path}/NatronRenderer",
                "-l",
                f"{current}/natron/paper.py",
                f"{project_path}/waxpaper.ntp",
                f"{frame}",
            ]
        )


class CrustRenderer:
    """Render Crust"""

    def __init__(self):
        pass

    def render(self, executable_path, project_path, data_path, frame):
        os.environ["CRUST_DATA_PATH"] = data_path
        subprocess.check_call(
            [
                f"{executable_path}/NatronRenderer",
                "-l",
                f"{current}/natron/crust.py",
                f"{project_path}/crust.ntp",
                f"{frame}",
            ]
        )


class SauceRenderer:
    """Render sauces"""

    def __init__(self):
        pass

    def render(self, executable_path, project_path, data_path, frame):
        os.environ["SAUCE_DATA_PATH"] = data_path
        subprocess.check_call(
            [
                f"{executable_path}/NatronRenderer",
                "-l",
                f"{current}/natron/sauce.py",
                f"{project_path}/sauce.ntp",
                f"{frame}",
            ]
        )


class CheeseRenderer:
    """Render cheeses"""

    def __init__(self):
        pass

    def render(self, executable_path, project_path, data_path, frame):
        os.environ["CHEESE_DATA_PATH"] = data_path
        subprocess.check_call(
            [
                f"{executable_path}/NatronRenderer",
                "-l",
                f"{current}/natron/cheese.py",
                f"{project_path}/cheese.ntp",
                f"{frame}",
            ]
        )


class ToppingRenderer:
    """Render toppings"""

    def __init__(self):
        pass

    def render(self, executable_path, project_path, data_path, frame):
        os.environ["TOPPING_DATA_PATH"] = data_path
        subprocess.check_call(
            [
                f"{executable_path}/NatronRenderer",
                "-l",
                f"{current}/natron/topping.py",
                f"{project_path}/topping.ntp",
                f"{frame}",
            ]
        )


class ExtraRenderer:
    """Render extras"""

    def __init__(self):
        pass

    def render(self, executable_path, project_path, data_path, frame):
        os.environ["EXTRA_DATA_PATH"] = data_path
        subprocess.check_call(
            [
                f"{executable_path}/NatronRenderer",
                "-l",
                f"{current}/natron/extra.py",
                f"{project_path}/extra.ntp",
                f"{frame}",
            ]
        )


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

        file_path = os.path.join(cache_dir, f"{ingredient.ingredient.unique_id}.json")

        # cache out the ingredient so it can be picked up by natron
        with open(file_path, "w") as ingredient_file:
            ingredient_file.write(ingredient.json())

        return file_path

    def flatten_image(self, layers: List[str]) -> str:
        """flatten the image layers into a single image and return its filename"""

        print("flattening")
        print(layers)

        output_dir = os.path.join(
            self.project_path,
            "../output/",
        )
        if not os.path.exists(output_dir):
            print("output directory not found")
            return ""

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

        base.save(os.path.join(output_dir, "rarepizza-00000.png"))

        return "rarepizza-00000.png"

    def render_pizza(self, job_id: str, order: KitchenOrder) -> HotPizza:
        """render the pizza out to the file systme using natron"""
        rendered_layer_files: List[str] = []

        base_layer_index = 0

        # iterate through each the base ingredients and render
        for (_, ingredient) in order.base_ingredients.items():
            result = self.render_ingredient(base_layer_index, ingredient)
            rendered_layer_files.append(result)
            base_layer_index += 1

        topping_layer_index = 0

        # # iterate through each of the layers and render
        for (_, ingredient) in order.layers.items():
            result = self.render_ingredient(topping_layer_index, ingredient)
            rendered_layer_files.append(result)
            topping_layer_index += 1

        #       for (key, ingredient) in order.special.items():
        #           result = self.render_ingredient(ingredient)
        #           if not result:
        #               print(f"error rendering special {ingredient.ingredient.name}")
        #               break

        # combiner all the images together
        output_file = self.flatten_image(rendered_layer_files)

        output_dir = os.path.join(
            self.project_path,
            "../output/",
        )

        # TODO: more things like hook up the return values
        # and pass the rendering back to the caller
        # note the IPFS id probably isnt populated in this function but instead by the caller
        return HotPizza(
            unique_id=job_id,
            order_id=order.unique_id,
            recipe_id=order.recipe_id,
            assets={
                "BLOB": "the binary representation of the pizza",
                "IMAGE_PATH": os.path.join(output_dir, output_file),
                "IPFS_HASH": "filled_in_by_calling_set_metadata",
            },
        )

    def render_ingredient(self, layer_index: int, ingredient: MadeIngredient) -> str:
        """render the ingredient"""
        data_path = self.cache_ingredient(ingredient)

        category = "base"
        if ingredient.ingredient.classification == Classification.box:
            category = "box"
            BoxRenderer().render(
                self.natron_path, self.project_path, data_path, self.frame
            )

        if ingredient.ingredient.classification == Classification.paper:
            category = "paper"
            PaperRenderer().render(
                self.natron_path, self.project_path, data_path, self.frame
            )

        if ingredient.ingredient.classification == Classification.crust:
            category = "crust"
            CrustRenderer().render(
                self.natron_path, self.project_path, data_path, self.frame
            )

        if ingredient.ingredient.classification == Classification.sauce:
            category = "topping"
            SauceRenderer().render(
                self.natron_path, self.project_path, data_path, self.frame
            )

        if ingredient.ingredient.classification == Classification.cheese:
            category = "topping"
            CheeseRenderer().render(
                self.natron_path, self.project_path, data_path, self.frame
            )
        if ingredient.ingredient.classification == Classification.topping:
            category = "topping"
            ToppingRenderer().render(
                self.natron_path, self.project_path, data_path, self.frame
            )
        if ingredient.ingredient.classification == Classification.extras:
            category = "topping"
            ExtraRenderer().render(
                self.natron_path, self.project_path, data_path, self.frame
            )

        output_filename = f"rarepizza-{self.frame}-{category}-{layer_index}.png"
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
