# -*- coding: utf-8 -*-
"""
Load module consist of class/methods which wraps ```OpenSeesPy``` to create and run load analysis. First part of the module
comprise the user interface functions. Following are the classes of various load types, compound load, load case,
moving load and moving load path.
"""

import pprint
from collections import namedtuple
from collections.abc import Iterable
from copy import deepcopy
from typing import Union

from scipy import interpolate

from ospgrillage.mesh import *


def create_load_vertex(**kwargs):
    """
    User interface function to create a load vertex. Load vertices are used in defining loads. For example,
    a point load consist of a single load vertex while a patch load is defined using four load vertices for each of
    its corner.

    :param kwargs: Keyword arg, see below.

    :keyword:

    * x (`float` or `int`): Value of x coordinate
    * y (`float` or `int`): Value of y coordinate. Default is model plane y = 0
    * z (`float` or `int`): Value of z coordinate
    * p (`float` or `int`): Magnitude of vertical load in y direction.

    :returns: namedTuple LoadPoint(x,y,z,p)

    :except: ValueError if missing one or more keyword arguments.

    """
    x = kwargs.get("x", None)
    y = kwargs.get("y", 0)
    z = kwargs.get("z", None)
    p = kwargs.get("p", None)

    if not any([x is None, y is None, z is None, p is None]):
        return LoadPoint(x, y, z, p)
    else:
        raise ValueError("Missing one or more keyword arguments for x=, y=, z=, or p=")


def create_point(**kwargs):
    """
    User interface function to create a Point namedTuple.
    :param kwargs: See below
    :keyword:

    * x (`float` or `int`): Value of x coordinate
    * y (`float` or `int`): Value of y coordinate. Default is y = 0
    * z (`float` or `int`): Value of z coordinate

    :return: Point(x,y,z) namedTuple
    """
    x = kwargs.get("x", None)
    y = kwargs.get("y", 0)
    z = kwargs.get("z", None)

    if not any(
        [
            x is None,
            z is None,
        ]
    ):
        return Point(x, y, z)
    else:
        raise ValueError("Missing one or more keyword arguments for x=, z=, ")


def create_load_case(**kwargs):
    """
    User interface function to create LoadCase objects. Following this function, users
    are required add loads to LoadCase object via :func:`~ospgrillage.load.LoadCase.add_load`.

    :keyword:
    * name(`str`): Name string of Load case object

    :returns: :class:`~ospgrillage.load.LoadCase` object
    """
    return LoadCase(**kwargs)


def create_compound_load(**kwargs):
    """
    User interface function to create CompoundLoad object. Following this function users are required to
    add loads to object via :func:`~ospgrillage.load.CompoundLoad.add_load`.

    :returns: :class:`~ospgrillage.load.CompoundLoad`
    """
    return CompoundLoad(**kwargs)


def create_load(**kwargs):
    """
    User interface function to create load types.

    :keyword:

    * type(`str`): type of load. Choose either ["point","line","patch","nodal"]
    * point# (`LoadPoint` namedTuple): LoadPoint for load type in global coordinate. Note different load type requires a
    different minimum LoadPoint.
    * local_load_point_# (`LoadPoint` namedTuple): LoadPoint for load type in local coordinate. Note different load type
    requires a different minimum LoadPoint.

    :return: PointLoad, LineLoading, PatchLoading, or NodalForces
    """
    type = kwargs.get("loadtype", None)

    vertice_list = []
    for i in range(4):
        vertice_string = f"point{i + 1}"
        vertice_list.append(kwargs.get(vertice_string, None))

    vertice_count = sum([1 for vertex in vertice_list if vertex])

    if vertice_count == 1:
        return PointLoad(**kwargs)
    elif vertice_count == 2:
        return LineLoading(**kwargs)
    elif vertice_count >= 4:
        return PatchLoading(**kwargs)
    elif type == "nodal":
        fx = kwargs.get("Fx", 0)
        fy = kwargs.get("Fy", 0)
        fz = kwargs.get("Fz", 0)
        mx = kwargs.get("Mx", 0)
        my = kwargs.get("My", 0)
        mz = kwargs.get("Mz", 0)
        tag = kwargs.get("node_tag", None)
        name = kwargs.get("name", None)
        if any(
            [fx is None, fy is None, fz is None, mx is None, my is None, mz is None]
        ):
            raise ValueError(
                "Missing arguments for nodal force definition : Hint check if all required keywords are given"
            )
        force = NodeForces(fx, fy, fz, mx, my, mz)
        return NodalLoad(name=name, node_tag=tag, node_force=force)
    else:
        raise TypeError(
            "load type not specified. hint: specify kwarg type= for create_load()"
        )


def create_moving_load(**kwargs):
    """
    User interface function to create Moving Load object. Following this function, users are required to:

    *. Set a common path to object via :func:`~ospgrillage.load.MovingLoad.set_path`
    *. Add loads to object via :func:`~ospgrillage.load.MovingLoad.add_load`

    :return: :class:`~ospgrillage.load.MovingLoad` object

    :keyword:

    * **common_path**(`Path`): Path object for all load groups added to the Moving load object to traverse
    * **global_increment**(`float` or `int`): Number of increments to discretize Path object. This keyword is only used in
      advance usage where Moving Load contains multiple load groups each with unique path objects.

    """
    return MovingLoad(**kwargs)


