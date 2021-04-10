# This is the content of a natron rarepizzas script
# Anthony Shafer aka "Shrimp" @anthonyshafer

import render_config as config

# kitchen order attrs
unique_id = "0500"
category = "waxpaper"
index = 1
filename = "0500-waxpaper-redchecker"
fileout = "rp-#####-waxpaper.png"
translate = [0, 0]
scale = 0.975
rotate = 0

# get ingredient from kitchen
lastNode = app.getNode("i1")
param = lastNode.getParam("filename" + ".png")
if param is not None:
    param.setValue(config.paths["database"] + filename)
del param

# switch index
switchNode = app.getNode("switch_%s" % unique_id)
whichP = switchNode.getParam("which")
whichP.setValue(index)

# change params
trsNode = app.getNode("TRS_%s" % unique_id)
translateP = trsNode.getParam("translate")
rotateP = trsNode.getParam("rotate")
scaleP = trsNode.getParam("scale")
translateP.setValue(translate[0], 0)
translateP.setValue(translate[1], 1)
rotateP.setValue(rotate)
scaleP.setValue(scale)

# bake to oven
lastNode = app.getNode("w1")
param = lastNode.getParam("filename")
if param is not None:
    param.setValue(config.paths["output"] + fileout)
del param
