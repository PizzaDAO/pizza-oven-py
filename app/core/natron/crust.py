#!/usr/bin/env python

from natron_base import NatronBase


class Crust(NatronBase):
    """base class override"""


instance = Crust(app, "CRUST_DATA_PATH")
instance.render()