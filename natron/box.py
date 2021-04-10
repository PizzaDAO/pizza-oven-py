# This is the content of a natron rarepizzas script
# Anthony Shafer aka "Shrimp" @anthonyshafer

# files
filename = "0000-box-cardboard.png"
fileout = "rp-#####-box.png"

# paths
oven = "../oven/"
idb = "../ingredients-db/"

# get ingredient from kitchen
lastNode = app.getNode("i1")
param = lastNode.getParam("filename")
if param is not None:
	param.setValue(idb+filename)
del param


# bake to oven
lastNode= app.getNode("w1")
param = lastNode.getParam("filename")
if param is not None:
	param.setValue(oven+fileout)
del param
