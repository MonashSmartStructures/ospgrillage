import pprint
from collections.abc import Iterable
from static import *
from collections import namedtuple


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

        self.load_point_data['x5'] = kwargs.get('x5', None)
        self.load_point_data['y5'] = kwargs.get('y5', 0)
        self.load_point_data['z5'] = kwargs.get('z5', None)
        self.load_point_data['p5'] = kwargs.get('p5', None)

        self.load_point_data['x6'] = kwargs.get('x6', None)
        self.load_point_data['y6'] = kwargs.get('y6', 0)
        self.load_point_data['z6'] = kwargs.get('z6', None)
        self.load_point_data['p6'] = kwargs.get('p6', None)

        self.load_point_data['x7'] = kwargs.get('x7', None)
        self.load_point_data['y7'] = kwargs.get('y7', 0)
        self.load_point_data['z7'] = kwargs.get('z7', None)
        self.load_point_data['p7'] = kwargs.get('p7', None)

        self.load_point_data['x8'] = kwargs.get('x8', None)
        self.load_point_data['y8'] = kwargs.get('y8', 0)
        self.load_point_data['z8'] = kwargs.get('z8', None)
        self.load_point_data['p8'] = kwargs.get('p8', None)

        # init dict
        self.spec = dict()  # dict {node number: {Fx:val, Fy:val, Fz:val, Mx:val, My:val, Mz:val}}
        self.load_counter = 0


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
        # if three points are defined, set line as curved circular line with point 2 (x2,y2,z2) in the centre of curve
        if self.load_point_data['x3'] is not None:  # curve
            self.d = findCircle(x1=self.load_point_data['x1'], y1=self.load_point_data['z1'],
                                x2=self.load_point_data['x2'], y2=self.load_point_data['z2'],
                                x3=self.load_point_data['x3'], y3=self.load_point_data['z3'])
            # return a function variable

        else:  # straight line
            self.m, self.phi = get_slope(
                [self.load_point_data['x1'], self.load_point_data['y1'], self.load_point_data['z1']],
                [self.load_point_data['x2'], self.load_point_data['y2'], self.load_point_data['z2']])
            self.c = get_y_intcp(m=self.m, x=self.load_point_data['x1'], y=self.load_point_data['z1'])

    def interpolate_udl_magnitude(self, point_coordinate):
        # check if line is straight or curve
        if self.load_point_data['x3'] is None:  # straight
            x = [self.load_point_data['x1'], self.load_point_data['x2']]
            y = [self.load_point_data['y1'], self.load_point_data['y2']]  # not used but generated here
            z = [self.load_point_data['z1'], self.load_point_data['z2']]
            p = [self.load_point_data['p1'], self.load_point_data['p2']]

            # x[0],z[0] and p[0] shall be reference point for interpolate
            xp = point_coordinate[0]
            yp = point_coordinate[0]  # not used but generated here
            zp = point_coordinate[0]

            # use parametric equation of line in 3D
            v = [x[1] - x[0], p[1] - p[0], z[1] - z[0]]
            pp = (xp - x[0]) / v[0] * v[1] + p[0]

        elif self.load_point_data['x3'] is not None:  # curve
            # TODO for curved line load
            pass
        return pp


class PatchLoading(Loads):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        # if only four point is define , patch load is a four point straight line quadrilateral
        if self.load_point_data['x5'] is None:
            pass
        # else , 8 point curve sided quadrilateral
        elif self.load_point_data['x8'] is not None:
            pass
        else:
            print("patch load points not valid")
        print("Patch load object created: {} ".format(name))


# ---------------------------------------------------------------------------------------------------------------
class LoadCase:
    def __init__(self, name):
        self.name = name
        self.load_groups = []

    def add_load_groups(self, *args):
        for loads in args:
            self.load_groups.append(loads)


# ---------------------------------------------------------------------------------------------------------------
class ShapeFunction:
    """
    Class for shape functions. Shape functions are presented as class methods. More shape functions can be added herein
    """
    def __init__(self,option):
        self.option = option

    @staticmethod
    def hermite_shape_function(zeta, a):  # using zeta and a as placeholders for normal coor + length of edge element
        # hermite shape functions
        """
        :param zeta: absolute position in x direction
        :param a: absolute position in x direction
        :return: Four terms [N1, N2, N3, N4] of hermite shape function
        .. note::

        """
        N1 = (1 - 3 * zeta ** 2 + 2 * zeta ** 3)
        N2 = (zeta - 2 * zeta ** 2 + zeta ** 3) * a
        N3 = (3 * zeta ** 2 - 2 * zeta ** 3)
        N4 = (-zeta ** 2 + zeta ** 3) * a
        return [N1, N2, N3, N4]

    @staticmethod
    def linear_shape_function(eta, zeta):
        """
        :param zeta: absolute position in x direction
        :param eta: absolute position in z direction
        :return: Four terms [N1, N2, N3, N4] of Linear shape function
        .. note::
            Further validation needed - trial on different bridge models
        """
        N1 = 0.25 * (1 - eta) * (1 - zeta)
        N2 = 0.25 * (1 + eta) * (1 - zeta)
        N3 = 0.25 * (1 + eta) * (1 + zeta)
        N4 = 0.25 * (1 - eta) * (1 + zeta)
        return [N1, N2, N3, N4]


Loadpoint = namedtuple("Point", "x1 y1 z1")
C = Loadpoint(1,2,3)