import pprint
import numpy as np


# ----------------------------------------------------------------------------------------------------------------
# Loading classes
# ---------------------------------------------------------------------------------------------------------------
class LoadCase:
    def __init__(self, name):
        self.name = name
        self.spec = dict()
        self.load_counter = 0

    def add_nodal_load(self, node_tag, Fx=0, Fy=0, Fz=0, Mx=0, My=0, Mz=0):
        self.load_counter += 1
        self.spec["nodal_load-{}".format(self.load_counter)] = dict(
            node_tag=node_tag, Fx=Fx, Fy=Fy, Fz=Fz, Mx=Mx, My=My, Mz=Mz)

    def add_point_load(self, position, Fy=0):
        self.load_counter += 1
        self.spec["nodal_load-{}".format(self.load_counter)] = dict(
            position=position, Fy=Fy)

    def add_line_load(self):
        pass

    def add_patch_load(self):
        pass

    def __str__(self):
        return "LoadCase {} \n".format(self.name) + pprint.pformat(self.spec)


# ---------------------------------------------------------------------------------------------------------------
class Loads:
    """
    Main class of loading definition
    """

    def __init__(self, name, Fx=0, Fy=0, Fz=0, Mx=0, My=0, Mz=0, wx=0, wy=0, wz=0):
        #
        self.name = name
        self.Fx = Fx
        self.Fy = Fy
        self.Fz = Fz
        self.Mx = Mx
        self.My = My
        self.Mz = Mz
        self.wx = wx
        self.wy = wy
        self.wz = wz
        #
        self.spec = dict()
        self.load_counter = 0

    def get_nodal_load_str(self, node_tag, load_value):
        # get str for ops.load() function.
        load_str = "ops.load({pt}, *{val})\n".format(pt=node_tag, val=load_value)
        return load_str


class NodalLoad(Loads):
    def __init__(self, name, node_tag, Fx=0, Fy=0, Fz=0, Mx=0, My=0, Mz=0):
        """

        :param name:
        :param load_value: list of load magnitude
        :param direction:
        :param node_tag: list of node tag of the load assignment. More nodes can be added using
        """
        super().__init__(name, Fx, Fy, Fz, Mx, My, Mz)
        self.node_tag = [node_tag]

    def edit_node_point(self, new_node_tag):
        self.node_tag.append(new_node_tag)

    def get_nodal_load_str(self):
        # get str for ops.load() function.
        load_str = []
        for node in list(self.node_tag):
            load_value = [self.Fx, self.Fy, self.Fz, self.Mx, self.My, self.Mz]
            load_str.append("ops.load({pt}, *{val})\n".format(pt=node, val=load_value))
        return load_str

class PointLoad(Loads):
    def __init__(self, name, load_value, position, direction="Global Y"):
        super().__init__(name, wy=load_value)
        self.position = position


class LineLoading(Loads):
    def __init__(self, name, load_value, ele_groups, direction="Global Y"):
        super().__init__(name, load_value, direction)
        print("Line Loading {} created".format(name))

    def get_line_position(self):
        pass

    def get_line_loading_str(self):
        pass


# ---------------------------------------------------------------------------------------------------------------
class PatchLoading(Loads):
    def __init__(self, name, load_value, northing_lines=[], easting_lines=None):
        super().__init__(name, wy=load_value)
        if len(northing_lines) == 1:
            self.northing_lines.append([0, northing_lines])  #
        elif len(northing_lines) > 2:
            self.northing_lines.append([northing_lines[0], northing_lines[-1]])
        else:
            self.northing_lines = northing_lines

        self.easting_lines = easting_lines
        print("Deck patch load {} created".format(name))


class VehicleLoad(PointLoad):
    def __init__(self, name, load_value, position, direction=None):
        super(VehicleLoad, self).__init__(name, load_value)
        # TODO populate class with vehicle models

        self.position
        self.offset
        self.chainage
        self.axles
        self.carriage

    def get_vehicle_load_str(self):
        pass