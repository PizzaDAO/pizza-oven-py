#!/usr/bin/env python

import os
import json

from natron_base import NatronBase

# This python 2.7 method will build the final delivery nodegraph inside of Natron
class Delivery(NatronBase):
    """base class override handles single input only for now"""

    def __init__(self, app, env_var):
        self.natron = app
        self._load_json_data(env_var)
        print("deliverynodes __init__")

    def render(self):
        # Start of node "Merge1"
        print("rendering in deliverynodes.py")
        count = 6  # temper

        mergeNode = app.createNode("net.sf.openfx.MergePlugin", 1)
        mergeNode.setScriptName("Merge1")
        mergeNode.setLabel("Merge1")
        mergeNode.setPosition(1069, 322)
        mergeNode.setSize(104, 43)
        mergeNode.setColor(0.3, 0.37, 0.776)
        # End of node "Merge1"

        # Iterate through the layer count and dynamically build a Natron node graph with params set
        for i in range(0, count + 1):
            position = 150 * i
            pad = "0"
            layer = format(i, pad + str(2))  # layer pad 2
            tokenID = format(frame, pad + str(4))  # frame pad 4

            # Start of Read_ nodes
            lastNode = app.createNode("fr.inria.built-in.Read", 1)
            lastNode.setScriptName("Read_%s" % layer)
            lastNode.setLabel("Read_%s" % layer)
            lastNode.setPosition(position, 65)
            lastNode.setSize(128, 78)
            lastNode.setColor(0.7, 0.7, 0.7)

            param = lastNode.getParam("decodingPluginID")
            if param is not None:
                param.setValue("fr.inria.openfx.ReadPNG")
                del param

            param = lastNode.getParam("filename")
            if param is not None:
                filename = """[Project]/../output/%s-layer-%s.png""" % (
                    """####""",
                    layer,
                )
                param.setValue(filename)
                del param

            param = lastNode.getParam("lastFrame")
            if param is not None:
                param.setValue(10000, 0)
                del param

            param = lastNode.getParam("onMissingFrame")
            if param is not None:
                param.set(4)
                del param

            param = lastNode.getParam("timeDomainUserEdited")
            if param is not None:
                param.setValue(True)
                del param

            # connect up node before destrying
            mergeNode.connectInput(i + 3, lastNode)

            del lastNode
            # End of node "Read_"

        # build writer node
        writeNode = app.createNode("fr.inria.built-in.Write", 1)
        writeNode.setScriptName("w1")
        writeNode.setLabel("w1")
        writeNode.setPosition(1069, 713)
        writeNode.setSize(104, 43)
        writeNode.setColor(0.75, 0.75, 0)

        param = writeNode.getParam("encodingPluginID")
        if param is not None:
            param.setValue("fr.inria.openfx.WritePNG")
            del param

        param = writeNode.getParam("filename")
        if param is not None:
            param.setValue("[Project]/../output/####.png")
            del param

        param = writeNode.getParam("NatronParamFormatChoice")
        if param is not None:
            param.set("HD")
            del param

        param = writeNode.getParam("ParamExistingInstance")
        if param is not None:
            param.setValue(True)
            del param

        # connect write node
        writeNode.connectInput(0, mergeNode)


instance = Delivery(app, "DELIVERY_DATA_PATH")
instance.render()