def create_moving_path(**kwargs):
    """
    User interface function to create Path object for moving load.

    :keyword:

    * start_point (`Point`): Start point of path
    * end_point (`Point`): End point of path
    * increments (`int`): Increment of path steps. Default is 50
    * mid_point (`Point`): Default = None

    :returns: :class:`~ospgrillage.load.Path` object
    """
    return Path(**kwargs)


# named tuple definition
LoadPoint = namedtuple("Point", ["x", "y", "z", "p"])
NodeForces = namedtuple("node_forces", ["Fx", "Fy", "Fz", "Mx", "My", "Mz"])
Line = namedtuple("line", ["m", "c", "phi"])


# ----------------------------------------------------------------------------------------------------------------
# Loading classes
# ---------------------------------------------------------------------------------------------------------------
class Loads:
    """
    Base class for Point, Line , and Patch loads
    """

    load_point_1: LoadPoint
    load_point_2: LoadPoint
    load_point_3: LoadPoint
    load_point_4: LoadPoint
    load_point_5: LoadPoint
    load_point_6: LoadPoint
    load_point_7: LoadPoint
    load_point_8: LoadPoint

    def __init__(self, **kwargs):
        """

        :param name: Name of load
        :param Fx: Axis force in x axis
        :param Fy: Axis force in y axis
        :param Fz: Axis force in z axis
        :param Mx: Moment about x axis
        :param My: Moment about y axis
        :param Mz: Moment about z axis
        :param kwargs: see below

        :keyword:

        * **point1**, **point2**, ..., **point8** : (LoadPoint namedTuple) coordinate points with force magnitude describing the load type
        * **localpoint1**, **localpoint2**, ..., **localpoint8**: (LoadPoint namedTuple) local coordinate points with force magnitude describing the load type


        """
        #
        self.name = kwargs.get("name", None)

        # Initialise dict for key load points of line UDL and patch load definitions
        self.load_point_data = dict()
        # parse namedtuple of global coordinates
        self.load_point_1 = kwargs.get("point1", None)
        self.load_point_2 = kwargs.get("point2", None)
        self.load_point_3 = kwargs.get("point3", None)
        self.load_point_4 = kwargs.get("point4", None)
        self.load_point_5 = kwargs.get("point5", None)
        self.load_point_6 = kwargs.get("point6", None)
        self.load_point_7 = kwargs.get("point7", None)
        self.load_point_8 = kwargs.get("point8", None)

        # shape function
        self.shape_function = kwargs.get("shape_function", "linear")
        # check if user skipped point 1 and defined point1 as point 2 instead
        if all([self.load_point_1 is None, self.load_point_2 is not None]):
            raise Exception("Load point 1 is not defined")

        # list of load points tuple
        self.point_list = [
            self.load_point_1,
            self.load_point_2,
            self.load_point_3,
            self.load_point_4,
            self.load_point_5,
            self.load_point_6,
            self.load_point_7,
            self.load_point_8,
        ]
        # self.local_point_list = [self.local_load_point_1, self.local_load_point_2, self.local_load_point_3,
        #                          self.local_load_point_4, self.local_load_point_5, self.local_load_point_6,
        #                          self.local_load_point_7, self.local_load_point_8]
        # var for compound load group (handled by LoadCase class when creating compound groups)
        self.compound_dist_x = 0  # local coordinate system
        self.compound_dist_z = 0  # local coordinate system
        self.ref_point = None  # local coordinate system
        self.compound_group = None  # group number access by LoadCase class to move load group if any path is defined
        # spec dict
        self.spec = dict(
            name=self.name, global_points=self.point_list, ref_point=self.ref_point
        )  # dict {node number: {Fx:val, Fy:val, Fz:val, Mx:val, My:val, Mz:val}}
        self.load_counter = 0  # counter for compound load

    # function called by Moving load module to move the load group
    def move_load(self, ref_point: Point):
        """
        Function to move each load point of load type by a reference coordinate. This function is handled by OpsGrillage
        :param ref_point: coordinate to be moved
        :type ref_point: namedTuple Point(x,y,z)
        :return: increment each load point by +x, +y, +z where (x,y,z) is the coordinate prescribed by ref_point
        """
        if any(self.point_list):
            self.load_point_1 = (
                self.load_point_1._replace(
                    x=self.load_point_1.x + ref_point.x,
                    z=self.load_point_1.z + ref_point.z,
                )
                if self.load_point_1 is not None
                else self.load_point_1
            )
            self.load_point_2 = (
                self.load_point_2._replace(
                    x=self.load_point_2.x + ref_point.x,
                    z=self.load_point_2.z + ref_point.z,
                )
                if self.load_point_2 is not None
                else self.load_point_2
            )
            self.load_point_3 = (
                self.load_point_3._replace(
                    x=self.load_point_3.x + ref_point.x,
                    z=self.load_point_3.z + ref_point.z,
                )
                if self.load_point_3 is not None
                else self.load_point_3
            )
            self.load_point_4 = (
                self.load_point_4._replace(
                    x=self.load_point_4.x + ref_point.x,
                    z=self.load_point_4.z + ref_point.z,
                )
                if self.load_point_4 is not None
                else self.load_point_4
            )
            self.load_point_5 = (
                self.load_point_5._replace(
                    x=self.load_point_5.x + ref_point.x,
                    z=self.load_point_5.z + ref_point.z,
                )
                if self.load_point_5 is not None
                else self.load_point_5
            )
            self.load_point_6 = (
                self.load_point_6._replace(
                    x=self.load_point_6.x + ref_point.x,
                    z=self.load_point_6.z + ref_point.z,
                )
                if self.load_point_6 is not None
                else self.load_point_6
            )
            self.load_point_7 = (
                self.load_point_7._replace(
                    x=self.load_point_7.x + ref_point.x,
                    z=self.load_point_7.z + ref_point.z,
                )
                if self.load_point_7 is not None
                else self.load_point_7
            )
            self.load_point_8 = (
                self.load_point_8._replace(
                    x=self.load_point_8.x + ref_point.x,
                    z=self.load_point_8.z + ref_point.z,
                )
                if self.load_point_8 is not None
                else self.load_point_8
            )

    def apply_load_factor(self, factor=1):
        """
        Function to apply load factor to each load point's p value (vertical P force)
        """
        self.load_point_1 = (
            self.load_point_1._replace(p=factor * self.load_point_1.p)
            if self.load_point_1 is not None
            else self.load_point_1
        )
        self.load_point_2 = (
            self.load_point_2._replace(p=factor * self.load_point_2.p)
            if self.load_point_2 is not None
            else self.load_point_2
        )
        self.load_point_3 = (
            self.load_point_3._replace(p=factor * self.load_point_3.p)
            if self.load_point_3 is not None
            else self.load_point_3
        )
        self.load_point_4 = (
            self.load_point_4._replace(p=factor * self.load_point_4.p)
            if self.load_point_4 is not None
            else self.load_point_4
        )
        self.load_point_5 = (
            self.load_point_5._replace(p=factor * self.load_point_5.p)
            if self.load_point_5 is not None
            else self.load_point_5
        )
        self.load_point_6 = (
            self.load_point_6._replace(p=factor * self.load_point_6.p)
            if self.load_point_6 is not None
            else self.load_point_6
        )
        self.load_point_7 = (
            self.load_point_7._replace(p=factor * self.load_point_7.p)
            if self.load_point_7 is not None
            else self.load_point_7
        )
        self.load_point_8 = (
            self.load_point_8._replace(p=factor * self.load_point_8.p)
            if self.load_point_8 is not None
            else self.load_point_8
        )

    def get_magnitude(self):
        # TODO
        magnitude = []
        for load_point in self.point_list:
            magnitude.append(load_point.p)

        return magnitude

    def __str__(self):
        return "Load object {} \n".format(self.name) + pprint.pformat(self.spec)


