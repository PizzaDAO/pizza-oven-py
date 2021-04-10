from natron_base import NatronBase

# setup
# TODO: should be an index
layer = "sauce"
unique_id = "sauce"

# params
import random

rotate = random.randint(-360, 360)

# files
in_file = "1000-%s-thin.png" % layer
out_file = "rp-#####-%s.png" % layer


# random rotate
# lastNode = app.getNode("TRS_%s" % layer)
# param = lastNode.getParam("rotate")
# if param is not None:
#     param.setValue(rotate)
# del param


class Sauce(NatronBase):
    """base class override"""

    pass


DONT_TRANSLATE = None
DONT_SCALE = None

sauce = Sauce(app)
sauce.setIngredient(in_file)
sauce.setPosition(unique_id, DONT_TRANSLATE, DONT_SCALE, rotate)
sauce.render(out_file)
