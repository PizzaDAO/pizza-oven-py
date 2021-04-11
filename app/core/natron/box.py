#!/usr/bin/env python
import os
import json

from natron_base import NatronBase

# files
# in_file = "0000-box-cardboard.png"
# out_file = "rp-#####-box.png"


class Box(NatronBase):
    """base class override"""

    def load(self):
        print("rendering in natron")
        file_path = os.environ["BOX_DATA_PATH"]
        with open(file_path) as json_file:
            element = json.load(json_file)
        print(element)
        self.in_file = element["ingredient"]["image_uris"]["filename"]
        self.out_file = element["ingredient"]["image_uris"]["output_mask"]

        print(self.out_file)


box = Box(app)
box.load()
box.setIngredient(box.in_file)
box.render(box.out_file)