all of the files in this folder are python 2.7 compatible

def doSomethingSpecial(self, some_unique_index, some_value_param):
    # set a default value if the param is none
    # this is the value that will be passed to the node
    # so this is like a translation coordiante, or an on/off or something
    if some_value_param is None:
       # maybe there is a default value such as 1 or 360 or something
       # that is defined at the class level or some other outer scope
       some_value_param = self.some_default_value

    # using the some_unique_index and a specific prefix
    # try to load the node by unique index. notice `SomethingSpecial`
    # is the same as the function name
    node = self.natron.getNode("SomethingSpecial_%s" % some_unique_index)

    # if we couldnt find the some_unique_index node, check for a default
    if node is None:
       node = self.natron.getNode("SomethingSpecial_default")

    # neither the some_unique_index and default nodes were found
    # so print an error and return
    if node is None:
       print("disable: could not find node: SomethingSpecial_%s" % switch_id)
       return

    # ok we made it this far means we found the node and can manipulate a value
    # note the param name can be anything and is up to you 
    # and correlates to whatever you set it to in natron.  
    # it could even be passed in as a parameter if needed 
    # (such as if you have say 20 topping translation params that are all the same
    # except their index value, we could loop over them, etc.)
    param = node.getParam("some_parameter_name_on_the_node")
    if param is not None:
       # now we finally set the value of the parameter that came in
       param.setValue(some_value_param)
    del param