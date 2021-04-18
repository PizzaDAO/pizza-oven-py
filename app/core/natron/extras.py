#!/usr/bin/env python

from natron_base import NatronBase


class Extra(NatronBase):
    """base class override"""

    def render(self):
        """override the render function in your derived class to customize behavior"""
        super(Extra, self).render()
        self.enable("%s_2" % self.unique_id)


instance = Extra(app, "EXTRAS_DATA_PATH")
instance.render()