class NodalLoad(Loads):
    """
    Main class for nodal load. Derived from Loads base class
    """

    def __init__(self, node_tag, node_force, name=None):
        """
        Nodal load takes a node tag and namedtuple NodalForce(Fx,Fy,Fz,Mx,My,Mz) as input.

        :param name: Name of load
        :type name: str
        :param node_tag: Node tag of grillage model for nodal load to be applied
        :type node_tag: int
        :param node_force: Named tuple of node forces
        :type node_force: NodalForces(Fx,Fy,Fz,Mx,My,Mz)
        """
        super().__init__(name=name, node_tag=node_tag)
        self.Fx = node_force.Fx
        self.Fy = node_force.Fy
        self.Fz = node_force.Fz
        self.Mx = node_force.Mx
        self.My = node_force.My
        self.Mz = node_force.Mz
        self.node_tag = node_tag
        if not isinstance(node_tag, Iterable):
            node_list = [node_tag]
        else:
            node_list = node_tag
        for nodes in node_list:
            self.spec[nodes] = {
                "Fx": self.Fx,
                "Fy": self.Fy,
                "Fz": self.Fz,
                "Mx": self.Mx,
                "My": self.My,
                "Mz": self.Mz,
            }

    def get_nodal_load_str(self):
        """
        Function to return ops.load() command for nodal load.
        """
        # get str for ops.load() function.
        load_value = [self.Fx, self.Fy, self.Fz, self.Mx, self.My, self.Mz]
        load_str = "ops.load({pt}, *{val})\n".format(pt=self.node_tag, val=load_value)
        return load_str


class PointLoad(Loads):
    """
    Class for Point loads. Derived from based :py:class:`Loads` class
    """

    def __init__(self, **kwargs):
        """

        :param name:
        :param kwargs:
        """
        super().__init__(**kwargs)


