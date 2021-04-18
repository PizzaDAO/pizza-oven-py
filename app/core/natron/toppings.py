#!/usr/bin/env python

from natron_base import NatronBase


class Topping(NatronBase):
    """base class override"""

    def render(self):
        """override the render function in your derived class to customize behavior"""
        super(Topping, self).render()
        self.enable("%s_2" % self.unique_id)


instance = Topping(app, "TOPPINGS_DATA_PATH")
instance.render()
