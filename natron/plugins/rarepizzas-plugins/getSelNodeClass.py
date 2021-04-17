import NatronEngine
from NatronGui import *

def getSelNodesClass():

    # get current Natron instance running in memory
    app = natron.getGuiInstance(0)

    # get selected nodes
    selectedNodes = app.getSelectedNodes()

    # cycle through every selected node
    for currentNode in selectedNodes:

        # get current node class
        currentID = currentNode.getPluginID()

        # write node class in console
        os.write(1,'\n' + str(currentID) + '\n')
        print(str(currentID) + '\n')

import os
import json
ko = "/Users/anthonyshafer/Dropbox/RarePizzas/rarepizzas-repo/pizza-oven-py/kitchen_order.json"
myfile = file(ko)
data = myfile.read()
print dir(data)
# parse file
obj = json.loads(data)

# show values
print obj["order"].keys()