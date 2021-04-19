#!/usr/bin/env python

from natron_base import NatronBase


class Extra(NatronBase):
    """base class override"""


instance = Extra(app, "EXTRAS_DATA_PATH")
instance.render()
