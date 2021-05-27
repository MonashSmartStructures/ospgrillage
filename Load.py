import pprint
import numpy as np
from collections.abc import Iterable
from scipy import interpolate

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

    def __init__(self, name, Fx=0, Fy=0, Fz=0, Mx=0, My=0, Mz=0, wx=0, wy=0, wz=0, qx=0, qy=0, qz=0, **kwargs):
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
        # Initialise dict for key load points of line UDL and patch load definitions
        self.load_point_data = dict()

        self.load_point_data['x1'] = kwargs.get('x1', None)
        self.load_point_data['y1'] = kwargs.get('y1', 0)
        self.load_point_data['z1'] = kwargs.get('z1', None)
        self.load_point_data['p1'] = kwargs.get('p1', None)

        self.load_point_data['x2'] = kwargs.get('x2', None)
        self.load_point_data['y2'] = kwargs.get('y2', 0)
        self.load_point_data['z2'] = kwargs.get('z2', None)
        self.load_point_data['p2'] = kwargs.get('p2', None)

        self.load_point_data['x3'] = kwargs.get('x3', None)
        self.load_point_data['y3'] = kwargs.get('y3', 0)
        self.load_point_data['z3'] = kwargs.get('z3', None)
        self.load_point_data['p3'] = kwargs.get('p3', None)

        self.load_point_data['x4'] = kwargs.get('x4', None)
        self.load_point_data['y4'] = kwargs.get('y4', 0)
        self.load_point_data['z4'] = kwargs.get('z4', None)
        self.load_point_data['p4'] = kwargs.get('p4', None)

        # init dict
        self.spec = dict()  # dict {node number: {Fx:val, Fy:val, Fz:val, Mx:val, My:val, Mz:val}}
        self.load_counter = 0

    # function to parse incoming keyword


class NodalLoad(Loads):
    def __init__(self, name, node_tag, Fx=0, Fy=0, Fz=0, Mx=0, My=0, Mz=0):
        super().__init__(name, Fx=Fx, Fy=Fy, Fz=Fz, Mx=Mx, My=My, Mz=Mz)
        if not isinstance(node_tag, Iterable):
            node_list = [node_tag]
        else:
            node_list = node_tag
        for nodes in node_list:
            self.spec[nodes] = {"Fx": self.Fx, "Fy": self.Fy, "Fz": self.Fz, "Mx": self.Mx, "My": self.My,
                                "Mz": self.Mz}

    @property
    def node_point(self):
        return self.spec

    @node_point.setter
    def node_point(self, new_node_tag, Fx=0, Fy=0, Fz=0, Mx=0, My=0, Mz=0):
        self.spec.setdefault(new_node_tag, {"Fx": Fx, "Fy": Fy, "Fz": Fz, "Mx": Mx, "My": My, "Mz": Mz})

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
    def __init__(self, name, x, z, y=0, magnitude=0):
        super().__init__(name, x1=x, y1=y, z1=z, Fy=magnitude)

    @staticmethod
    def get_nodal_load_str(node_list, node_val_list):
        # node_list and node_val_list must be a list of same size

        load_str = []
        for count, node in enumerate(node_list):
            load_str.append("ops.load({pt}, *{val})\n".format(pt=node, val=node_val_list[count]))
        return load_str


class LineLoading(Loads):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        print("Line Loading {} created".format(name))

    def get_line_loading_str(self):
        load_str = []
        for node in list(self.grid_line_x):
            load_value = [self.Fx, self.Fy, self.Fz, self.Mx, self.My, self.Mz]
            load_str.append("ops.load({pt}, *{val})\n".format(pt=node, val=load_value))
        return load_str

    def interpolate_udl_magnitude(self, point_coordinate):
        # check if line is defined by either 2 point or 3 point
        if self.load_point_data['x3'] is None:
            x = [self.load_point_data['x1'], self.load_point_data['x2']]
            y = [self.load_point_data['y1'], self.load_point_data['y2']]  # not used but generated here
            z = [self.load_point_data['z1'], self.load_point_data['z2']]
            p = [self.load_point_data['p1'], self.load_point_data['p2']]

            # x[0],z[0] and p[0] shall be reference point for interpolate
            xp = point_coordinate[0]
            yp = point_coordinate[0]
            zp = point_coordinate[0]

            # use parametric equation of line in 3D
            v =[x[1]-x[0],p[1]-p[0],z[1]-z[0]]
            pp = (xp-x[0])/v[0]*v[1]+p[0]

        elif self.load_point_data['x3'] is not None:
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


    def get_vehicle_load_str(self):
        pass


class LoadCase:
    def __init__(self, name):
        self.name = name
        self.load_groups = []

    def add_load_groups(self, *args):
        for loads in args:
            self.load_groups.append(loads)
