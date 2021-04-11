#!/usr/bin/env python
import os
import json

import natron_config as config

# import render_config as config


class NatronBase:
    """Base class for toggling natron nodes"""

    # in_file = ""
    # out_file = ""

    def __init__(self, app):
        self.natron = app

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
