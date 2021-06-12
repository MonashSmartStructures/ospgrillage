import pprint
from collections.abc import Iterable
from typing import Type
from scipy import interpolate
from static import *
from collections import namedtuple

# named tuple definition
LoadPoint = namedtuple("Point", ["x", "y", "z", "p"])
NodeForces = namedtuple("node_forces", ["Fx", "Fy", "Fz", "Mx", "My", "Mz"])
Line = namedtuple("line", ["m", "c", "phi"])


# ----------------------------------------------------------------------------------------------------------------
# Loading classes
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
        # parse namedtuple of points
        self.load_point_1 = kwargs.get('point1', None)
        self.load_point_2 = kwargs.get('point2', None)
        self.load_point_3 = kwargs.get('point3', None)
        self.load_point_4 = kwargs.get('point4', None)
        self.load_point_5 = kwargs.get('point5', None)
        self.load_point_6 = kwargs.get('point6', None)
        self.load_point_7 = kwargs.get('point7', None)
        self.load_point_8 = kwargs.get('point8', None)

        # init dict
        self.spec = dict()  # dict {node number: {Fx:val, Fy:val, Fz:val, Mx:val, My:val, Mz:val}}
        self.load_counter = 0

    def __str__(self):
        return "LoadCase {} \n".format(self.name) + pprint.pformat(self.spec)


class NodalLoad(Loads):
    def __init__(self, name, node_tag, node_force):
        super().__init__(name, node_tag=node_tag, Fx=node_force.Fx, Fy=node_force.Fy, Fz=node_force.Fz, Mx=node_force.Mx
                         , My=node_force.My, Mz=node_force.Mz)
        if not isinstance(node_tag, Iterable):
            node_list = [node_tag]
        else:
            node_list = node_tag
        for nodes in node_list:
            self.spec[nodes] = {"Fx": self.Fx, "Fy": self.Fy, "Fz": self.Fz, "Mx": self.Mx, "My": self.My,
                                "Mz": self.Mz}

    def get_nodal_load_str(self):
        # get str for ops.load() function.
        load_str = []
        for node in list(self.node_tag):
            load_value = [self.Fx, self.Fy, self.Fz, self.Mx, self.My, self.Mz]
            load_str.append("ops.load({pt}, *{val})\n".format(pt=node, val=load_value))
        return load_str


class PointLoad(Loads):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)

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
        # shape function object
        self.shape_function = ShapeFunction()
        print("Line Loading {} created".format(name))
        # if three points are defined, set line as curved circular line with point 2 (x2,y2,z2) in the centre of curve
        if self.load_point_3 is not None:  # curve
            # findCircle assumes model plane is y = 0, ignores y input, y in this case is a 2D view of x z plane
            self.d = findCircle(x1=self.load_point_1.x, y1=self.load_point_1.z,
                                x2=self.load_point_2.x, y2=self.load_point_2.z,
                                x3=self.load_point_3.x, y3=self.load_point_3.z)
            # return a function variable
            self.line_end_point = self.load_point_3
        else:  # straight line with 2 points
            self.m, self.phi = get_slope(
                [self.load_point_1.x, self.load_point_1.y, self.load_point_1.z],
                [self.load_point_2.x, self.load_point_2.y, self.load_point_2.z])
            self.c = get_y_intcp(m=self.m, x=self.load_point_1.x, y=self.load_point_1.z)
            self.angle = np.arctan(self.m) if self.m is not None else np.pi / 2  # in radian
            self.line_end_point = self.load_point_2
            # namedTuple Line
            self.line_equation = Line(self.m, self.c, self.phi)

    def interpolate_udl_magnitude(self, point_coordinate):
        # check if line is straight or curve
        if self.load_point_3 is None:  # straight line

            # x[0],z[0] and p[0] shall be reference point for interpolate
            xp = point_coordinate[0]
            yp = point_coordinate[0]  # not used but generated here
            zp = point_coordinate[0]

            # use parametric equation of line in 3D
            v = [self.load_point_2.x - self.load_point_1.x, self.load_point_2.p - self.load_point_1.p,
                 self.load_point_2.z - self.load_point_1.z]
            pp = (xp - self.load_point_1.x) / v[0] * v[1] + self.load_point_1.p

        elif self.load_point_3 is not None:  # curve
            # TODO for curved line load
            pass
        return pp

    def get_point_given_distance(self, xbar, point_coordinate):
        # function to return centroid of line load given reference point coordinate (point2) and xbar calculated based
        # on
        z_dis = xbar * np.sin(self.angle)
        x_dis = xbar * np.cos(self.angle)
        # y dis = 0 due to model plane
        new_point = [point_coordinate[0] - x_dis, point_coordinate[1], point_coordinate[2] - z_dis]
        return new_point

    def get_line_segment_given_x(self, x):
        if self.load_point_1.x <= x < self.line_end_point.x or self.load_point_1.x > x >= self.line_end_point.x:
            return line_func(self.line_equation.m, self.line_equation.c, x)

    def get_line_segment_given_z(self, z):
        if self.line_equation.m is None:  # if vertical line
            if self.load_point_1.z <= z < self.line_end_point.z or self.load_point_1.z > z >= self.line_end_point.z:
                return self.load_point_1.x
        else:
            if self.load_point_1.z <= z < self.line_end_point.z or self.load_point_1.z > z >= self.line_end_point.z:
                return inv_line_func(self.line_equation.m, self.line_equation.c, z)


