from math import cos, sin, sqrt, ceil
from app.models.prep import SCALAR, MadeIngredientPrep
from typing import Dict, List, Tuple

from ..models.recipe import IngredientScope, ScopedIngredient, ScatterType

from .random_num import (
    Counter,
    deterministic_shuffle,
    get_random_deterministic_uint256,
    get_random_deterministic_float,
    select_value,
)

PI = 3.14159
TWO_PI = 2 * PI

X = 0
Y = 1

__all__ = [
    "Canvas",
    "Scatter",
    "RandomScatter",
    "RandomScatter2",
]


class Canvas:
    """the size of the natron canvas"""

    origin = (0, 0)
    center = (3072 / 2, 3072 / 2)
    end = (4096, 4096)
    hypotenuse = sqrt(end[0] ^ 2 + end[1] ^ 2)


class Scatter:
    def __init__(self, random_seed: int, nonce: Counter) -> None:
        self.random_seed = random_seed
        self.nonce = nonce

    def evaluate(
        self, topping_list: List[ScopedIngredient]
    ) -> List[MadeIngredientPrep]:
        """implement in your derived class"""
        ...

    def translate_to_canvas(self, point: Tuple[float, float]) -> Tuple[float, float]:
        """translate a raw point to a location on the canvas"""
        canvas = Canvas()
        # position based on 1024 topping image size - if pixel dimensions are different, position will be off
        x = point[0] + (3072 / 2)
        y = point[1] + (3072 / 2)

        return (x, y)


class Hero(Scatter):
    """Creates a grid pattern to distrubute toppins evenly - Grid is alwyas the same size and can have empty
    spots if there are fewer toppings to disburse"""

    def evaluate(
        self, topping_list: List[ScopedIngredient]
    ) -> List[MadeIngredientPrep]:

        instances: List[MadeIngredientPrep] = []

        ingredient = topping_list[0]

        rotation = select_value(self.random_seed, self.nonce, ingredient.scope.rotation)
        scale = select_value(
            self.random_seed, self.nonce, ingredient.scope.particle_scale
        )
        made = MadeIngredientPrep(
            translation=(0, 0),
            rotation=rotation,
            scale=scale,
            image_uri=ingredient.ingredient.image_uris["filename"],
        )

        translation = self.translate_to_canvas(made.translation)
        made.translation = translation
        instances.append(made)

        return instances


class Grid(Scatter):
    """Creates a grid pattern to distrubute toppins evenly - Grid is alwyas the same size and can have empty
    spots if there are fewer toppings to disburse"""

    def evaluate(
        self, topping_list: List[ScopedIngredient]
    ) -> List[MadeIngredientPrep]:
        """implement in your derived class"""
        ...

        grid_positions = self.build_grid(len(topping_list))

        instances: List[MadeIngredientPrep] = []

        print(f"grid: {len(grid_positions)}  toppings: {len(topping_list)}")
        for i in range(0, len(grid_positions)):
            if i < len(topping_list):
                ingredient = topping_list[i]

                rotation = select_value(
                    self.random_seed, self.nonce, ingredient.scope.rotation
                )
                scale = select_value(
                    self.random_seed, self.nonce, ingredient.scope.particle_scale
                )

                translation = self.translate_to_canvas(grid_positions[i])
                instances.append(
                    MadeIngredientPrep(
                        translation=translation,
                        rotation=rotation,
                        scale=scale,
                        image_uri=ingredient.ingredient.image_uris["filename"],
                    )
                )

        return instances

    def translate_to_canvas(self, point: Tuple[float, float]) -> Tuple[float, float]:
        """translate a raw point to a location on the canvas"""
        canvas = Canvas()
        # Grid is created with (0,0) at top left corner, so override the translation method
        x = point[0]
        y = point[1]

        return (x, y)

    def randomize(self, posiion: tuple) -> tuple:
        randx = select_value(self.random_seed, self.nonce, (-75, 75))
        randy = select_value(self.random_seed, self.nonce, (-115, 115))

        return (posiion[0] + randx, posiion[1] + randy)

    def build_grid(self, item_count) -> list:
        positions = list()
        x_values = list()
        y_values = list()
        origin = (3072 / 2, 3072 / 2)

        inner_circle = 2800
        margin = 3072 - inner_circle

        line_count = ceil(sqrt(item_count))
        item_width = inner_circle / line_count

        for i in range(0, line_count):

            position = (i * item_width) + margin
            x_values.append(position)
            y_values.append(position)

        unfiltered_positions = list()
        for i in range(0, line_count):
            x = x_values[i]
            for n in range(0, line_count):
                y = y_values[n]
                if n % 2 == 0:
                    unfiltered_positions.append((x - 90, y))
                else:
                    unfiltered_positions.append((x + 90, y))

        # Is this gonna work with the detrministic random setup?
        unfiltered_positions = deterministic_shuffle(unfiltered_positions)

        for un_pos in unfiltered_positions:
            dist_from_center = sqrt(
                (un_pos[0] - origin[0]) ** 2 + (un_pos[1] - origin[1]) ** 2
            )

            if dist_from_center < (inner_circle / 2) and len(positions) < item_count:
                final_pos = self.randomize(un_pos)
                positions.append(final_pos)

        return positions


