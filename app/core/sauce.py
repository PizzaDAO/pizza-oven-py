# This is the content of a natron rarepizzas script
# Anthony Shafer aka "Shrimp" @anthonyshafer
# Python2.7 because of Naton

import render_config as config

# setup
layer = "sauce"

# params
import random

rotate = random.randint(-360, 360)

# files
filein = "1000-%s-thin.png" % layer
fileout = "rp-#####-%s.png" % layer


# get ingredient from kitchen
lastNode = app.getNode("i1")
param = lastNode.getParam("filename")
if param is not None:
    param.setValue(config.paths["database"] + filein)
del param

# random rotate
lastNode = app.getNode("TRS_%s" % layer)
param = lastNode.getParam("rotate")
if param is not None:
    param.setValue(rotate)
del param

# bake to oven
lastNode = app.getNode("w1")
param = lastNode.getParam("filename")
if param is not None:
    param.setValue(config.paths["output"] + fileout)
del param
