from natron_base import NatronBase

# kitchen order attrs
unique_id = "1010"
category = "crust"
index = 2
variation = 1


translate = [0,0]
scale = 1
rotate = 0


class Crust(NatronBase):
    """base class override"""


instance = Crust(app)
instance.load("CRUST_DATA_PATH")
instance.setIngredient(instance.in_file)
instance.setSwitchProperty(instance.unique_id, instance.ON)
instance.setPosition(instance.unique_id, translate, scale, rotate)
instance.render(instance.out_file)