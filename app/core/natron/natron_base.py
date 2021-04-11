#!/usr/bin/env python
import os
import json

import natron_config as config

# import render_config as config


class NatronBase:
    """Base class for toggling natron nodes"""

    ON = 1
    OFF = 0

    def __init__(self, app):
        self.natron = app

    def load(self, env_var):
        file_path = os.environ[env_var]
        with open(file_path) as json_file:
            element = json.load(json_file)
        print(element)
        self.unique_id = element["ingredient"]["unique_id"]
        self.in_file = element["ingredient"]["image_uris"]["filename"]
        self.out_file = element["ingredient"]["image_uris"]["output_mask"]

    def setIngredient(self, filename):
        print("loading: " + config.paths["database"] + filename)
        node = self.natron.getNode("i1")
        param = node.getParam("filename")
        if param is not None:
            param.setValue(config.paths["database"] + filename)
        del param

    def setSwitchProperty(self, unique_id, value):
        node = self.natron.getNode("Switch_%s" % unique_id)
        param = node.getParam("which")
        param.setValue(value)

    def setPosition(self, unique_id, translate, scale, rotate):
        node = self.natron.getNode("TRS_%s" % unique_id)

        if translate is not None:
            translateP = node.getParam("translate")
            translateP.setValue(translate[0], 0)
            translateP.setValue(translate[1], 1)
        if rotate is not None:
            rotateP = node.getParam("rotate")
            rotateP.setValue(rotate)
        if scale is not None:
            scaleP = node.getParam("scale")
            scaleP.setValue(scale, 0)
            scaleP.setValue(scale, 1)

    def render(self, filename):
        print("rendering: " + config.paths["output"] + filename)
        node = self.natron.getNode("w1")
        param = node.getParam("filename")
        if param is not None:
            param.setValue(config.paths["output"] + filename)
        del param
