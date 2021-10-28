from math import cos, sin, sqrt, ceil, atan2
from app.models.prep import SCALAR, MadeIngredientPrep
from typing import Dict, List, Tuple

from ..models.recipe import IngredientScope, ScopedIngredient, ScatterType
from app.core.config import OvenToppingParams, Settings

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
]

settings = Settings()


class Canvas:
    """the size of the natron canvas"""

    def __init__(self, oven_params: OvenToppingParams) -> None:
        self.oven_params = oven_params
        self.origin = (oven_params.scatter_origin_x, oven_params.scatter_origin_y)
        self.center = (oven_params.scatter_center_x, oven_params.scatter_center_y)
        self.end = (4096, 4096)
        self.hypotenuse = sqrt(self.end[0] ^ 2 + self.end[1] ^ 2)


class Scatter:
    def __init__(
        self, random_seed: int, nonce: Counter, oven_params: OvenToppingParams
    ) -> None:
        self.random_seed = random_seed
        self.nonce = nonce
        self.oven_params = oven_params

    def evaluate(
        self, topping_list: List[ScopedIngredient]
    ) -> List[MadeIngredientPrep]:
        """implement in your derived class"""
        ...

    def translate_to_canvas(self, point: Tuple[float, float]) -> Tuple[float, float]:
        """translate a raw point to a location on the canvas"""
        canvas = Canvas(self.oven_params)
        # position based on 1024 topping image size - if pixel dimensions are different, position will be off
        x = point[0] + self.oven_params.scatter_center_x
        y = point[1] + self.oven_params.scatter_center_y

        return (x, y)

    def prevent_overflow(
        self, instances: List[MadeIngredientPrep]
    ) -> List[MadeIngredientPrep]:
        """This will take an instance off the edgee and move it towrds center to prevent overhand"""
        canvas = Canvas(self.oven_params)

        # The circumference to use as a boundary - past this, reign it in
        inner_circle = self.oven_params.prevent_overflow_control_diameter
        inner_radius = inner_circle / 2

        translated_instances = []
        for instance in instances:
            x1 = canvas.center[0]
            y1 = canvas.center[1]
            x2 = instance.translation[0]
            y2 = instance.translation[1]
            # calculate the distance from the center
            dist_from_center = sqrt(
                (x2 - canvas.center[0]) ** 2 + (y2 - canvas.center[0]) ** 2
            )

            # take scale into account
            relative_size = instance.scale * 1024
            # approximate the fall off amount - won't be perfect due to image variation
            edge_distance = dist_from_center + (relative_size / 2)

            # if an instance is too far, reign it in
            if edge_distance > inner_radius:
                fall_off = edge_distance - inner_radius
                preferred_distance_from_center = inner_radius - fall_off
                angle = atan2((y2 - y1), (x2 - x1))
                tx = x1 + (preferred_distance_from_center * cos(angle))
                ty = y1 + (preferred_distance_from_center * sin(angle))

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
        random_location = self.randomize((0, 0))
        made = MadeIngredientPrep(
            translation=random_location,
            rotation=rotation,
            scale=scale,
            image_uri=ingredient.ingredient.image_uris["filename"],
        )

        translation = self.translate_to_canvas(made.translation)
        made.translation = translation
        instances.append(made)

        instances = self.prevent_overflow(instances)

        return instances

    def randomize(self, posiion: tuple) -> tuple:
        randx = select_value(
            self.random_seed,
            self.nonce,
            (
                -self.oven_params.hero_random_offset_x,
                self.oven_params.hero_random_offset_x,
            ),
        )
        randy = select_value(
            self.random_seed,
            self.nonce,
            (
                -self.oven_params.hero_random_offset_y,
                self.oven_params.hero_random_offset_y,
            ),
        )

        return (posiion[0] + randx, posiion[1] + randy)


class FiveSpot(Scatter):
    """Creates a pattern of five locations on the pie that can be randomized"""

    def evaluate(
        self, topping_list: List[ScopedIngredient]
    ) -> List[MadeIngredientPrep]:

        # The base locations we will use
        # defaults [(850, 850), (2222, 850), (2222, 2222), (850, 2222), (1536, 1536)]
        spot_1 = (self.oven_params.five_spot_x_1, self.oven_params.five_spot_y_1)
        spot_2 = (self.oven_params.five_spot_x_2, self.oven_params.five_spot_y_2)
        spot_3 = (self.oven_params.five_spot_x_3, self.oven_params.five_spot_y_3)
        spot_4 = (self.oven_params.five_spot_x_4, self.oven_params.five_spot_y_4)
        spot_5 = (self.oven_params.five_spot_x_5, self.oven_params.five_spot_y_5)

        locations = [spot_1, spot_2, spot_3, spot_4, spot_5]

        # rarndomize list for variety of placements
        locations = deterministic_shuffle(locations)

        instances: List[MadeIngredientPrep] = []

        for i in range(0, len(topping_list)):
            ingredient = topping_list[i]
            rotation = select_value(
                self.random_seed, self.nonce, ingredient.scope.rotation
            )
            scale = select_value(
                self.random_seed, self.nonce, ingredient.scope.particle_scale
            )

            # topping lists greater than five should not be passed to this scatter
            # if it happens, ignore the excess instances - for now
            if len(locations) > 0:
                next_spot = locations.pop()
                translation = self.randomize(next_spot)
                instances.append(
                    MadeIngredientPrep(
                        translation=translation,
                        rotation=rotation,
                        scale=scale,
                        image_uri=ingredient.ingredient.image_uris["filename"],
                    )
                )

        instances = self.prevent_overflow(instances)

        return instances

    # a randmizer that will add jitter to each position
    # when y values move more it looks better
    def randomize(self, posiion: tuple) -> tuple:
        randx = select_value(
            self.random_seed,
            self.nonce,
            (
                -self.oven_params.five_spot_x_random_offset,
                self.oven_params.five_spot_x_random_offset,
            ),
        )
        randy = select_value(
            self.random_seed,
            self.nonce,
            (
                -self.oven_params.five_spot_y_random_offset,
                self.oven_params.five_spot_y_random_offset,
            ),
        )

        return (posiion[0] + randx, posiion[1] + randy)


