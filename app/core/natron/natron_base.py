#!/usr/bin/env python
import os
import json

import natron_config as config


class NatronBase:
    """Base class for toggling natron nodes"""

    ON = 1
    OFF = 0
    DONT_TRANSLATE = None
    DONT_SCALE = None
    DONT_ROTATE = None

    def __init__(self, app, env_var):
        self.natron = app
        self._load_json_data(env_var)
        self._load_image(self.in_file)

    def render(self):
        """override the render function in your derived class to customize behavior"""
        self.enable()
        self.setTransform(self.translate, self.scale, self.rotate)
        self.setOutput()

    def enable(self):
        node = self.natron.getNode("Switch_%s" % self.unique_id)
        if node is None:
            print("enable: could not find node")
            return
        param = node.getParam("which")
        if param is not None:
            param.setValue(self.ON)
        del param

    def disable(self):
        node = self.natron.getNode("Switch_%s" % self.unique_id)
        if node is None:
            print("disable: could not find node")
            return
        param = node.getParam("which")
        if param is not None:
            param.setValue(self.OFF)
        del param

    def setTransform(
        self, translate=DONT_TRANSLATE, scale=DONT_SCALE, rotate=DONT_ROTATE
    ):
        node = self.natron.getNode("TRS_%s" % self.unique_id)
        if node is None:
            print("setTransform: could not find node")
            return

        if translate is not None:
            param = node.getParam("translate")
            if param is not None:
                param.setValue(translate[0], 0)
                param.setValue(translate[1], 1)
            del param
        if rotate is not None:
            param = node.getParam("rotate")
            if param is not None:
                param.setValue(rotate)
            del param
        if scale is not None:
            param = node.getParam("scale")
            if param is not None:
                param.setValue(scale, 0)
                param.setValue(scale, 1)
            del param

    def setOutput(self):
        print("setOutput: " + config.paths["output"] + self.out_file % self.index)
        node = self.natron.getNode("w1")
        if node is None:
            print("setOutput: could not find node")
            return
        param = node.getParam("filename")
        if param is not None:
            param.setValue(config.paths["output"] + self.out_file % self.index)
        del param
 
    def burn(self):
        pass

    def melt(self):
        pass

    def blend(self):
        pass

    def _load_json_data(self, env_var):
        file_path = os.environ[env_var]
        with open(file_path) as json_file:
            self.element = json.load(json_file)
        print(self.element)

        # ingredients
        self.index = self.element["ingredient"]["index"]
        self.unique_id = self.element["ingredient"]["unique_id"]
        self.in_file = self.element["ingredient"]["image_uris"]["filename"]
        self.out_file = self.element["ingredient"]["image_uris"]["output_mask"]

        # node transforms
        # TODO: translate
        self.translate = [0, 0]
        self.rotate = self.element["prep"]["rotation"]
        self.scale = self.element["prep"]["particle_scale"]

    def _load_image(self, filename):
        print("loading: " + config.paths["database"] + filename)
        node = self.natron.getNode("i1")
        param = node.getParam("filename")
        if param is not None:
            param.setValue(config.paths["database"] + filename)
        del param