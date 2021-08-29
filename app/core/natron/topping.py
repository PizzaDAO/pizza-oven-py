#!/usr/bin/env python

from natron_base import NatronBase


class Topping(NatronBase):
    """base class override handles single input only for now"""

    MAX_INSTANCES = 30

    def __init__(self, app, env_var):
        self.natron = app
        self._load_json_data(env_var)

        # TODO: allow for loading one file per input node
        # so we can have different variations of each topping?
        self._load_image(self.in_file, "input_single")

    def render(self):
        """override the render function in your derived class to customize behavior"""
        self._disableOthers()
        for instance in self.instances:
            index = self.instances.index(instance)
            self.enable(index)
            self.setTransform(
                instance["translation"], instance["scale"], instance["rotation"], index
            )
        self.setOutput()

    def render_single(self):
        """override the render function in your derived class to customize behavior"""
        self._disableOthers()
        self.enable("single")
        self.setTransform(self.translate, self.scale, self.rotate)
        self.setOutput()

    def _disableOthers(self):
        for i in range(0, self.MAX_INSTANCES):
            self.disable(i)


instance = Topping(app, "TOPPING_DATA_PATH")
instance.render()
