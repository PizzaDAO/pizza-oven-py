# This is the content of a natron rarepizzas script
# Anthony Shafer aka "Shrimp" @anthonyshafer

import render_config as config

# files
filename = "0000-box-cardboard.png"
fileout = "rp-#####-box.png"


# get ingredient from kitchen
lastNode = app.getNode("i1")
param = lastNode.getParam("filename")
if param is not None:
    param.setValue(config.paths["database"] + filename)
del param


# bake to oven
lastNode = app.getNode("w1")
param = lastNode.getParam("filename")
if param is not None:
    param.setValue(config.paths["output"] + fileout)
del param