class LineLoading(Loads):
    """
    Class for line loading. Derived from based Loads class
    """

    def __init__(self, **kwargs):
        """

        :param name:
        :param kwargs:
        """
        super().__init__(**kwargs)

        self.long_beam_ele_load_flag = kwargs.get("long_beam_element_load", False)
        self.trans_beam_ele_load_flag = kwargs.get("trans_beam_element_load", False)

        # if three points are defined, set line as curved circular line with point 2 (x2,y2,z2) in the centre of
        # curve
        if self.load_point_3 is not None:  # curve
            # findCircle assumes model plane is y = 0, ignores y input, y in this case is a 2D view of x z plane
            self.d = find_circle(
                x1=self.load_point_1.x,
                y1=self.load_point_1.z,
                x2=self.load_point_2.x,
                y2=self.load_point_2.z,
                x3=self.load_point_3.x,
                y3=self.load_point_3.z,
            )
            # return a function variable
            self.line_end_point = self.load_point_3
        else:  # straight line with 2 points
            self.m, self.phi = get_slope(
                [self.load_point_1.x, self.load_point_1.y, self.load_point_1.z],
                [self.load_point_2.x, self.load_point_2.y, self.load_point_2.z],
            )
            self.c = get_y_intcp(m=self.m, x=self.load_point_1.x, y=self.load_point_1.z)
            self.angle = (
                np.arctan(self.m) if self.m is not None else np.pi / 2
            )  # in radian
            self.line_end_point = self.load_point_2
            # namedTuple Line
            self.line_equation = Line(self.m, self.c, self.phi)
        # else:
        #     raise ValueError("Invalid load points for line load {}".format(self.name))

    def interpolate_udl_magnitude(self, point_coordinate):
        #   """
        #   Function to interpolate magnitude of load point between two load points in a line segment.
        #
        #   Example illustration: Function returns p @ [x y z]
        #
        #   p(loadpoint1)_____p(x=,y,z)_______ p(loadpoint2)
        #   ||||||||||||||||||||||||||||||||||||||||||||||      Line loading
        #   ||||||||||||||||||||||||||||||||||||||||||||||
        # __________________________________________________________
        #
        #   :param point_coordinate: coordinate list [x,y,z]
        #   :type point_coordinate: list
        #   :return: point force (udl) magnitude at coordinate
        #   """
        # input: point_coordinate list of [x,y,z]
        pp = None
        # check if line is straight or curve
        if self.load_point_3 is None:  # straight line
            # x[0],z[0] and p[0] shall be reference point for interpolate
            xp = point_coordinate[0]
            yp = point_coordinate[0]  # not used but generated here
            zp = point_coordinate[0]

            # use parametric equation of line in 3D
            v = [
                self.load_point_2.x - self.load_point_1.x,
                self.load_point_2.p - self.load_point_1.p,
                self.load_point_2.z - self.load_point_1.z,
            ]
            if v[0] == 0 and self.load_point_2.x == self.load_point_1.x:
                pp = (zp - self.load_point_1.z) / v[2] * v[1] + self.load_point_1.p
            else:
                pp = (xp - self.load_point_1.x) / v[0] * v[1] + self.load_point_1.p

        elif self.load_point_3 is not None:  # curve
            # TODO for curved line load
            pass
        return pp

    def get_point_given_distance(self, xbar, point_coordinate):
        # """
        # Function to return
        # :param xbar: distance
        # :type xbar: float
        # :param point_coordinate: coordinates list [x,y,z]
        # :type point_coordinate: list
        # :return new_point: coordinate list [x,y,z] shifted by distance
        # :type new_point: list
        # """
        # function to return centroid of line load given reference point coordinate (point2) and xbar calculated based
        # on
        z_dis = xbar * np.sin(self.angle)
        x_dis = xbar * np.cos(self.angle)
        # y dis = 0 due to model plane
        new_point = [
            point_coordinate[0] - x_dis,
            point_coordinate[1],
            point_coordinate[2] - z_dis,
        ]
        return new_point

    def get_line_segment_given_x(self, x):
        # """
        # Function to return straight line equation for line segment (in OpsGrillage case, segment bounded by grid) given x point
        # :param x: value of x input for line equation
        # :type x: float
        # :return: solution of line equation (i.e. y = mx + c)
        # """
        if self.line_equation.m is None:  # if vertical line
            pass
        else:
            if (
                self.load_point_1.x <= x <= self.line_end_point.x
                or self.load_point_1.x >= x >= self.line_end_point.x
            ):
                return line_func(self.line_equation.m, self.line_equation.c, x)

    def get_line_segment_given_z(self, z):
        if self.line_equation.m is None:  # if vertical line
            if (
                self.load_point_1.z <= z <= self.line_end_point.z
                or self.load_point_1.z >= z >= self.line_end_point.z
            ):
                return self.load_point_1.x
        else:
            if (
                self.load_point_1.z <= z <= self.line_end_point.z
                or self.load_point_1.z >= z >= self.line_end_point.z
            ):
                return inv_line_func(self.line_equation.m, self.line_equation.c, z)


