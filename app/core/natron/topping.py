#!/usr/bin/env python

from natron_base import NatronBase


class Topping(NatronBase):
    """base class override"""


instance = Topping(app, "TOPPING_DATA_PATH")
instance.render()