class PatchLoading(Loads):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        a = sort_vertices([self.load_point_2, self.load_point_3, self.load_point_1, self.load_point_4])
        # if only four point is define , patch load is a four point straight line quadrilateral
        if self.load_point_5 is None:
            # create each line
            self.line_1 = LineLoading("Patch load line 1", point1=self.load_point_1, point2=self.load_point_2)
            self.line_2 = LineLoading("Patch load line 2", point1=self.load_point_2, point2=self.load_point_3)
            self.line_3 = LineLoading("Patch load line 3", point1=self.load_point_3, point2=self.load_point_4)
            self.line_4 = LineLoading("Patch load line 4", point1=self.load_point_4, point2=self.load_point_1)

            # create equation of plane from four straight lines

            # create interpolate object f
            p = np.array([[self.load_point_1.p, self.load_point_2.p], [self.load_point_3.p, self.load_point_4.p]])
            x = np.array([[self.load_point_1.x, self.load_point_2.x], [self.load_point_3.x, self.load_point_4.x]])
            z = np.array([[self.load_point_1.z, self.load_point_2.z], [self.load_point_3.z, self.load_point_4.z]])

            # create function to get interpolation of p
            self.patch_mag_interpolate = interpolate.interp2d(x, z, p)

        elif self.load_point_8 is not None:
            # point 1 2 3
            # point 3 4 5
            # point 5 6 7
            # point 7 8 1
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

    def add_compound_load_group(self, *args):
        for loads in args:
            pass

    def add_moving_load(self, *args):

        pass


# ---------------------------------------------------------------------------------------------------------------
class ShapeFunction:
    """
    Class for shape functions. Shape functions are presented as class methods. More shape functions can be added herein
    """

    def __init__(self, option_three_node="triangle_linear", option_four_node="hermite"):
        self.option_three_node = option_three_node
        self.option_four_node = option_four_node

    def get_shape_function(self, option, eta=0, zeta=0):
        if option == "hermite":
            return lambda: self.hermite_shape_function_2d(eta, zeta)
        elif option == "linear":
            return lambda: self.linear_shape_function(eta, zeta)
        elif option == "triangle_linear":
            return lambda: self.linear_triangular

    @staticmethod
    def hermite_shape_function_1d(zeta, a):  # using zeta and a as placeholders for normal coor + length of edge element
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
    def hermite_shape_function_2d(eta, zeta):
        # nodes must be counter clockwise such that n1 = left bottom of relative grid
        # 4  3
        # 1  2
        h1 = 0.25 * (2 - 3 * eta + eta ** 3)
        h2 = 0.25 * (1 - eta - eta ** 2 + eta ** 3)
        h3 = 0.25 * (2 + 3 * eta - eta ** 3)
        h4 = 0.25 * (-1 - eta + eta ** 2 + eta ** 3)
        z1 = 0.25 * (2 - 3 * zeta + zeta ** 3)
        z2 = 0.25 * (1 - zeta - zeta ** 2 + zeta ** 3)
        z3 = 0.25 * (2 + 3 * zeta - zeta ** 3)
        z4 = 0.25 * (-1 - zeta + zeta ** 2 + zeta ** 3)
        Nv = [h1 * z1, h3 * z1, h3 * z3, h1 * z3]
        Nmz = [h2 * z1, h4 * z1, h4 * z3, h2 * z3]
        Nmx = [h1 * z2, h3 * z2, h3 * z4, h1 * z4]
        return Nv, Nmx, Nmz

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

    @staticmethod
    def linear_triangular(x, z, x1, z1, x2, z2, x3, z3):
        # modelling plane = y plane
        ae = 0.5 * ((x2 * z3 - x3 * z2) + (z2 - z3) * x1 + (x3 - x2) * z1)
        a1 = (x2 * z3 - x3 * z2) / (2 * ae)
        b1 = (z2 - z3) / (2 * ae)
        c1 = (x3 - x2) / (2 * ae)

        a2 = (x3 * z1 - x1 * z3) / (2 * ae)
        b2 = (z3 - z1) / (2 * ae)
        c2 = (x1 - x3) / (2 * ae)

        a3 = (x1 * z2 - x2 * z1) / (2 * ae)
        b3 = (z1 - z2) / (2 * ae)
        c3 = (x2 - x1) / (2 * ae)
        N1 = a1 + b1 * x + c1 * z
        N2 = a2 + b2 * x + c2 * z
        N3 = a3 + b3 * x + c3 * z
        return [N1, N2, N3]
