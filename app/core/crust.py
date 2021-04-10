from natron_base import NatronBase

# kitchen order attrs
unique_id = "1010"
category = "crust"
index = 2
variation = 1

in_file = "1010-crust-thick.png"
out_file = "rp-#####-crust.png"

translate = [1000, 1000]
scale = 0.5
rotate = 180


class Crust(NatronBase):
    """base class override"""


crust = Crust(app)
crust.setIngredient(in_file)
crust.setSwitchProperty(unique_id, index)
crust.setPosition(unique_id, translate, scale, rotate)
crust.render(out_file)