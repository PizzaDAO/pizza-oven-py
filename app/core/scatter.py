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

    def prevent_overflow(
        self, instances: List[MadeIngredientPrep]
    ) -> List[MadeIngredientPrep]:
        """This will take an instance off the edgee and move it towrds center to prevent overhand"""
        canvas = Canvas()

        # The circumference to use as a boundary - past this, reign it in
        inner_circle = 3000
        inner_radius = inner_circle / 2

        translated_instances = []
        for instance in instances:
            # calculate the distance from the center
            x = instance.translation[0]
            y = instance.translation[1]
            dist_from_center = sqrt(
                (x - canvas.center[0]) ** 2 + (y - canvas.center[0]) ** 2
            )

            # take scale into account
            relative_size = instance.scale * 1024
            # approximate the fall off amount - won't be perfect due to image variation
            edge_distance = dist_from_center + (relative_size / 2)
            print(edge_distance)
            # if an instance is too far, reign it in
            if edge_distance > inner_radius:
                fall_off = edge_distance - inner_radius
                tx = instance.translation[0] - fall_off
                ty = instance.translation[1] - fall_off
                instance.translation = (tx, ty)

            translated_instances.append(instance)

        return translated_instances


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

        # instances = self.prevent_overflow(instances)

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
        # the collection enumeration method isnt working as expected, translations are not being assigned
        # switching to index enumeration and checking that the index is not out of bounds
        # we use grid_positions here because we don't want to force more instances into positions available
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

        # instances = self.prevent_overflow(instances)

        return instances

    def translate_to_canvas(self, point: Tuple[float, float]) -> Tuple[float, float]:
        """translate a raw point to a location on the canvas"""
        canvas = Canvas()
        # Grid is created with (0,0) at top left corner, so override the translation method
        x = point[0]
        y = point[1]

        return (x, y)

    # a randmizer that will add jitter to each position
    # when y values move more it looks better
    def randomize(self, posiion: tuple) -> tuple:
        randx = select_value(self.random_seed, self.nonce, (-75, 75))
        randy = select_value(self.random_seed, self.nonce, (-115, 115))

        return (posiion[0] + randx, posiion[1] + randy)

    def build_grid(self, item_count) -> list:
        positions = list()
        x_values = list()
        y_values = list()
        origin = (3072 / 2, 3072 / 2)

        # The circumference of the area we can place ingredients - just inside the crust
        inner_circle = 2800
        margin = 3072 - inner_circle

        # The number of sections in the grid based on how many instances we will have
        line_count = ceil(sqrt(item_count))
        # The width of each cell in the grid
        item_width = inner_circle / line_count

        # Assign all the basic positions of the grid
        # these are just unit values
        for i in range(0, line_count):

            position = (i * item_width) + margin
            x_values.append(position)
            y_values.append(position)

        # Actually make the grid with a nested loop
        unfiltered_positions = list()
        for i in range(0, line_count):
            x = x_values[i]
            for n in range(0, line_count):
                y = y_values[n]
                # Adding some shifting to the lines to creaete more a random feel
                if n % 2 == 0:
                    unfiltered_positions.append((x - 90, y))
                else:
                    unfiltered_positions.append((x + 90, y))

        # Add some shufflee to the instances so the grid doesn't populate in a predictable manner
        unfiltered_positions = deterministic_shuffle(unfiltered_positions)

        # Filtre out instancees that fall off the pie
        # WARNING - if it's imperitive to have the number of instnaces selected appear on the pie
        # this will need to be revised - could have fewer items than selected
        for un_pos in unfiltered_positions:
            # calculate the distance from the center
            dist_from_center = sqrt(
                (un_pos[0] - origin[0]) ** 2 + (un_pos[1] - origin[1]) ** 2
            )
            # if an instance is too far, don's add it to the list
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

        # the circumference of the circle we will place instances - just inside the crust
        inner_circle = 2800

        # choose a random radius for the ring
        min_radius = 250.0
        max_radius = (
            inner_circle / 2
        )  # might be a better way to calculat this, take into account the particle size
        radius = min_radius + (
            get_random_deterministic_float(self.random_seed, self.nonce)
            * (max_radius - min_radius)
        )

        for i in range(0, len(topping_list)):
            ingredient = topping_list[i]
            rotation = select_value(
                self.random_seed, self.nonce, ingredient.scope.rotation
            )
            scale = select_value(
                self.random_seed, self.nonce, ingredient.scope.particle_scale
            )

            translation = self.calculate_tree_position(radius, len(topping_list), i)
            translation = self.translate_to_canvas(translation)

            instances.append(
                MadeIngredientPrep(
                    translation=translation,
                    rotation=rotation,
                    scale=scale,
                    image_uri=ingredient.ingredient.image_uris["filename"],
                )
            )

        # instances = self.prevent_overflow(instances)

        return instances

    def calculate_tree_position(self, radius, item_count, index) -> Tuple[float, float]:
        """Return a position on the circle based on the index count"""

        # evenly distibute toppings around the ring
        # unit values that will later be converted to natron coordinates
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

        # instances = self.prevent_overflow(instances)

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