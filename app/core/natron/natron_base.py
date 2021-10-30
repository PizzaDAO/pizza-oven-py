#!/usr/bin/env python
import os
import json

import natron_config as config


class NatronBase(object):
    """Base class for toggling natron nodes"""

    ON = 1
    OFF = 0
    DONT_TRANSLATE = None
    DONT_SCALE = None
    DONT_ROTATE = None

    def __init__(self, app, env_var):
        self.natron = app
        self._load_json_data(env_var)
        self._load_image(self.in_file)
        self._setBake()

    def render(self):
        """override the render function in your derived class to customize behavior"""
        self.enable()
        item = self.instances[0]
        self.setTransform(item["translation"], item["scale"], item["rotation"])
        self.setOutput()

    def enable(self, switch_id=None):
        if switch_id is None:
            switch_id = self.unique_id

        node = self.natron.getNode("Switch_%s" % switch_id)
        if node is None:
            node = self.natron.getNode("Switch_default")
        if node is None:
            print("enable: could not find node: Switch_%s" % switch_id)
            return
        param = node.getParam("which")
        if param is not None:
            param.setValue(self.ON)
        del param

    def disable(self, switch_id=None):
        if switch_id is None:
            switch_id = self.unique_id

        node = self.natron.getNode("Switch_%s" % switch_id)
        if node is None:
            node = self.natron.getNode("Switch_default")
        if node is None:
            print("disable: could not find node: Switch_%s" % switch_id)
            return
        param = node.getParam("which")
        if param is not None:
            param.setValue(self.OFF)
        del param

    def setTransform(
        self,
        translate=DONT_TRANSLATE,
        scale=DONT_SCALE,
        rotate=DONT_ROTATE,
        switch_id=None,
    ):
        if switch_id is None:
            switch_id = self.unique_id

        node = self.natron.getNode("TRS_%s" % switch_id)
        if node is None:
            node = self.natron.getNode("TRS_default")
        if node is None:
            print("setTransform: could not find node: TRS_%s" % switch_id)
            return

        if translate is not None:
            param = node.getParam("translate")
            if param is not None:
                param.setValue(translate[0], 0)
                param.setValue(translate[1], 1)
            del param
        if rotate is not None:
            param = node.getParam("rotate")
            if param is not None:
                param.setValue(rotate)
            del param
        if scale is not None:
            # value is -1 to 1
            param = node.getParam("scale")
            if param is not None:
                param.setValue(scale, 0)
                param.setValue(scale, 1)
            del param

    def setImageURI(self, file_path, switch_id=None):
        node = self.natron.getNode("TRS_%s" % switch_id)

        if node is None:
            node = self.natron.getNode("i%s" % switch_id)
        if node is None:
            node = self.natron.getNode("input_default")
        if node is None:
            node = self.natron.getNode("i1")
        if node is None:
            print("setImageURI: could not find node for: %s" % file_path)
            return
        param = node.getParam("filename")
        if param is not None:
            param.setValue(file_path)
        del param

    def setOutput(self):
        print(config.paths["output"] + self.out_file)
        node = self.natron.getNode("w1")
        if node is None:
            print("setOutput: could not find node: w1")
            return
        param = node.getParam("filename")
        if param is not None:
            param.setValue(config.paths["output"] + self.out_file)
        del param

    def watermark(self):
        node = self.natron.getNode("watermark")
        if node is None:
            print("watermark: could not find node: watermark")
        else:
            param = node.getParm("text")
            param.setValue("layer %s" % self.index)

    def burn(self):
        pass

    def melt(self):
        pass

    def blend(self):
        pass

    def _load_json_data(self, env_var):
        """Load the json data, assign some common properties, and return the json"""

        file_path = os.environ[env_var]
        with open(file_path) as json_file:
            self.element = json.load(json_file)
        print(self.element)

        # ingredients
        self.index = self.element["ingredient"]["index"]
        self.unique_id = self.element["ingredient"]["unique_id"]
        self.in_file = self.element["ingredient"]["image_uris"]["filename"]
        self.out_file = self.element["ingredient"]["image_uris"]["output_mask"]
        self.instances = self.element["instances"]
        # nutritional bake data
        self.potassium = self.element["ingredient"]["nutrition"]["potassium"]
        self.vitamin_c = self.element["ingredient"]["nutrition"]["vitamin_c"]
        self.magnesium = self.element["ingredient"]["nutrition"]["magnesium"]
        self.vitamin_b5 = self.element["ingredient"]["nutrition"]["vitamin_b5"]
        self.vitamin_d = self.element["ingredient"]["nutrition"]["vitamin_d"]
        self.vitamin_b7 = self.element["ingredient"]["nutrition"]["vitamin_b7"]
        self.height = self.element["ingredient"]["nutrition"]["height"]
        self.moisture = self.element["ingredient"]["nutrition"]["moisture"]
        self.cholesterol = self.element["ingredient"]["nutrition"]["cholesterol"]
        self.vitamin_a = self.element["ingredient"]["nutrition"]["vitamin_a"]
        self.dietary_fiber = self.element["ingredient"]["nutrition"]["dietary_fiber"]
        self.vitamin_b6 = self.element["ingredient"]["nutrition"]["vitamin_b6"]
        self.sugar = self.element["ingredient"]["nutrition"]["sugar"]
        self.protein = self.element["ingredient"]["nutrition"]["protein"]
        self.iron = self.element["ingredient"]["nutrition"]["iron"]
        self.complex_carb = self.element["ingredient"]["nutrition"]["complex_carb"]
        self.selenium = self.element["ingredient"]["nutrition"]["selenium"]
        self.vitamin_k = self.element["ingredient"]["nutrition"]["vitamin_k"]
        self.vitamin_b12 = self.element["ingredient"]["nutrition"]["vitamin_b12"]
        self.calories_from_fat = self.element["ingredient"]["nutrition"][
            "calories_from_fat"
        ]
        self.vitamin_e = self.element["ingredient"]["nutrition"]["vitamin_e"]
        self.zinc = self.element["ingredient"]["nutrition"]["zinc"]
        self.saturated_fat = self.element["ingredient"]["nutrition"]["saturated_fat"]
        self.iodine = self.element["ingredient"]["nutrition"]["iodine"]
        self.trans_fat = self.element["ingredient"]["nutrition"]["trans_fat"]
        self.sodium = self.element["ingredient"]["nutrition"]["sodium"]
        self.monosaturated_fat = self.element["ingredient"]["nutrition"][
            "monosaturated_fat"
        ]
        self.calcium = self.element["ingredient"]["nutrition"]["calcium"]
        self.riboflavin = self.element["ingredient"]["nutrition"]["riboflavin"]
        self.thiamin = self.element["ingredient"]["nutrition"]["thiamin"]
        self.folate = self.element["ingredient"]["nutrition"]["folate"]
        self.added_sugar = self.element["ingredient"]["nutrition"]["added_sugar"]
        self.chromium = self.element["ingredient"]["nutrition"]["chromium"]
        self.manganese = self.element["ingredient"]["nutrition"]["manganese"]

        return self.element

    def _load_image(self, filename, switch_id=None):
        print("loading: " + config.paths["database"] + filename)
        node = None

        if switch_id is None:
            switch_id = self.unique_id

        # if node_name is not None:
        #     node = self.natron.getNode(node_name)
        if node is None:
            node = self.natron.getNode("i%s" % switch_id)
        if node is None:
            node = self.natron.getNode("input_default")
        if node is None:
            node = self.natron.getNode("i1")
        if node is None:
            print("_load_image: could not find node for: %s" % filename)
            return
        param = node.getParam("filename")
        if param is not None:
            param.setValue(config.paths["database"] + filename)
        del param

    def _setBake(self, switch_id=None):

        if switch_id is None:
            switch_id = self.unique_id

        node_name = "Bake"
        node = self.natron.getNode(node_name)
        if node is None:
            node_name = "Bake_default"
            node = self.natron.getNode(node_name)
        if node is None:
            node_name = "Bake_" + str(switch_id)
            node = self.natron.getNode(node_name)
        if node is None:
            print("setBake: could not find any nodes. trying: Bake_%s" % switch_id)
            return
        else:
            print(f"Using bake node: {node_name}")

        # node = self.natron.getNode("Bake_%s" % switch_id)
        # if node is None:
        #     node = self.natron.getNode("Bake_default")
        # if node is None:
        #     print("setBake: could not find node: Bake_%s" % switch_id)
        #     return

        if self.potassium is not None:
            param = node.getParam("do_weld")
            if param is not None:
                param.setValue(self.potassium)
            del param

        if self.vitamin_c is not None:
            param = node.getParam("do_separation")
            if param is not None:
                param.setValue(self.vitamin_c)
            del param

        if self.magnesium is not None:
            param = node.getParam("do_burn_before")
            if param is not None:
                param.setValue(self.magnesium)
            del param

        if self.vitamin_b5 is not None:
            param = node.getParam("do_melt")
            if param is not None:
                param.setValue(self.vitamin_b5)
            del param

        if self.vitamin_d is not None:
            param = node.getParam("do_lumpiness")
            if param is not None:
                param.setValue(self.vitamin_d)
            del param

        if self.vitamin_b7 is not None:
            param = node.getParam("do_burn_after")
            if param is not None:
                param.setValue(self.vitamin_b7)
            del param

        ##------ float setters for separation

        if self.cholesterol is not None:
            param = node.getParam("clotting")
            if param is not None:
                param.setValue(self.cholesterol)
            del param

        if self.vitamin_a is not None:
            param = node.getParam("thinning")
            if param is not None:
                param.setValue(self.vitamin_a)
            del param

        if self.dietary_fiber is not None:
            param = node.getParam("coagulation")
            if param is not None:
                param.setValue(self.dietary_fiber)
            del param

        if self.vitamin_b6 is not None:
            param = node.getParam("absorption")
            if param is not None:
                param.setValue(self.vitamin_b6)
            del param

        ##------ float setters for burn_before

        if self.sugar is not None:
            param = node.getParam("burn_amt")
            if param is not None:
                param.setValue(self.sugar)
            del param

        if self.protein is not None:
            param = node.getParam("burn_edges")
            if param is not None:
                param.setValue(self.protein)
            del param

        if self.iron is not None:
            param = node.getParam("caramelization")
            if param is not None:
                param.setValue(self.iron)
            del param

        ##------float setters for melt

        if self.complex_carb is not None:
            param = node.getParam("liquify")
            if param is not None:
                param.setValue(self.complex_carb)
            del param

        if self.selenium is not None:
            param = node.getParam("amplify")
            if param is not None:
                param.setValue(self.selenium)
            del param

        if self.vitamin_k is not None:
            param = node.getParam("expand")
            if param is not None:
                param.setValue(self.vitamin_k)
            del param

        ##------lumpiness big

        if self.vitamin_b12 is not None:
            param = node.getParam("lumpy_big_mix")
            if param is not None:
                param.setValue(self.vitamin_b12)
            del param

        if self.calories_from_fat is not None:
            param = node.getParam("lumpy_big_size")
            if param is not None:
                param.setValue(self.calories_from_fat)
            del param

        if self.vitamin_e is not None:
            param = node.getParam("lumpy_big_intensity")
            if param is not None:
                param.setValue(self.vitamin_e)
            del param

        ##------ lumpiness small

        if self.zinc is not None:
            param = node.getParam("lumpy_small_mix")
            if param is not None:
                param.setValue(self.zinc)
            del param

        if self.saturated_fat is not None:
            param = node.getParam("lumpy_small_size")
            if param is not None:
                param.setValue(self.saturated_fat)
            del param

        ##------ lumpy mix
        if self.trans_fat is not None:
            param = node.getParam("lumpy_height")
            if param is not None:
                param.setValue(self.trans_fat)
            del param

        if self.sodium is not None:
            param = node.getParam("lumpy_mix")
            if param is not None:
                param.setValue(self.sodium)
            del param

        if self.monosaturated_fat is not None:
            param = node.getParam("lumpy_wet")
            if param is not None:
                param.setValue(self.monosaturated_fat)
            del param

        if self.calcium is not None:
            param = node.getParam("lumpy_rough")
            if param is not None:
                param.setValue(self.calcium)
            del param

        ##------ blend
        if self.riboflavin is not None:
            param = node.getParam("edge_size")
            if param is not None:
                param.setValue(self.riboflavin)
            del param

        if self.thiamin is not None:
            param = node.getParam("edge_falloff")
            if param is not None:
                param.setValue(self.thiamin)
            del param

        if self.folate is not None:
            param = node.getParam("thickness")
            if param is not None:
                param.setValue(self.folate)
            del param

        ##------ burn2 (charring)
        if self.added_sugar is not None:
            param = node.getParam("burn_amt2")
            if param is not None:
                param.setValue(self.added_sugar)
            del param

        if self.chromium is not None:
            param = node.getParam("burn_edges2")
            if param is not None:
                param.setValue(self.chromium)
            del param

        if self.manganese is not None:
            param = node.getParam("caramelization2")
            if param is not None:
                param.setValue(self.manganese)
            del param

        # TODO: fix when added to the spreadsheet
        # if self.weight is not None:
        #     param = node.getParam("weight")
        #     if param is not None:
        #         param.setValue(self.weight)
        #     del param

        if self.height is not None:
            param = node.getParam("height")
            if param is not None:
                param.setValue(self.height)
            del param

        if self.moisture is not None:
            param = node.getParam("moisture")
            if param is not None:
                param.setValue(self.moisture)
            del param
