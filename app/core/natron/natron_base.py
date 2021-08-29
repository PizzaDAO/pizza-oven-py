#!/usr/bin/env python
import os
import json

import natron_config as config


class NatronBase(object):
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
        item = self.instances[0]
        self.setTransform(item["translation"], item["scale"], item["rotation"])
        self.setOutput()

    def enable(self, switch_id=None):
        if switch_id is None:
            switch_id = self.unique_id

        node = self.natron.getNode("Switch_%s" % switch_id)
        if node is None:
            node = self.natron.getNode("Switch_default")
        if node is None:
            print("enable: could not find node: Switch_%s" % switch_id)
            return
        param = node.getParam("which")
        if param is not None:
            param.setValue(self.ON)
        del param

    def disable(self, switch_id=None):
        if switch_id is None:
            switch_id = self.unique_id

        node = self.natron.getNode("Switch_%s" % switch_id)
        if node is None:
            node = self.natron.getNode("Switch_default")
        if node is None:
            print("disable: could not find node: Switch_%s" % switch_id)
            return
        param = node.getParam("which")
        if param is not None:
            param.setValue(self.OFF)
        del param

    def setTransform(
        self,
        translate=DONT_TRANSLATE,
        scale=DONT_SCALE,
        rotate=DONT_ROTATE,
        switch_id=None,
    ):
        if switch_id is None:
            switch_id = self.unique_id

        node = self.natron.getNode("TRS_%s" % switch_id)
        if node is None:
            node = self.natron.getNode("TRS_default")
        if node is None:
            print("setTransform: could not find node: TRS_%s" % switch_id)
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
            # value is -1 to 1
            param = node.getParam("scale")
            if param is not None:
                param.setValue(scale, 0)
                param.setValue(scale, 1)
            del param

    def setOutput(self):
        print("setOutput: " + config.paths["output"] + self.out_file % self.index)

        node = self.natron.getNode("w1")
        if node is None:
            print("setOutput: could not find node: w1")
            return
        param = node.getParam("filename")
        if param is not None:
            param.setValue(config.paths["output"] + self.out_file % self.index)
        del param

    def watermark(self):
        node = self.natron.getNode("watermark")
        if node is None:
            print("watermark: could not find node: watermark")
        else:
            param = node.getParm("text")
            param.setValue("layer %s" % self.index)

    def burn(self):
        pass

    def melt(self):
        pass

    def blend(self):
        pass

    def _load_json_data(self, env_var):
        """Load the json data, assign some common properties, and return the json"""

        file_path = os.environ[env_var]
        with open(file_path) as json_file:
            self.element = json.load(json_file)
        print(self.element)

        # ingredients
        self.index = self.element["ingredient"]["index"]
        self.unique_id = self.element["ingredient"]["unique_id"]
        self.in_file = self.element["ingredient"]["image_uris"]["filename"]
        self.out_file = self.element["ingredient"]["image_uris"]["output_mask"]
        self.instances = self.element["instances"]

        return self.element

    def _load_image(self, filename, switch_id=None):
        print("loading: " + config.paths["database"] + filename)
        node = None

        if switch_id is None:
            switch_id = self.unique_id

        # if node_name is not None:
        #     node = self.natron.getNode(node_name)
        if node is None:
            node = self.natron.getNode("i%s" % switch_id)
        if node is None:
            node = self.natron.getNode("input_default")
        if node is None:
            node = self.natron.getNode("i1")
        if node is None:
            print("_load_image: could not find node for: %s" % filename)
            return
        param = node.getParam("filename")
        if param is not None:
            param.setValue(config.paths["database"] + filename)
        del param