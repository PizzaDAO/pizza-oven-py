# This is the content of a natron rarepizzas script
# Anthony Shafer aka "Shrimp" @anthonyshafer
# Python2.7 because of Naton

# This is the content of a natron rarepizzas script
# Anthony Shafer aka "Shrimp" @anthonyshafer

# kitchen order attrs
unique_id = "1010"
category = "crust"
index = 2
variation = 1
filename = "1010-crust-thick"
fileout = "rp-#####-crust"
translate = [1000,1000]
scale = .5
rotate = 180

# paths
oven = "../oven/"
idb = "../ingredients-db/"

# get ingredient from kitchen
lastNode = app.getNode("i%s" % index)
param = lastNode.getParam("filename")
if param is not None:
	param.setValue(idb+filename+".png")
del param


# switch index
switchNode = app.getNode("Switch%s" % unique_id)
whichP = switchNode.getParam("which")
whichP.setValue(variation)

# change params
trsNode = app.getNode("TRS_%s" % unique_id)
translateP = trsNode.getParam("translate")
rotateP = trsNode.getParam("rotate")
scaleP = trsNode.getParam("scale")
translateP.setValue(translate[0],0)
translateP.setValue(translate[1],1)
rotateP.setValue(rotate)
scaleP.setValue(scale,0)
scaleP.setValue(scale,1)

# bake to oven
lastNode= app.getNode("w1")
param = lastNode.getParam("filename")
if param is not None:
	param.setValue(oven+fileout+".png")
del param
