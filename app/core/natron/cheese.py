#!/usr/bin/env python

from natron_base import NatronBase


class Cheese(NatronBase):
    """base class override"""

    def __init__(self, app, env_var):
        self.natron = app
        self._load_json_data(env_var)

        for item in self.instances:
            index = self.instances.index(item)
            image_uri = item["image_uri"]
            self._load_image(image_uri, index)

        self._setBake()


instance = Cheese(app, "CHEESE_DATA_PATH")
instance.render()
