#!/usr/bin/env python

from natron_base import NatronBase


class Sauce(NatronBase):
    """base class override"""


instance = Sauce(app, "SAUCE_DATA_PATH")
instance.render()