class SpokeCluster(Scatter):
    """Creates a pattern of instancies evenly distributed around a center with random radius"""

    def evaluate(
        self, topping_list: List[ScopedIngredient]
    ) -> List[MadeIngredientPrep]:

        instances: List[MadeIngredientPrep] = []

        degree_int = (2 * PI) / len(topping_list)

        inner_circle = self.oven_params.spokecluster_inner_circle
        # max radius is the inner circle minus half the scaled width - this preevents rings on the pie edge
        max_radius = (
            inner_circle - self.oven_params.spokecluster_max_radius_offset
        ) / 2

        for i in range(0, len(topping_list)):
            ingredient = topping_list[i]
            rotation = select_value(
                self.random_seed, self.nonce, ingredient.scope.rotation
            )
            scale = select_value(
                self.random_seed, self.nonce, ingredient.scope.particle_scale
            )

            # radius min should be relative to scale size - bigger instances have bigger min radius
            min_radius = self.oven_params.spokecluster_min_radius * scale

            radius = select_value(
                self.random_seed, self.nonce, (min_radius, max_radius)
            )

            spoke_angle = i * degree_int
            x = radius * cos(spoke_angle)
            y = radius * sin(spoke_angle)

            next_spot = (x, y)
            translation = self.translate_to_canvas(next_spot)

            instances.append(
                MadeIngredientPrep(
                    translation=translation,
                    rotation=rotation,
                    scale=scale,
                    image_uri=ingredient.ingredient.image_uris["filename"],
                )
            )

        instances = self.prevent_overflow(instances)

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

        instances = self.prevent_overflow(instances)

        return instances

    def translate_to_canvas(self, point: Tuple[float, float]) -> Tuple[float, float]:
        """translate a raw point to a location on the canvas"""
        canvas = Canvas(self.oven_params)
        # Grid is created with (0,0) at top left corner, so override the translation method
        x = point[0]
        y = point[1]

        return (x, y)

    # a randmizer that will add jitter to each position
    # when y values move more it looks better
    def randomize(self, posiion: tuple) -> tuple:
        randx = select_value(
            self.random_seed,
            self.nonce,
            (
                -self.oven_params.grid_random_offset_x,
                self.oven_params.grid_random_offset_x,
            ),
        )
        randy = select_value(
            self.random_seed,
            self.nonce,
            (
                -self.oven_params.grid_random_offset_y,
                self.oven_params.grid_random_offset_y,
            ),
        )

        return (posiion[0] + randx, posiion[1] + randy)

    def build_grid(self, item_count) -> list:
        positions: List[Tuple] = []
        x_values = []
        y_values = []
        origin = (self.oven_params.scatter_center_x, self.oven_params.scatter_center_y)

        # The circumference of the area we can place ingredients - just inside the crust
        inner_circle = self.oven_params.grid_inner_circle
        margin = 3072 - inner_circle

        # The number of sections in the grid based on how many instances we will have
        line_count = ceil(sqrt(item_count))
        # prevent divide by zero in case we try to build a grid with zero instances
        if line_count < 1:
            line_count = 1

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
                    unfiltered_positions.append(
                        (x - self.oven_params.grid_line_shift_offset, y)
                    )
                else:
                    unfiltered_positions.append(
                        (x + self.oven_params.grid_line_shift_offset, y)
                    )

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
        inner_circle = self.oven_params.treerinng_inner_circle

        # maximum scale for this ingredient
        instance_scale = topping_list[0].scope.particle_scale[1]

        # choose a random radius for the ring
        min_radius = self.oven_params.treering_min_radius
        # max radius is the inner circle minus half the scaled width - this preevents rings on the pie edge
        max_radius = (inner_circle - ((instance_scale * 1024) / 2)) / 2
        # make radius with respect to instance scale
        # larger instances should have larger radius to accmodate
        scaled_radius = instance_scale * (max_radius - min_radius)
        radius = min_radius + scaled_radius

        # if we have a small ingredient, let the ring change in diameter, there should be room
        variance = 1 - instance_scale
        if variance > self.oven_params.treering_variance_threshold:
            radius_variance = select_value(
                self.random_seed, self.nonce, (0, variance * max_radius)
            )
        else:
            radius_variance = 0

        radius = radius + radius_variance

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

        instances = self.prevent_overflow(instances)

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

        instances = self.prevent_overflow(instances)

        return instances

    def get_random_point(
        self, seed: int, nonce: Counter, position: int
    ) -> Tuple[SCALAR, SCALAR]:
        """Slightly different calculation for random point - limits the distribution to a radius"""

        rad = get_random_deterministic_float(seed, nonce, "random-point_rad", position)
        ang = get_random_deterministic_float(seed, nonce, "random-point_ang", position)

        random_radius = rad * (
            self.oven_params.random_inner_circle / 2.0
        )  # 3072 is the pixel width of pies - temp minus 20 to decrease bleed off pie
        random_angle = ang * TWO_PI
        x = random_radius * cos(random_angle)
        y = random_radius * sin(random_angle)

        return (x,y)