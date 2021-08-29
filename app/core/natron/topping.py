#!/usr/bin/env python

from natron_base import NatronBase


class Topping(NatronBase):
    """base class override handles single input only for now"""

    MAX_INSTANCES = 30

    def __init__(self, app, env_var):
        self.natron = app
        self._load_json_data(env_var)

        for item in self.instances:
            index = self.instances.index(item)
            self._load_image(self.in_file, index)

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
