#!/usr/bin/env python

import random
import os

from app.core.recipe_box import get_pizza_recipe
from app.core.prep_line import reduce
from app.core.test.simple_render import SimpleRenderer

if __name__ == "__main__":
    """invoke the rendering steps via the command line"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Render components using Splat method",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-r",
        "--recipe_id",
        metavar="<recipe_id>",
        default=0,
        type=int,
        help="The recipe to generate",
    )

    parser.add_argument(
        "-c",
        "--count",
        metavar="<count>",
        default=1,
        type=int,
        help="The number of pies to generate",
    )

    args = parser.parse_args()

    print(f"We are going to make {args.count} of recipe {args.recipe_id}")

    project_path: str = ""

    output_dir = os.path.join(
        project_path,
        "output/recipe_gen/",
    )
    if not os.path.exists(output_dir):
        os.makedirs("output/recipe_gen/")

    # Load the recipe
    recipe = get_pizza_recipe(args.recipe_id)

    for i in range(0, args.count):

        kitchen_order = reduce(recipe, i)

        img = SimpleRenderer().render_pizza(kitchen_order)

        # Save Image
        unique_filename = str(i).zfill(4) + ".png"
        img.save(os.path.join(output_dir, unique_filename))

        # Save KO JSON
        # save the kitchen order out to the file system
        kitchen_order_file_path = os.path.join(output_dir, f"{str(i).zfill(4)}.json")
        with open(kitchen_order_file_path, "w") as kitchen_order_file:
            kitchen_order_file.write(kitchen_order.json())

    # with open(args.kitchen_order_path) as json_file:
    #     kitchen_order = KitchenOrder(**json.load(json_file))
    #     Renderer(
    #         args.frame, "abc-1234", args.natron_path, args.project_path
    #     ).render_pizza(kitchen_order)