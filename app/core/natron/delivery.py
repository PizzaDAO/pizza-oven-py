#!/usr/bin/env python

import os
import json

import natron_config as config
from natron_base import NatronBase

# This python 2.7 method will build the final delivery nodegraph inside of Natron
class Delivery(NatronBase):
    """base class override handles single input only for now"""

    def __init__(self, app, env_var):
        self.natron = app
        self._load_json_data(env_var)
        print("delivery __init__")

    def render(self):
        # Start of node "Merge1"
        print("rendering in delivery.py")
        count = 6  # temper

        mergeNode = self.natron.createNode("net.sf.openfx.MergePlugin", 1)
        mergeNode.setScriptName("Merge1")
        mergeNode.setLabel("Merge1")
        mergeNode.setPosition(1069, 322)
        mergeNode.setSize(104, 43)
        mergeNode.setColor(0.3, 0.37, 0.776)
        # End of node "Merge1"

        # Iterate through the layer count and dynamically build a Natron node graph with params set
        i = 0
        for layer_filename in self.element["layers"]:
            pad = "0"
            layer = format(i, pad + str(2))  # layer pad 2

            # Start of Read_ nodes
            lastNode = self.natron.createNode("fr.inria.built-in.Read", 1)
            lastNode.setScriptName("Read_%s" % layer)
            lastNode.setLabel("Read_%s" % layer)

            param = lastNode.getParam("decodingPluginID")
            if param is not None:
                param.setValue("fr.inria.openfx.ReadPNG")
                del param

            param = lastNode.getParam("filename")
            if param is not None:
                filename = config.paths["output"] + layer_filename
                print(filename)
                param.setValue(filename)
                del param

            param = lastNode.getParam("lastFrame")
            if param is not None:
                param.setValue(10000, 0)
                del param

            param = lastNode.getParam("filePremult")
            if param is not None:
                param.set("unpremult")
                del param

            param = lastNode.getParam("onMissingFrame")
            if param is not None:
                param.set("black")
                del param

            param = lastNode.getParam("timeDomainUserEdited")
            if param is not None:
                param.setValue(True)
                del param

            # connect up node before destrying
            mergeNode.connectInput(i + 3, lastNode)

            del lastNode
            # End of node "Read_"
            i += 1

        self.setOutput(mergeNode)

    def setOutput(self, mergeNode):
        # Start of node "FinalGrade" for colorcorrection
        gradeNode = app.createNode("net.sf.openfx.GradePlugin", 2)
        gradeNode.setScriptName("FinalGrade")
        gradeNode.setLabel("FinalGrade")
        gradeNode.setPosition(1069, 478)
        gradeNode.setSize(104, 26)
        gradeNode.setColor(0.48, 0.66, 1)
        param = gradeNode.getParam("white")
        if param is not None:
            param.setValue(1.113, 0)
            param.setValue(1.113, 1)
            param.setValue(1.113, 2)
            param.setValue(1.113, 3)
        del param

        param = gradeNode.getParam("premult")
        if param is not None:
            param.setValue(True)
        del param

        # build writer node
        print(config.paths["output"] + self.out_file)
        writeNode = self.natron.createNode("fr.inria.built-in.Write", 1)
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
            param.setValue(config.paths["output"] + self.out_file)
            del param

        param = writeNode.getParam("NatronParamFormatChoice")
        if param is not None:
            param.set("HD")
            del param

        param = writeNode.getParam("ParamExistingInstance")
        if param is not None:
            param.setValue(True)
            del param

        # connect everything up
        gradeNode.connectInput(0, mergeNode)
        writeNode.connectInput(0, gradeNode)

    def _load_json_data(self, env_var):
        """Load the json data, assign some common properties, and return the json"""

        file_path = os.environ[env_var]
        print("loading")
        print(file_path)
        with open(file_path) as json_file:
            self.element = json.load(json_file)
        print(self.element)

        self.index = self.element["frame"]
        self.out_file = "####.png"


instance = Delivery(app, "DELIVERY_DATA_PATH")
instance.render()