class PatchLoading(Loads):
    """
    Main class for Patch loads. Derived from base Loads class.

    Patch load can take up to 8 load points. By default requires at least 4 load point for patch (quadrilateral)
    """

    def __init__(self, **kwargs):
        """

        :param name:
        :param kwargs:
        """
        super().__init__(**kwargs)
        if not all(v is None for v in self.point_list):
            a, _ = sort_vertices(
                [
                    self.load_point_2,
                    self.load_point_3,
                    self.load_point_1,
                    self.load_point_4,
                ]
            )
            match = [
                self.load_point_1,
                self.load_point_2,
                self.load_point_3,
                self.load_point_4,
            ]
            # if len(self.point_list) < 4:
            #     raise ValueError("invalid number of vertices. Hint:  either 4 or 8 is accepted for patch")

        else:
            raise ValueError(
                "vertices missing.hint: patch load must have either 4  or 8 vertices  "
            )
        if a != match:
            raise Exception(
                "vertices of patch load gives invalid patch layout: hint: make sure vertices are in counter"
                "clockwise order with first point (load_point_1) being the bottom left vertice of the "
                "patch load"
            )
        # get patch min dimension
        self.patch_min_dim = None  # instantiate
        # procedure to define lines of patch
        self._define_patch_edge_lines()

    def _define_patch_edge_lines(self):
        # create each line
        self.line_1 = LineLoading(point1=self.load_point_1, point2=self.load_point_2)
        self.line_2 = LineLoading(point1=self.load_point_2, point2=self.load_point_3)
        self.line_3 = LineLoading(point1=self.load_point_3, point2=self.load_point_4)

        # if only four point is define , patch load is a four point straight line quadrilateral
        if self.load_point_5 is None:
            # create fourth line
            self.line_4 = LineLoading(
                point1=self.load_point_4, point2=self.load_point_1
            )

            # create equation of plane from four straight lines

            # create interpolate object f
            p = np.array(
                [
                    [self.load_point_1.p, self.load_point_2.p],
                    [self.load_point_3.p, self.load_point_4.p],
                ]
            )
            x = np.array(
                [
                    [self.load_point_1.x, self.load_point_2.x],
                    [self.load_point_3.x, self.load_point_4.x],
                ]
            )
            z = np.array(
                [
                    [self.load_point_1.z, self.load_point_2.z],
                    [self.load_point_3.z, self.load_point_4.z],
                ]
            )

            # create function to get interpolation of p
            self.patch_mag_interpolate = interpolate.interp2d(x, z, p)
            mod_list = [ls for ls in self.point_list if ls is not None]
            self.patch_min_dim = min(
                [
                    get_distance(p1, p2)
                    for (p1, p2) in zip(mod_list, mod_list[1:] + [mod_list[0]])
                    if all([p1 is not None, p2 is not None])
                ]
            )
        elif self.load_point_4 is None:
            # update line 3
            self.line_3 = LineLoading(
                point1=self.load_point_3, point2=self.load_point_1
            )

            # TODO create equation of plane from 3 points
            # create interpolate object f
            p = np.array(
                [
                    [self.load_point_1.p, self.load_point_2.p],
                    [self.load_point_3.p, self.load_point_4.p],
                ]
            )
            x = np.array(
                [
                    [self.load_point_1.x, self.load_point_2.x],
                    [self.load_point_3.x, self.load_point_4.x],
                ]
            )
            z = np.array(
                [
                    [self.load_point_1.z, self.load_point_2.z],
                    [self.load_point_3.z, self.load_point_4.z],
                ]
            )

            # create function to get interpolation of p
            self.patch_mag_interpolate = interpolate.interp2d(x, z, p)
            mod_list = [ls for ls in self.point_list if ls is not None]
            self.patch_min_dim = min(
                [
                    get_distance(p1, p2)
                    for (p1, p2) in zip(mod_list, mod_list[1:] + [mod_list[0]])
                    if all([p1 is not None, p2 is not None])
                ]
            )
        elif self.load_point_8 is not None:
            # TODO
            # point 1 2 3
            # point 3 4 5
            # point 5 6 7
            # point 7 8 1
            pass

        else:
            raise ValueError(
                "Patch load points for patch load {} not valid".format(self.name)
            )


# ---------------------------------------------------------------------------------------------------------------
class CompoundLoad:
    """
    Main class for Compound load definition.

    When a Load object is pass as an input, CompoundLoad treats the initial positions (load_points) of the Load classes
    as local coordinates. Then CompoundLoad sets the loads "in-place" of the local coordinate. If class input local_coord
    is given, CompoundLoad replaces the coordinates of the initial load points (retaining the magnitude of load points)

    When set_global_coord() function is called, CompoundLoad sets the input global coordinate as the new centroid of the
    compounded load groups. This is done by shifting each local coordinate load point in all load groups under
    CompoundLoad by x (global) and z (global).

    Here are a few relationships between CompoundLoad and other classes

    * CompoundLoad object can have Loads class and its inheritances (Line, Point, Patch)
    * CompoundLoad handles functions of Load classes (e.g. move_load)

    """

    def __init__(self, name):
        self.name = name
        self.compound_load_obj_list = []
        self.local_coord_list = []
        self.centroid = Point(0, 0, 0)  # named tuple Point
        self.global_coord = self.centroid

    def add_load(self, load_obj: Loads):
        """
        Function to add load object to compound load group. If a local_coord parameter is given, this new local_coord overwrites the coordinates (either local or global) of the load object.

        ..note:
            If load object is defined using local coordinate and local_coord is None, its default local coord precedes.

        :param load_obj: Load object
        :type load_obj: PointLoad,LineLoading,PatchLoading
        :param local_coord: Local coordinate of load object
        :type local_coord: Point namedTuple

        """
        # update the load obj to be part of compound load by first
        # shifting all load points relative to centroid of defined load class
        # then shifting centroid and load_points relative to A Local Coordinate system
        load_obj_copy = deepcopy(load_obj)
        # check if input load object is valid (local vs global coordinate) system.
        # If local load + local_coord input, raise ValueError
        # if local_coord is not None and any(load_obj_copy.local_point_list):
        #     raise ValueError("{} was defined in local coordinate space. However a `load_coord=` parameter"
        #                      "exist for this load when creating compound load "
        #                      "Hint: Loads defined in local coordinate space does not "
        #                      "need another "
        #                      "`local_coord=` parameter".format(load_obj_copy.name))
        # if global load + local_coord input, raise Value error
        # if local_coord is not None and not any(load_obj_copy.local_point_list):
        #    raise ValueError("{} was defined in global coordinate. However a local_coord= parameter exist for this load"
        #                     ".Hint: Load defined in global coordinate space does not need `local_coord=` "
        #                     "parameter".format(load_obj_copy.name))
        #    pass
        # inputs for compound load are valid, proceed to set compound load
        # if local coord is passed in,
        # if local_coord is not None:  # else points defined as global already
        #     load_obj_copy.form_compound_load(compound_dist_x=local_coord.x, compound_dist_z=local_coord.z)
        #     # then shift load obj relative to global coord (this is the coord of the model) default is 0,0,0 if not set
        #     # by user
        #     load_obj_copy.move_load(self.global_coord)

        self.compound_load_obj_list.append(
            load_obj_copy
        )  # after update, append to list
        # self.local_coord_list.append(local_coord)

    def set_global_coord(self, global_coord: Point):
        """
        Function to set global coordinate of the compound load with respect to global coordinate system of grillage model.
        The global coordinate is set to all local load points (i.e. it adds the global coord x y z to each local coord)

        :param global_coord: Value of x y z (global coord) to offset the basic coordinate system
        :type global_coord: Point namedTuple
        """
        # overwrite global coordinate
        if global_coord != self.global_coord:
            self.global_coord = global_coord
            # loop each load type in compound load and shift by global_coord
            append_load_list = []
            # once overwritten, update loadpoints in each load obj of compound load by global_coord
            for loads in self.compound_load_obj_list:
                loads.move_load(
                    global_coord
                )  # shift load objs using Load class method move_load()
                append_load_list.append(
                    loads
                )  # append loads which have been moved to new list and
            self.compound_load_obj_list = (
                append_load_list  # overwrite it to class variable
            )