class TreeRing(Scatter):
    """Scatter that defines a circle centered in the frame, and place items evely around it"""

    def evaluate(
        self, topping_list: List[ScopedIngredient]
    ) -> List[MadeIngredientPrep]:

        instances: List[MadeIngredientPrep] = []

        min_radius = 250.0
        max_radius = (
            3072 / 2
        )  # might be a better way to calculat this, take into account the particle size
        radius = min_radius + (
            get_random_deterministic_float(self.random_seed, self.nonce)
            * (max_radius - min_radius)
        )

        for ingredient in topping_list:
            rotation = select_value(
                self.random_seed, self.nonce, ingredient.scope.rotation
            )
            scale = select_value(
                self.random_seed, self.nonce, ingredient.scope.particle_scale
            )
            index = topping_list.index(ingredient)
            translation = self.calculate_tree_position(radius, len(topping_list), index)
            translation = self.translate_to_canvas(translation)
            instances.append(
                MadeIngredientPrep(
                    translation=translation,
                    rotation=rotation,
                    scale=scale,
                    image_uri=ingredient.ingredient.image_uris["filename"],
                )
            )

        return instances

    def calculate_tree_position(self, radius, item_count, index) -> Tuple[float, float]:
        """Return a position on the circle based on the index count"""

        degree_int = (2 * PI) / item_count
        rotation = index * degree_int
        x = radius * cos(rotation)
        y = radius * sin(rotation)

        return (x, y)


class RandomScatter(Scatter):
    "randomly scatter by placing items on circles"

    def evaluate(
        self, topping_list: List[ScopedIngredient]
    ) -> List[MadeIngredientPrep]:

        instances: List[MadeIngredientPrep] = []

        for ingredient in topping_list:
            rotation = select_value(
                self.random_seed, self.nonce, ingredient.scope.rotation
            )
            scale = select_value(
                self.random_seed, self.nonce, ingredient.scope.particle_scale
            )

            index = topping_list.index(ingredient)
            translation = self.get_random_point(self.random_seed, self.nonce, index)
            translation = self.translate_to_canvas(translation)
            instances.append(
                MadeIngredientPrep(
                    translation=translation,
                    rotation=rotation,
                    scale=scale,
                    image_uri=ingredient.ingredient.image_uris["filename"],
                )
            )

        return instances

    def get_random_point(
        self, seed: int, nonce: Counter, position: int
    ) -> Tuple[SCALAR, SCALAR]:
        """Slightly different calculation for random point - limits the distribution to a radius"""

        rad = get_random_deterministic_float(seed, nonce, "random-point_rad", position)
        ang = get_random_deterministic_float(seed, nonce, "random-point_ang", position)

        random_radius = rad * (
            3052.0 / 2.0
        )  # 3072 is the pixel width of pies - temp minus 20 to decrease bleed off pie
        random_angle = ang * TWO_PI
        x = random_radius * cos(random_angle)
        y = random_radius * sin(random_angle)

        return (x, y)

    def random_point(
        self, seed: int, nonce: Counter, position: int
    ) -> Tuple[SCALAR, SCALAR]:
        """get a random point on a circle"""
        theta = TWO_PI * get_random_deterministic_float(
            seed, nonce, "random-point", position
        )
        print(f"theta: {theta}")
        # TODO: probably calculate max radius based on a rectangle instead of a square
        radius = select_value(seed, nonce, (Canvas.origin[X], Canvas.center[X]))
        print(f"radius: {radius}")
        r = sqrt(
            get_random_deterministic_float(seed, nonce, "random-point", int(theta))
        )
        print(f"r: {r}")
        x = Canvas.center[X] + r * radius * cos(theta)
        print(f"x: {x}")
        y = Canvas.center[Y] + r * radius * sin(theta)
        print(f"y: {y}")

        return (x, y)