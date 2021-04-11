from natron_base import NatronBase

# kitchen order attrs
unique_id = "0500"
category = "waxpaper"

translate = [0, 0]
scale = 0.975
rotate = 0


class Paper(NatronBase):
    """base class override"""


instance = Paper(app)
instance.load("PAPER_DATA_PATH")
instance.setIngredient(instance.in_file)
instance.setSwitchProperty(unique_id, instance.ON)
instance.setPosition(instance.unique_id, translate, scale, rotate)
instance.render(instance.out_file)