# ---------------------------------------------------------------------------------------------------------------
class LoadCase:
    """
    Main class for load cases. Each load case holds information about:
    #. Load object types (point line patch or combination i.e. compound load)
    #. load case ops load command line - this is generated by ops-grillage class method (add_load_case()) and updated to LoadCase class object.
    #. Load factor - all load objects within a Load case are link to one same load factor


    Here are a few relationships between LoadCase and other classes

    * MovingLoad class creates a series of load case representing the movement of load objects in each load case.
    * Load combination takes in several LoadCase class instance with varied load factors into a single analysis
    * Analysis class handles the ops. commands required for
    * OpsGrillage class takes in load case and updates the variable 'load_command_list' after distributing loads within the LoadCase class to nodes/elements of the Mesh in OpsGrillage.
    * LoadCase class can have Load objects or CompoundLoad class object

    """

    def __init__(self, name):
        """
        :param name: str of load case name
        """
        self.name = name
        self.load_groups = []
        self.position = None
        # preset load factor for
        self.load_command_list = []

    def add_load(self, load_obj: Union[Loads, CompoundLoad], **kwargs):
        """
        Function to add load objects to LoadCase

        :param load_obj: Load or Compound load object
        :param kwargs: keyword arguments
        :keyword:

        * global_coord_of_load_obj (`Point` namedTuple): if load objects are defined in local coordinate, this parameter
          is required to set the origin of local coordinate of load groups onto the global coordinate of the grillage

        """
        load_dict = dict()
        load_dict.setdefault(
            "load", deepcopy(load_obj)
        )  # create copy of object instance
        # check if load_obj's load points are local points, if True, check if kwargs global coord is provided
        global_coord_of_load_obj: Point = kwargs.get("global_coord_of_load_obj", None)

        load_factor = kwargs.get("load_factor", 1)
        load_dict.setdefault("factor", load_factor)
        self.load_groups.append(load_dict)

    # function for if load groups are to change its ref position due to movement / traversing loads
    # warning : this function is only to be handled by MovingLoad class
    def move_load_group(self, ref_point: Point):
        self.position = ref_point
        for load_dict in self.load_groups:
            load_obj = load_dict.get("load")
            if isinstance(load_obj, CompoundLoad):
                for ind_load_obj in load_obj.compound_load_obj_list:
                    ind_load_obj.move_load(self.position)
            else:
                load_obj.move_load(self.position)


