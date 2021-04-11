#!/usr/bin/env python

from natron_base import NatronBase


class Box(NatronBase):
    """base class override"""


instance = Box(app, "BOX_DATA_PATH")
instance.render()