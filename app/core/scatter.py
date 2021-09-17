from math import cos, sin, sqrt
from app.models.prep import SCALAR, MadeIngredientPrep
from typing import Dict, List, Tuple

from ..models.recipe import IngredientScope, ScatterType

from .random_num import (
    Counter,
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