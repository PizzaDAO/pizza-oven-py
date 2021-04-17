#!/usr/bin/env python

from natron_base import NatronBase


class Paper(NatronBase):
    """base class override"""


instance = Paper(app, "PAPER_DATA_PATH")
instance.render()