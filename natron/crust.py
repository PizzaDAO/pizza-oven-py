# This is the content of a natron rarepizzas script
# Anthony Shafer aka "Shrimp" @anthonyshafer
# Python2.7 because of Naton

import random

# files
filein = "1000-crust-thin.png"
fileout = "rp-#####-crust.png"

# paths
oven = "../oven/"
idb = "../ingredients-db/"

# get ingredient from kitchen
lastNode = app.getNode("i1")
param = lastNode.getParam("filename")
if param is not None:
	param.setValue(idb+filein)
del param

# do some otherstuff...
lastNode = app.getNode("TRS_crust")
param = lastNode.getParam("rotate")
if param is not None:
	param.setValue(random.randint(-360,360))
del param

# bake to oven
lastNode= app.getNode("w1")
param = lastNode.getParam("filename")
if param is not None:
	param.setValue(oven+fileout)
del param
