#!/usr/bin/env python

import os
import json

from natron_base import NatronBase


class Slice(NatronBase):
    """base class override"""
    MAX_INSTANCES = 8

    def __init__(self, app, env_var):
        self.natron = app
        self._load_json_data(env_var)

        # 
        for item in self.instances:
            index = self.instances.index(item)
            image_uri = item["image_uri"]
            self._load_image(image_uri, index)

        self._setBake()

    def enable(self, switch_id=None):
        """Which plate will be activated in the natron image tree. plates are number 0 to 7, zereo starting a noon to 1 o'clock. defalut plate id is all plates""" 
        
        
        # Default slice list is all slices. To enable specific selection, need to define this in json
        # defualut is on
        # slice_list = [0,1,2,3,4,5,6,7]

        # for x in slice_list:
        #     node = self.natron.getNode("Plate_%s" % slice_list)
        #     param = node.getParam("which")
        # if param is not None:
        #     param.setValue(self.ON)
        # del param

    def render(self):
        """override the render function in your derived class to customize behavior"""
        for item in self.instances:
            index = self.instances.index(item)
            # enable the slice switch
            # set the alpha
            # set the nft source image
        # 
        self.setOutput()
instance = Slice(app, "SLICE_DATA_PATH")
instance.render()