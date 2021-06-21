import pprint
from collections.abc import Iterable
from typing import Type
from scipy import interpolate
from static import *
from Mesh import *
from collections import namedtuple
from typing import Union
from copy import deepcopy

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
    load_point_1: LoadPoint
    load_point_2: LoadPoint
    load_point_3: LoadPoint
    load_point_4: LoadPoint
    load_point_5: LoadPoint
    load_point_6: LoadPoint
    load_point_7: LoadPoint
    load_point_8: LoadPoint

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
        # parse namedtuple of global coordinates
        self.load_point_1 = kwargs.get('point1', None)
        self.load_point_2 = kwargs.get('point2', None)
        self.load_point_3 = kwargs.get('point3', None)
        self.load_point_4 = kwargs.get('point4', None)
        self.load_point_5 = kwargs.get('point5', None)
        self.load_point_6 = kwargs.get('point6', None)
        self.load_point_7 = kwargs.get('point7', None)
        self.load_point_8 = kwargs.get('point8', None)

        # parse namedtuple of local coordinates
        self.local_load_point_1 = kwargs.get('localpoint1', None)
        self.local_load_point_2 = kwargs.get('localpoint2', None)
        self.local_load_point_3 = kwargs.get('localpoint3', None)
        self.local_load_point_4 = kwargs.get('localpoint4', None)
        self.local_load_point_5 = kwargs.get('localpoint5', None)
        self.local_load_point_6 = kwargs.get('localpoint6', None)
        self.local_load_point_7 = kwargs.get('localpoint7', None)
        self.local_load_point_8 = kwargs.get('localpoint8', None)

        #TODO check if user skipped point 1 and defined point1 as point 2 instead

        # check if load object has both a local and global coordinate
        if all([self.load_point_1 is not None,self.local_load_point_1 is not None]):
            raise Exception("Load object created with both local and global coordinates: Only either one is permitted")

        # list of load points tuple
        self.point_list = [self.load_point_1, self.load_point_2, self.load_point_3, self.load_point_4,
                           self.load_point_5, self.load_point_6, self.load_point_7, self.load_point_8]
        self.local_point_list = [self.local_load_point_1, self.local_load_point_2, self.local_load_point_3,
                                 self.local_load_point_4, self.local_load_point_5, self.local_load_point_6,
                                 self.local_load_point_7, self.local_load_point_8]
        # var for compound load group (handled by LoadCase class when creating compound groups)
        self.compound_dist_x = 0  # local coordinate system
        self.compound_dist_z = 0  # local coordinate system
        self.ref_point = None  # local coordinate system
        self.compound_group = None  # group number access by LoadCase class to move load group if any path is defined
        # init dict
        self.spec = dict()  # dict {node number: {Fx:val, Fy:val, Fz:val, Mx:val, My:val, Mz:val}}
        self.load_counter = 0

    # modify load points if compound load option is present i.e. compound_x_list
    def form_compound_load(self, **kwargs):

        # if global coordinates are given, reset global to local by subtracting the centroid, then adding the local coord if any
        if any(self.point_list):
            point_list = [i for i in self.point_list if i is not None]
            centroid = find_plane_centroid(point_list)
            # get kwargs
            self.ref_point = kwargs.get('ref_point', Point(0, self.load_point_1.y,
                                                           0))  # custom ref_point of load_point groups with respect to local coord default = origin of local coord
            self.compound_dist_x = kwargs.get('compound_dist_x',
                                              0)  # shift of ref point (and all poinst) in x direction with respect to local coord
            self.compound_dist_z = kwargs.get('compound_dist_z',
                                              0)  # shift of ref point (and all points) in z direction with respect to local coord

            # translate points with respect to centroid to origin
            self.load_point_1 = self.load_point_1._replace(
                x=self.load_point_1.x - centroid[0] + self.compound_dist_x + self.ref_point.x,
                z=self.load_point_1.z - centroid[
                    1] + self.compound_dist_z + self.ref_point.z) if self.load_point_1 is not None else self.load_point_1
            self.load_point_2 = self.load_point_2._replace(
                x=self.load_point_2.x - centroid[0] + self.compound_dist_x + self.ref_point.x,
                z=self.load_point_2.z - centroid[
                    1] + self.compound_dist_z + self.ref_point.z) if self.load_point_2 is not None else self.load_point_2
            self.load_point_3 = self.load_point_3._replace(
                x=self.load_point_3.x - centroid[0] + self.compound_dist_x + self.ref_point.x,
                z=self.load_point_3.z - centroid[
                    1] + self.compound_dist_z + self.ref_point.z) if self.load_point_3 is not None else self.load_point_3
            self.load_point_4 = self.load_point_4._replace(
                x=self.load_point_4.x - centroid[0] + self.compound_dist_x + self.ref_point.x,
                z=self.load_point_4.z - centroid[
                    1] + self.compound_dist_z + self.ref_point.z) if self.load_point_4 is not None else self.load_point_4
            self.load_point_5 = self.load_point_5._replace(
                x=self.load_point_5.x - centroid[0] + self.compound_dist_x + self.ref_point.x,
                z=self.load_point_5.z - centroid[
                    1] + self.compound_dist_z + self.ref_point.z) if self.load_point_5 is not None else self.load_point_5
            self.load_point_6 = self.load_point_6._replace(
                x=self.load_point_6.x - centroid[0] + self.compound_dist_x + self.ref_point.x,
                z=self.load_point_6.z - centroid[
                    1] + self.compound_dist_z + self.ref_point.z) if self.load_point_6 is not None else self.load_point_6
            self.load_point_7 = self.load_point_7._replace(
                x=self.load_point_7.x - centroid[0] + self.compound_dist_x + self.ref_point.x,
                z=self.load_point_7.z - centroid[
                    1] + self.compound_dist_z + self.ref_point.z) if self.load_point_7 is not None else self.load_point_7
            self.load_point_8 = self.load_point_8._replace(
                x=self.load_point_8.x - centroid[0] + self.compound_dist_x + self.ref_point.x,
                z=self.load_point_8.z - centroid[
                    1] + self.compound_dist_z + self.ref_point.z) if self.load_point_8 is not None else self.load_point_8

        else:
            pass
        # else set points


        # find centroid of load_points

    # function called by Moving load module to move the load group
    def move_load(self, ref_point: Point):
        if any(self.point_list):
            self.load_point_1 = self.load_point_1._replace(x=self.load_point_1.x + ref_point.x,
                                                           z=self.load_point_1.z + ref_point.z) if self.load_point_1 is \
                                                                                                   not None else self.load_point_1
            self.load_point_2 = self.load_point_2._replace(x=self.load_point_2.x + ref_point.x,
                                                           z=self.load_point_2.z + ref_point.z) if self.load_point_2 is \
                                                                                                   not None else self.load_point_2
            self.load_point_3 = self.load_point_3._replace(x=self.load_point_3.x + ref_point.x,
                                                           z=self.load_point_3.z + ref_point.z) if self.load_point_3 is \
                                                                                                   not None else self.load_point_3
            self.load_point_4 = self.load_point_4._replace(x=self.load_point_4.x + ref_point.x,
                                                           z=self.load_point_4.z + ref_point.z) if self.load_point_4 is \
                                                                                                   not None else self.load_point_4
            self.load_point_5 = self.load_point_5._replace(x=self.load_point_5.x + ref_point.x,
                                                           z=self.load_point_5.z + ref_point.z) if self.load_point_5 is \
                                                                                                   not None else self.load_point_5
            self.load_point_6 = self.load_point_6._replace(x=self.load_point_6.x + ref_point.x,
                                                           z=self.load_point_6.z + ref_point.z) if self.load_point_6 is \
                                                                                                   not None else self.load_point_6
            self.load_point_7 = self.load_point_7._replace(x=self.load_point_7.x + ref_point.x,
                                                           z=self.load_point_7.z + ref_point.z) if self.load_point_7 is \
                                                                                                   not None else self.load_point_7
            self.load_point_8 = self.load_point_8._replace(x=self.load_point_8.x + ref_point.x,
                                                           z=self.load_point_8.z + ref_point.z) if self.load_point_8 is \
                                                                                                   not None else self.load_point_8
        else:  # set global position by movign local coordinates by x (global) and z (global)
            self.load_point_1 = self.local_load_point_1._replace(x=self.local_load_point_1.x + ref_point.x,
                                                           z=self.local_load_point_1.z + ref_point.z) if self.local_load_point_1 is \
                                                                                                   not None else self.local_load_point_1
            self.load_point_2 = self.local_load_point_2._replace(x=self.local_load_point_2.x + ref_point.x,
                                                           z=self.local_load_point_2.z + ref_point.z) if self.local_load_point_2 is \
                                                                                                   not None else self.local_load_point_2
            self.load_point_3 = self.local_load_point_3._replace(x=self.local_load_point_3.x + ref_point.x,
                                                           z=self.local_load_point_3.z + ref_point.z) if self.local_load_point_3 is \
                                                                                                   not None else self.local_load_point_3
            self.load_point_4 = self.local_load_point_4._replace(x=self.local_load_point_4.x + ref_point.x,
                                                           z=self.local_load_point_4.z + ref_point.z) if self.local_load_point_4 is \
                                                                                                   not None else self.local_load_point_4
            self.load_point_5 = self.local_load_point_5._replace(x=self.local_load_point_5.x + ref_point.x,
                                                           z=self.local_load_point_5.z + ref_point.z) if self.local_load_point_5 is \
                                                                                                   not None else self.local_load_point_5
            self.load_point_6 = self.local_load_point_6._replace(x=self.local_load_point_6.x + ref_point.x,
                                                           z=self.local_load_point_6.z + ref_point.z) if self.local_load_point_6 is \
                                                                                                   not None else self.local_load_point_6
            self.load_point_7 = self.local_load_point_7._replace(x=self.local_load_point_7.x + ref_point.x,
                                                           z=self.local_load_point_7.z + ref_point.z) if self.local_load_point_7 is \
                                                                                                   not None else self.local_load_point_7
            self.load_point_8 = self.local_load_point_8._replace(x=self.local_load_point_8.x + ref_point.x,
                                                           z=self.local_load_point_8.z + ref_point.z) if self.local_load_point_8 is \
                                                                                                   not None else self.local_load_point_8



    def apply_load_factor(self, factor=1):
        self.load_point_1 = self.load_point_1._replace(p=factor * self.load_point_1.p) if self.load_point_1 is \
                                                                                          not None else self.load_point_1
        self.load_point_2 = self.load_point_2._replace(p=factor * self.load_point_2.p) if self.load_point_2 is \
                                                                                          not None else self.load_point_2
        self.load_point_3 = self.load_point_3._replace(p=factor * self.load_point_3.p) if self.load_point_3 is \
                                                                                          not None else self.load_point_3
        self.load_point_4 = self.load_point_4._replace(p=factor * self.load_point_4.p) if self.load_point_4 is \
                                                                                          not None else self.load_point_4
        self.load_point_5 = self.load_point_5._replace(p=factor * self.load_point_5.p) if self.load_point_5 is \
                                                                                          not None else self.load_point_5
        self.load_point_6 = self.load_point_6._replace(p=factor * self.load_point_6.p) if self.load_point_6 is \
                                                                                          not None else self.load_point_6
        self.load_point_7 = self.load_point_7._replace(p=factor * self.load_point_7.p) if self.load_point_7 is \
                                                                                          not None else self.load_point_7
        self.load_point_8 = self.load_point_8._replace(p=factor * self.load_point_8.p) if self.load_point_8 is \
                                                                                          not None else self.load_point_8

    def __str__(self):
        return "Load object {} \n".format(self.name) + pprint.pformat(self.spec)


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
            if v[0] == 0 and self.load_point_2.x == self.load_point_1.x:
                pp = (zp - self.load_point_1.z) / v[2] * v[1] + self.load_point_1.p
            else:
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
    *. CompoundLoad object can have Loads class and its inheritances (Line, Point, Patch)
    *. CompoundLoad handles functions of Load classes (e.g. move_load)

    """
    def __init__(self, name):
        self.name = name
        self.compound_load_obj_list = []
        self.local_coord_list = []
        self.centroid = Point(0, 0, 0)  # named tuple Point
        self.global_coord = self.centroid

    def add_load(self, load_obj: Loads, local_coord: Point = None):
        # update the load obj to be part of compound load by first
        # shifting all load points relative to centroid of defined load class
        # then shifting centroid and load_points relative to A Local Coordinate system
        if local_coord is None:
            local_coord = Point(0,0,0)
        load_obj_copy = deepcopy(load_obj)
        load_obj_copy.form_compound_load(compound_dist_x=local_coord.x, compound_dist_z=local_coord.z)
        # then shift load obj relative to global coord (this is the coord of the model) default is 0,0,0 if not set
        # by user
        load_obj_copy.move_load(self.global_coord)
        self.compound_load_obj_list.append(load_obj_copy)  # after update, append to list
        self.local_coord_list.append(local_coord)

    def set_global_coord(self, global_coord: Point):
        # overwrite global coordinate
        if global_coord != self.global_coord:
            self.global_coord = global_coord
            # loop each load type in compound load and shift by global_coord
            append_load_list = []
            # once overwritten, update loadpoints in each load obj of compound load by global_coord
            for loads in self.compound_load_obj_list:
                loads.move_load(global_coord)  # shift load objs using Load class method move_load()
                append_load_list.append(loads)  # append loads which have been moved to new list and
            self.compound_load_obj_list = append_load_list  # overwrite it to class variable


# ---------------------------------------------------------------------------------------------------------------
class LoadCase:
    """
    Main class for load cases. Each load case holds information about:
    1) Load object types (point line patch or combination i.e. compound load)
    2) load case ops load command line - this is generated by ops-grillage class method (add_load_case()) and updated
         to LoadCase class object.
    3) Load factor - all load objects within a Load case are link to one same load factor


    Here are a few relationships between LoadCase and other classes
    *. MovingLoad class creates a series of load case representing the movement of load objects in each load case.
    *. Load combination takes in several LoadCase class instance with varied load factors into a single analysis
    *. Analysis class handles the ops. commands required for
    *. OpsGrillage class takes in load case and updates the variable 'load_command_list' after distributing loads
        within the LoadCase class to nodes/elements of the Mesh in OpsGrillage.
    *. LoadCase class can have Load objects or CompoundLoad class object

    """
    def __init__(self, name):
        self.name = name
        self.load_groups = []
        self.position = None
        # preset load factor for
        self.load_command_list = []

    def add_load_groups(self, load_obj, **kwargs):
        load_dict = dict()
        load_dict.setdefault('load',deepcopy(load_obj))  # create copy of object instance
        load_factor = kwargs.get('load_factor', 1)
        load_dict.setdefault('factor', load_factor)
        self.load_groups.append(load_dict)

    # function for if load groups are to change its ref position due to movement / traversing loads
    # warning : this function is only to be handled by MovingLoad class
    def move_load_group(self, ref_point: Point):
        self.position = ref_point
        for load_dict in self.load_groups:
            load_obj = load_dict.get('load')
            load_obj.move_load(self.position)

    # # function handled by ops_grillage to set load commands (ops.load()) of current load case
    # def set_load_case_load_command(self, load_str: list):
    #     self.load_command_list += load_str


# ---------------------------------------------------------------------------------------------------------------
class MovingLoad:
    """
    Main class of moving load case. MovingLoad class parses and creates multiple loadcase object corresponding to
    traversing the input load groups - be it compound or single. Moving load is able to set various path (defined by
    Path class object) to individual load groups.

    """
    def __init__(self, name):
        self.name = name
        self.load_list = []
        self.path_list = []
        self.load_case_dict_list = []       # Variable to access
        self.moving_load_case = []      # Variable recording all created load case for all load group's respective path
        self.static_load_case = []

    def add_loads(self, load_obj: Union[Loads, CompoundLoad], path_obj=None):
        """
        Function to set a load type (Loads class object) with its path (Path class object). Function accepts compound
        load (Compound load class) as a load input, which in turn sets the path object to all loads within the compound
        load group.
        :param load_obj: Loads class object , or Compound load object
        :param path_obj: Path class object - A path object must be defined for the Load class object. If none is
                        defined, Load is treated as a static load and is added to each incremental analysis of the moving
                        load

        Structure of lists (example)

        load_list = [1st LoadCase point,  2nd LoadCase patch, ... , Nth LoadCase misc load]
        path_list = [Path for LoadCase point 1, [], ... , [] for Nth path]

        size of load_list and path_list must be identical.



        """
        # if no path object is added, set empty list to path_obj. The load group will be treated as a static load
        # present throughout the movement of other load groups (added to the series of moving load case)
        if path_obj is None:
            path_obj = []
        load_pair_path = dict()
        load_pair_path.setdefault("load", load_obj)
        load_pair_path.setdefault("path", path_obj)
        self.load_case_dict_list.append(load_pair_path)

    # function to sort moving loads into multiple load cases - automatically called by Ops-grillage
    def parse_moving_load_cases(self):
        # loop through all load-path pairs and identify static loads
        for load_pair_dict in self.load_case_dict_list:
            if not load_pair_dict["path"]: # empty path, load is static
                self.static_load_case.append(load_pair_dict["load"])

        # create load case obj for each step in the move
        for load_pair_dict in self.load_case_dict_list:
            path_list = load_pair_dict["path"]  # extract path_list of load object
            load_obj = load_pair_dict["load"]
            # loop to create a load case for each increment of the path obj
            load_case_list = []
            for steps in path_list:
                load_step_lc = LoadCase(name="load {} at {}".format(load_obj.name,repr(steps)))  # _lc in name stands for load case
                load_obj_copy = deepcopy(load_obj)  # Use deepcopy module to copy instance of load
                load_step_lc.add_load_groups(load_obj_copy)    # and add load to newly created load case
                # add entries of static load to load groups
                step_point = Point(steps[0],steps[1],steps[2])  # convert increment position into Point tuple
                load_step_lc.move_load_group(step_point)        # increment the load groups by step point
                for static_load in self.static_load_case:       # add static load portions to each incremental load case
                    static_load_copy = deepcopy(static_load)
                    load_step_lc.add_load_groups(static_load_copy)
                load_case_list .append(load_step_lc)
            self.moving_load_case.append(load_case_list)
        return self.moving_load_case


class Path:
    def __init__(self, start_point: Point, end_point: Point, increments=50) -> list:
        self.start_point = start_point
        self.end_point = end_point
        # here create a straight path
        self.path_points_x = np.linspace(start_point.x, end_point.x, increments)
        self.path_points_y = np.linspace(start_point.y, end_point.y, increments)
        self.path_points_z = np.linspace(start_point.z, end_point.z, increments)
        self.path_points_list = []

    def get_path_points(self):
        self.path_points_list = [[x,y,z] for (x,y,z) in zip(self.path_points_x,self.path_points_y,self.path_points_z)]
        return self.path_points_list


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
