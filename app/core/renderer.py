#!/usr/bin/env python

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional
import os
import subprocess
import json

from app.models.recipe import Classification
from app.models.prep import KitchenOrder, MadeIngredient
from app.models.pizza import HotPizza

DEFAULT_FRAME = 9
DEFAULT_EXECUTABLE_PATH = os.environ["NATRON_PATH"]
DEFAULT_PROJECT_PATH = os.environ["NATRON_PROJECT_PATH"]

current = os.path.dirname(os.path.realpath(__file__))


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


@dataclass
class Renderer:
    """render the kitchen order"""

    natron_path: str
    project_path: str
    frame: str

    rendered_files: Dict[str, str] = field(default_factory=lambda: {})

    order: Optional[KitchenOrder] = field(default=None)

    def cache_ingredient(self, ingredient: MadeIngredient) -> str:
        cache_dir = os.path.join(
            self.project_path,
            ".cache/",
        )
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

        file_path = os.path.join(cache_dir, f"{ingredient.ingredient.unique_id}.json")

        with open(file_path, "w") as json_file:
            json_file.write(ingredient.json())

        return file_path

    def render_pizza(self, order: KitchenOrder) -> None:
        """render the pizza out to the file systme using natron"""

        for (key, ingredient) in order.base_ingredients.items():
            result = self.render_ingredient(ingredient)
            if not result:
                print(f"error rendering {ingredient.ingredient.name}")
                break

        # TODO: more things like render the toppings, hook up the return values
        # and pass the rendering back to the caller

    def render_ingredient(self, ingredient: MadeIngredient) -> bool:
        """render the ingredient"""
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
            pass
        if ingredient.ingredient.classification == Classification.topping:
            pass
        if ingredient.ingredient.classification == Classification.special:
            pass

        return True


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
        default=DEFAULT_FRAME,
        type=int,
        help="The frame to render",
    )

    parser.add_argument(
        "-n",
        "--natron-path",
        metavar="<natron>",
        default=DEFAULT_EXECUTABLE_PATH,
        type=str,
        help="The folder where NatronRenderer exists",
    )

    parser.add_argument(
        "-p",
        "--project-path",
        metavar="<project>",
        default=DEFAULT_PROJECT_PATH,
        type=str,
        help="The folder where project files exist",
    )

    parser.add_argument(
        "-r",
        "--recipe-path",
        metavar="<project>",
        default=DEFAULT_PROJECT_PATH,
        type=str,
        help="The absolute path to a recipe file. ignored if kitchen order is specified",
    )

    parser.add_argument(
        "-k",
        "--kitchen-order-path",
        metavar="<project>",
        default=DEFAULT_PROJECT_PATH,
        type=str,
        help="The absolute path to a kitchen order",
    )

    args = parser.parse_args()

    if args.kitchen_order_path is not None:
        with open(args.kitchen_order_path) as json_file:
            kitchen_order = KitchenOrder(**json.load(json_file))
            Renderer(args.natron_path, args.project_path, args.frame).render_pizza(
                kitchen_order
            )

    # TODO: load the recipe, parse it, and render
