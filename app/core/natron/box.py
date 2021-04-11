#!/usr/bin/env python
import os
import json

from natron_base import NatronBase


class Box(NatronBase):
    """base class override"""


instance = Box(app)
instance.load("BOX_DATA_PATH")
instance.setIngredient(instance.in_file)
instance.setSwitchProperty(instance.unique_id, instance.ON)
instance.render(instance.out_file)