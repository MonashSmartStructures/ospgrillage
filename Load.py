import pprint
import numpy as np
from collections.abc import Iterable

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

    def __init__(self, name, Fx=0, Fy=0, Fz=0, Mx=0, My=0, Mz=0, wx=0, wy=0, wz=0, qx=0, qy=0, qz=0):
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
        self.qx = qx
        self.qy = qy
        self.qz = qz
        # Initialise coordinate properties
        self.x1 = []
        self.x2 = []
        self.x3 = []
        self.x4 = []
        self.x5 = []
        self.x6 = []
        self.x7 = []
        self.x8 = []
        #
        self.y1 = []
        self.y2 = []
        self.y3 = []
        self.y4 = []
        self.y5 = []
        self.y6 = []
        self.y7 = []
        self.y8 = []
        #
        self.z1 = []
        self.z2 = []
        self.z3 = []
        self.z4 = []
        self.z5 = []
        self.z6 = []
        self.z7 = []
        self.z8 = []
        #
        self.p1 = []
        self.p2 = []
        self.p3 = []
        self.p4 = []
        self.p5 = []
        self.p6 = []
        self.p7 = []
        self.p8 = []
        self.spec = dict() # dict {node number: {Fx:val, Fy:val, Fz:val, Mx:val, My:val, Mz:val}}
        self.load_counter = 0


class NodalLoad(Loads):
    def __init__(self, name, node_tag, Fx=0, Fy=0, Fz=0, Mx=0, My=0, Mz=0):
        super().__init__(name, Fx=Fx, Fy=Fy, Fz=Fz, Mx=Mx, My=My, Mz=Mz)
        if not isinstance(node_tag, Iterable):
            node_list = [node_tag]
        else:
            node_list = node_tag
        for nodes in node_list:
            self.spec[nodes] = {"Fx":self.Fx, "Fy":self.Fy, "Fz":self.Fz, "Mx":self.Mx,"My":self.My,"Mz":self.Mz}

    @property
    def node_point(self):
        return self.spec

    @node_point.setter
    def node_point(self, new_node_tag, Fx=0, Fy=0, Fz=0, Mx=0, My=0, Mz=0):
        self.spec.setdefault(new_node_tag, {"Fx":Fx, "Fy":Fy, "Fz":Fz, "Mx":Mx,"My":My,"Mz":Mz})

    def remove_node_point(self, del_node_tag):
        self.spec.pop(del_node_tag, None)

    def get_nodal_load_str(self):
        # get str for ops.load() function.
        load_str = []
        for node in list(self.node_tag):
            load_value = [self.Fx, self.Fy, self.Fz, self.Mx, self.My, self.Mz]
            load_str.append("ops.load({pt}, *{val})\n".format(pt=node, val=load_value))
        return load_str


class PointLoad(Loads):
    def __init__(self, name, position, magnitude=0):
        super().__init__(name, wy=magnitude)
        self.position = position


class LineLoading(Loads):
    def __init__(self, name, const_magnitude=0, pt_list=[], pt_mag_list=[]):
        super().__init__(name, wy=const_magnitude)
        print("Line Loading {} created".format(name))
        self.pt_list = pt_list
        self.pt_mag_list = pt_mag_list

    def get_line_loading_str(self):
        load_str = []
        for node in list(self.grid_line_x):
            load_value = [self.Fx, self.Fy, self.Fz, self.Mx, self.My, self.Mz]
            load_str.append("ops.load({pt}, *{val})\n".format(pt=node, val=load_value))
        return load_str

    def interpolate_udl_magnitude(self, node_coordinate):
        # TODO
        pass


# ---------------------------------------------------------------------------------------------------------------
class PatchLoading(Loads):
    def __init__(self, name):
        super().__init__(name)




    def set_straight_side_patch_load(self, x1=0):
        pass


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


class LoadCase:
    def __init__(self, name):
        self.name = name
        self.load_groups = []

    def add_load_groups(self, *args):
        for loads in args:
            self.load_groups.append(loads)