# ---------------------------------------------------------------------------------------------------------------
class MovingLoad:
    """
    Main class of moving load case. MovingLoad class parses and creates multiple loadcase object corresponding to
    traversing the input load groups - be it compound or single. Moving load is able to set various path (defined by
    Path class object) to individual load groups.

    """

    def __init__(self, name, **kwargs):
        """

        :param name: Name string of moving load
        :keyword:
        * common_path (`Path`): Path object specifying the common path for all loads defined in moving load to traverse
        * global_increment(`int`): Number of increments to discretize Path object.

        .. note::
            global_increment argument is used in advance moving load analysis, where a moving load object attributes
            each assigned load type with a corresponding unique Path object (which can differ between different paths).
        """
        self.name = name
        self.load_list = []
        self.load_case_dict_list = []  # Variable to access
        self.moving_load_case = (
            []
        )  # Variable recording all created load case for all load group's respective path
        self.static_load_case = []
        # get kwargs
        self.common_path = kwargs.get("common_path", None)
        self.global_increment = kwargs.get("global_increment", None)  # for advance use
        self.parse = False  # flag for if query option is available
        self.incremental_name = None  # init variable of query method

    def set_path(self, path_obj):
        """
        Function to assign/modify the common path variable with a new Path object.
        All loads added later to Moving load object will traverse the same common path object.

        :param path_obj: Path object to specify common path variable.
        :type path_obj: Path

        """
        if self.global_increment is not None:
            raise ValueError(
                "Option for Basic use - common path defined for all added loads in MovingLoad however"
                "a global increment parameter was defined. Hint: Remove global_increment= on creating"
                "moving load object"
            )
        # else, valid input for setting a basic moving load - proceed setting common path variable
        self.common_path = path_obj

    def add_load(self, load_obj: Union[Loads, CompoundLoad], path_obj=None):
        """
        Function to set a load type (Loads class object) with its path (Path class object). Function accepts compound load (Compound load class) as a load input, which in turn sets the path object to all loads within the compound
        load group.

        :param load_obj: Loads class object , or Compound load object
        :param path_obj: Path class object - this is for advance use, where users specify unique path object for each load within the moving load object.

        """
        # if no path object is added, set empty list to path_obj. The load group will be treated as a static load
        # present throughout the movement of other load groups (added to the series of moving load case)

        load_pair_path = dict()
        load_pair_path.setdefault("load", load_obj)
        # check if basic moving load case
        if self.common_path and self.global_increment is None:
            load_pair_path.setdefault(
                "path", self.common_path.get_path_points()
            )  # .get_path_points() class method of Path class
        elif (
            self.global_increment
        ):  # advance use - where each object has individual path
            load_pair_path.setdefault(
                "path", path_obj.get_custom_path_points(self.global_increment)
            )
        else:  # error, no global statement was provided,
            raise ValueError(
                "No set_path() for moving load {}: Hint run set_path() before add_loads()".format(
                    self.name
                )
            )
        self.load_case_dict_list.append(load_pair_path)

    # function to create incremental load cases for each step of the moving loads. Function handled by OspGrillage
    def parse_moving_load_cases(self):
        # loop through all load-path pairs and identify static loads
        for load_pair_dict in self.load_case_dict_list:
            if not load_pair_dict["path"]:  # empty path, load is static
                self.static_load_case.append(load_pair_dict["load"])

        # create load case obj for each step in the move
        for load_pair_dict in self.load_case_dict_list:
            path_list = load_pair_dict["path"]  # extract path_list of load object
            load_obj = load_pair_dict["load"]
            # loop to create a load case for each increment of the path obj
            load_case_list = []
            for steps in path_list:
                load_step_lc = LoadCase(
                    name="{} at global position [{:.2f},{:.2f},{:.2f}]".format(
                        self.name, steps[0], steps[1], steps[2]
                    )
                )  # _lc in name stands for load case
                load_obj_copy = deepcopy(
                    load_obj
                )  # Use deepcopy module to copy instance of load
                load_step_lc.add_load(
                    load_obj_copy
                )  # and add load to newly created load case
                # add entries of static load to load groups
                step_point = Point(
                    steps[0], steps[1], steps[2]
                )  # convert increment position into Point tuple
                load_step_lc.move_load_group(
                    step_point
                )  # increment the load groups by step point
                # static load not used
                for (
                    static_load
                ) in (
                    self.static_load_case
                ):  # add static load portions to each incremental load case
                    static_load_copy = deepcopy(static_load)
                    load_step_lc.add_load(static_load_copy)
                load_case_list.append(load_step_lc)
            self.moving_load_case.append(load_case_list)
            self.parse = True
        return self.moving_load_case

    def query(self, incremental_lc_name, **kwargs):
        """
        Function to query properties of moving load

        :param incremental_lc_name: Name string of load case to query properties
        :type incremental_lc_name: str
        :param kwargs:
        :return:
        """
        # get query options
        if not self.parse:
            raise Exception(
                "Moving load is not yet set to a grillage model - no information ready for query. hint"
                "add moving load to a grillage model via add_load_case()"
            )
        # specific incremental load case name
        self.incremental_name = incremental_lc_name
        # specific load group name
        load_group_name = kwargs.get("load_group_name", [])
        index = kwargs.get("index", 0)
        option = kwargs.get("option", "position")

        # instantiate variables
        query_load_case = []
        # get incremental load cases based on incremental names provided by users
        for ml in self.moving_load_case:
            for incremental_lc in ml:
                if self.incremental_name == incremental_lc.name:
                    query_load_case = incremental_lc
                    break
            break
        # get load groups within moving load and its respective path
        if load_group_name:
            selected_load_groups = [
                load
                for load in query_load_case.load_groups
                if load["load"].name in load_group_name
            ]
            selected_lc_list = [
                a for a in self.load_case_dict_list if a["load"].name in load_group_name
            ]
        else:  # select all load groups in
            selected_load_groups = query_load_case.load_groups
            selected_lc_list = self.load_case_dict_list

        # TODO add more options* and check if compound or basic
        if option == "position":
            return [a["load"].point_list for a in selected_load_groups]
        elif option == "offset":
            return [
                a["load"].point_list - b
                for (a, b) in zip(selected_load_groups, selected_lc_list)
            ]
        elif option == "original":
            return selected_lc_list
        elif option == "path":
            return [load["path"] for load in selected_lc_list]


class Path:
    """
    Main class to define path of a moving load object
    """

    def __init__(
        self,
        start_point: Point,
        end_point: Point,
        increments=50,
        mid_point: Point = None,
    ):
        self.start_point = start_point
        self.end_point = end_point
        # here create a straight path
        self.path_points_x = np.linspace(start_point.x, end_point.x, increments)
        self.path_points_y = np.linspace(start_point.y, end_point.y, increments)
        self.path_points_z = np.linspace(start_point.z, end_point.z, increments)
        self.path_points_list = []

    def get_path_points(self) -> list:
        self.path_points_list = [
            [x, y, z]
            for (x, y, z) in zip(
                self.path_points_x, self.path_points_y, self.path_points_z
            )
        ]
        return self.path_points_list

    def get_custom_path_points(self, new_increment):
        path_points_x = np.linspace(self.start_point.x, self.end_point.x, new_increment)
        path_points_y = np.linspace(self.start_point.x, self.end_point.x, new_increment)
        path_points_z = np.linspace(self.start_point.x, self.end_point.x, new_increment)
        path_point_list = [
            [x, y, z] for (x, y, z) in zip(path_points_x, path_points_y, path_points_z)
        ]
        return path_point_list


