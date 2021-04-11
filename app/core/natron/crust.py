from natron_base import NatronBase

# kitchen order attrs
unique_id = "1010"
category = "crust"
index = 2
variation = 1


translate = [1000, 1000]
scale = 0.5
rotate = 180


class Crust(NatronBase):
    """base class override"""


instance = Crust(app)
instance.load("CRUST_DATA_PATH")
instance.setIngredient(instance.in_file)
instance.setSwitchProperty(instance.unique_id, instance.ON)
instance.setPosition(instance.unique_id, translate, scale, rotate)
instance.render(instance.out_file)