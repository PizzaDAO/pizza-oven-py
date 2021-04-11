from natron_base import NatronBase

# setup
# TODO: should be an index
layer = "sauce"

# params
import random

rotate = random.randint(-360, 360)


class Sauce(NatronBase):
    """base class override"""


DONT_TRANSLATE = None
DONT_SCALE = None

instance = Sauce(app)
instance.load("SAUCE_DATA_PATH")
instance.setIngredient(instance.in_file)
instance.setPosition(instance.unique_id, DONT_TRANSLATE, DONT_SCALE, rotate)
instance.render(instance.out_file)
