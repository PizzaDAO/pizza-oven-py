from math import cos, sin, sqrt
from app.models.prep import SCALAR, MadeIngredientPrep
from typing import Dict, List, Tuple

from ..models.recipe import IngredientScope, ScatterType

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


class Canvas:
    """the size of the natron canvas"""

    origin = (0, 0)
    center = (2048, 2048)
    end = (4096, 4096)
    hypotenuse = sqrt(end[0] ^ 2 + end[1] ^ 2)


class Scatter:
    def __init__(self, random_seed: int, nonce: Counter) -> None:
        self.random_seed = random_seed
        self.nonce = nonce

    def evaluate(self, scope: IngredientScope) -> List[MadeIngredientPrep]:
        """implement in your derived class"""
        ...

    def translate_to_canvas(self,point:Tuple[float,float]) -> Tuple[float,float]:
        """translate a raw point to a location on the canvas"""
        canvas = Canvas()
        # position based on 1024 topping image size - if pixel dimensions are different, position will be off
        x = point[0] + canvas.center[0] - (1024/2)
        y = point[1] + canvas.center[1] - (1024/2)

        return(x,y)

class Grid(Scatter):
    """Creates a grid pattern to distrubute toppins evenly - Grid is alwyas the same size and can have empty
    spots if there are fewer toppings to disburse"""

    def evaluate(self, scope: IngredientScope) -> List[MadeIngredientPrep]:

        instance_selection = select_value(
            self.random_seed, self.nonce, scope.emission_count
        )

        instance_count = round(instance_selection)

        grid_positions = self.build_grid(instance_count)
        
        instances: List[MadeIngredientPrep] = []

        for i in range(0,len(grid_positions)):
            rotation = select_value(self.random_seed, self.nonce, scope.rotation)
            scale = select_value(self.random_seed, self.nonce, scope.particle_scale)
            translation = self.translate_to_canvas(grid_positions[i])
            instances.append(
                MadeIngredientPrep(
                    translation=translation, rotation=rotation, scale=scale
                )
            )

        return instances

    def translate_to_canvas(self,point:Tuple[float,float]) -> Tuple[float,float]:
        """translate a raw point to a location on the canvas"""
        canvas = Canvas()
        # Grid is created with (0,0) at top left corner, so override the translation method
        x = point[0]
        y = point[1]

        return(x,y)

    def build_grid(self, item_count) -> list:

        line_count = round(sqrt(item_count)) + 1
        item_width = 3072 / line_count #3072 is the crust layer size - grid should not extend past this

        unfiltered_positions = list()
        for i in range(0, line_count):
            x = (i * item_width)
            for n in range(0, line_count):
                y = (n * item_width)
                unfiltered_positions.append((x,y))
        
        # Is this gonna work with the detrministic random setup?
        # We perform a shuffle here to spread out items over the grid when there are less items than grid spots
        unfiltered_positions = deterministic_shuffle(unfiltered_positions)

        positions:List[Tuple[float,float]] = list()
        center = Canvas().center[X]
        # Now filter the list to remove any toppings outside the crust layer circle
        # Large toppings may extend past crust - This does not take into account the topping size...
        for p in unfiltered_positions:
            dist_from_center = sqrt( (p[0] - center)**2 + (p[1] - center)**2 )
            
            if( dist_from_center < (3072/2) and len(positions) < len(unfiltered_positions)):
                positions.append(p)

        return positions


class TreeRing(Scatter):
    """Scatter that defines a circle centered in the frame, and place items evely around it"""

    def evaluate(self, scope: IngredientScope) -> List[MadeIngredientPrep]:

        instance_selection = select_value(
            self.random_seed, self.nonce, scope.emission_count
        )

        instance_count = round(instance_selection)

        min_radius = 250.0
        max_radius = 3072/2 # might be a better way to calculat this, take into account the particle size
        radius = min_radius + (get_random_deterministic_float(self.random_seed, self.nonce) * (max_radius - min_radius))

        instances: List[MadeIngredientPrep] = []

        for instance_index in range(instance_count):
            rotation = select_value(self.random_seed, self.nonce, scope.rotation)
            scale = select_value(self.random_seed, self.nonce, scope.particle_scale)
            translation = self.calculate_tree_position(radius, instance_count, instance_index)
            translation = self.translate_to_canvas(translation)
            instances.append(
                MadeIngredientPrep(
                    translation=translation, rotation=rotation, scale=scale
                )
            )

        return instances

    def calculate_tree_position(self, radius, item_count, index) -> Tuple[float,float]:
        """Return a position on the circle based on the index count"""

        degree_int = (2 * PI) / item_count
        rotation = index * degree_int
        x = radius * cos(rotation)
        y = radius * sin(rotation)

        return (x, y)

class RandomScatter(Scatter):
    "randomly scatter by placing items on circles"

    def evaluate(self, scope: IngredientScope) -> List[MadeIngredientPrep]:

        print(scope)

        instance_selection = select_value(
            self.random_seed, self.nonce, scope.emission_count
        )

        instance_count = round(instance_selection)
        print(f"instance count: {instance_count}")

        instances: List[MadeIngredientPrep] = []

        for instance_index in range(instance_count):
            rotation = select_value(self.random_seed, self.nonce, scope.rotation)
            scale = select_value(self.random_seed, self.nonce, scope.particle_scale)
            translation = self.get_random_point(
                self.random_seed, self.nonce, instance_index
            )
            translation = self.translate_to_canvas(translation)
            instances.append(
                MadeIngredientPrep(
                    translation=translation, rotation=rotation, scale=scale
                )
            )

        return instances

    def get_random_point(
        self, seed: int, nonce: Counter, position: int
    ) -> Tuple[SCALAR, SCALAR]:
        """Slightly different calculation for random point - limits the distribution to a radius"""

        rad = get_random_deterministic_float(seed, nonce, "random-point_rad", position)
        ang = get_random_deterministic_float(seed, nonce, "random-point_ang", position)

        random_radius = rad * (3052.0/2.0)  # 3072 is the pixel width of pies - temp minus 20 to decrease bleed off pie
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