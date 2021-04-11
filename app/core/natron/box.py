#!/usr/bin/env python

from natron_base import NatronBase

# files
in_file = "0000-box-cardboard.png"
out_file = "rp-#####-box.png"


class Box(NatronBase):
    """base class override"""


box = Box(app)
box.setIngredient(in_file)
box.render(out_file)