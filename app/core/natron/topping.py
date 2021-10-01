#!/usr/bin/env python

import os
import json

from natron_base import NatronBase


class Topping(NatronBase):
    """base class override handles single input only for now"""

    MAX_INSTANCES = 30

    def __init__(self, app, env_var):
        self.natron = app
        self._load_json_data(env_var)

        for item in self.instances:
            index = self.instances.index(item)
            image_uri = item["image_uri"]
            self._load_image(image_uri, index)

    def _load_json_data(self, env_var):
        """Override for depth swap JSON"""

        file_path = os.environ[env_var]
        with open(file_path) as json_file:
            self.element = json.load(json_file)
        print(self.element)

        # Depth swap layers has different JSON -source is a ShuffledLayer
        self.index = self.element["index"]
        self.unique_id = self.element["unique_id"]
        self.out_file = self.element["output_mask"]
        self.instances = self.element["instances"]

        return self.element

    def render(self):
        """override the render function in your derived class to customize behavior"""
        for item in self.instances:
            index = self.instances.index(item)
            # enable the switch
            self.enable(index)
            # set the transform
            self.setTransform(
                item["translation"], item["scale"], item["rotation"], index
            )
        self.setOutput()

    def render_single(self):
        self.enable("single")
        item = self.instances[0]
        self.setTransform(item["translation"], item["scale"], item["rotation"])
        self.setOutput()


instance = Topping(app, "TOPPING_DATA_PATH")
instance.render()