# ---------------------------------------------------------------------------------------------------------------
def create_load_model(**kwargs):
    """
    Function to create a CompoundLoad object of a vehicle load model model
    :return: `LoadModel` object
    """
    return LoadModel(**kwargs)
    pass


class LoadModel:
    """
    Class to handle load model generator. This contains library of load models and creates load model using
    `CompoundLoad` class.

    For users wishing to contribute/add load models, do so herein by adding the load model as a function to
    this class.

    """

    def __init__(self, gap=0, **kwargs):
        """
        Init the class.

        :param gap: Gap between axle (specific to M1600)
        :param kwargs: See below
        """
        self.gap = gap
        self.model_type = kwargs.get("model_type", None)
        self.units = kwargs.get("units", "SI")
        self.origin = kwargs.get("origin", Point(0, 0, 0))
        # create unit dict
        self.unit_dict = {"m": 1, "kN": 1e3}
        # create variables
        self.x_offset = self.origin.x
        self.z_offset = self.origin.z
        # default y offset is zero

        # checks
        if self.origin is None:
            self.x_offset = 0

    def create(self):
        if self.model_type == "M1600":
            return self.create_m1600_vehicle(self.gap)

    def create_m1600_vehicle(self, gap):
        """
        AS5100 Australian load model.

        :param gap: Gap between axle group
        :return: :class:`~ospgrillage.load.CompoundLoad` object of a M1600 vehicle in local coordinate.
        """
        # default SI units
        m = 1
        kN = 1e3
        if self.units == "SI":  # if SI, de-activate converter variables
            ft_convert = 1
            ton_convert = 1
        else:  # Imperial units
            ft_convert = 3.28084
            ton_convert = 0.10036113565668

        axle_dist = 1.25 * m * ft_convert
        left_group_dist = 3.75 * m * ft_convert
        right_group_dist = 5 * m * ft_convert
        wheel_load = 60 * kN * ton_convert
        load_positions_x = [
            0,
            axle_dist,
            axle_dist * 2,
            left_group_dist + axle_dist * 2,
            left_group_dist + axle_dist * 2 + axle_dist,
            left_group_dist + axle_dist * 2 + 2 * axle_dist,
            gap + left_group_dist + axle_dist * 2,
            gap + left_group_dist + axle_dist * 2 + axle_dist,
            gap + left_group_dist + axle_dist * 2 + 2 * axle_dist,
            right_group_dist + gap + left_group_dist + axle_dist * 2,
            right_group_dist + gap + left_group_dist + axle_dist * 2 + axle_dist,
            right_group_dist + gap + left_group_dist + axle_dist * 2 + 2 * axle_dist,
        ]
        load_positions_x = [point + self.x_offset for point in load_positions_x]

        load_positions_z = [-1, 1]
        load_positions_z = [point + self.z_offset for point in load_positions_z]

        M1600_vehicle = create_compound_load(name="M1600 Vehicle")
        for z in load_positions_z:
            for x in load_positions_x:
                vert = create_load_vertex(x=x, z=z, p=wheel_load)
                point = create_load(loadtype="point", name="M1600 point", point1=vert)
                M1600_vehicle.add_load(load_obj=point)

        return M1600_vehicle


# ---------------------------------------------------------------------------------------------------------------
class ShapeFunction:
    """
    Class for shape functions. The role of Shape functions in ospgrillage is to distribute loads to nodes.

    Here developers can add more shape functions to this class by:
    * adding the option in get_shape_function()
    * defining the shape function as a class function

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
    def hermite_shape_function_1d(
        zeta, a
    ):  # using zeta and a as placeholders for normal coor + length of edge element
        # hermite shape functions
        """
        :param zeta: absolute position in x direction
        :param a: absolute position in x direction
        :return: Four terms [N1, N2, N3, N4] of hermite shape function
        .. note::

        """
        N1 = 1 - 3 * zeta**2 + 2 * zeta**3
        N2 = (zeta - 2 * zeta**2 + zeta**3) * a
        N3 = 3 * zeta**2 - 2 * zeta**3
        N4 = (-(zeta**2) + zeta**3) * a
        return [N1, N2, N3, N4]

    @staticmethod
    def hermite_shape_function_2d(eta, zeta):
        # nodes must be counter clockwise such that n1 = left bottom of relative grid
        # 4  3
        # 1  2
        h1 = 0.25 * (2 - 3 * eta + eta**3)
        h2 = 0.25 * (1 - eta - eta**2 + eta**3)
        h3 = 0.25 * (2 + 3 * eta - eta**3)
        h4 = 0.25 * (-1 - eta + eta**2 + eta**3)
        z1 = 0.25 * (2 - 3 * zeta + zeta**3)
        z2 = 0.25 * (1 - zeta - zeta**2 + zeta**3)
        z3 = 0.25 * (2 + 3 * zeta - zeta**3)
        z4 = 0.25 * (-1 - zeta + zeta**2 + zeta**3)
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
