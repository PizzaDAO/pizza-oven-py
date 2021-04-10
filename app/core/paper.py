from natron_base import NatronBase

# kitchen order attrs
unique_id = "0500"
category = "waxpaper"
index = 1

in_file = "0500-waxpaper-redchecker.png"
out_file = "rp-#####-waxpaper.png"

translate = [0, 0]
scale = 0.975
rotate = 0

node = app.getNode("switch_%s" % unique_id)
param = node.getParam("which")
param.setValue(index)


class Paper(NatronBase):
    """base class override"""

    pass


paper = Paper(app)
paper.setIngredient(in_file)
# TODO: paper.setSwitchProperty(unique_id, index)
paper.setPosition(unique_id, translate, scale, rotate)
paper.render(out_file)