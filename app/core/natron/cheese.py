#!/usr/bin/env python

from natron_base import NatronBase


class Cheese(NatronBase):
    """base class override"""


instance = Cheese(app, "CHEESE_DATA_PATH")
instance.render()
