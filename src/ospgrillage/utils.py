# -*- coding: utf-8 -*-
"""
This module holds all static methods used in other modules. Static methods are general functions to perform
calculations. Most methods herein are not part of API of ospgrillage - these functions are only called and accessed in
ospgrillage for the purpose of its meshing and calculations. However, users may find some static methods to be useful
for their workflow.
"""

import numpy as np
from scipy.spatial import distance
from scipy.optimize import fsolve, root
import warnings


def diff(li1, li2):
    """
    Static method to determine the difference between two list. used in OspGrillage.set_member() function to check member
    assignment
    """
    return list(list(set(li1) - set(li2)) + list(set(li2) - set(li1)))


def find_circle(x1, y1, x2, y2, x3, y3):
    x12 = x1 - x2
    x13 = x1 - x3

    y12 = y1 - y2
    y13 = y1 - y3

    y31 = y3 - y1
    y21 = y2 - y1

    x31 = x3 - x1
    x21 = x2 - x1

    # x1^2 - x3^2
    sx13 = pow(x1, 2) - pow(x3, 2)

    # y1^2 - y3^2
    sy13 = pow(y1, 2) - pow(y3, 2)

    sx21 = pow(x2, 2) - pow(x1, 2)
    sy21 = pow(y2, 2) - pow(y1, 2)

    f = ((sx13) * (x12) + (sy13) * (x12) + (sx21) * (x13) + (sy21) * (x13)) // (
        2 * ((y31) * (x12) - (y21) * (x13))
    )

    g = ((sx13) * (y12) + (sy13) * (y12) + (sx21) * (y13) + (sy21) * (y13)) // (
        2 * ((x31) * (y12) - (x21) * (y13))
    )

    c = -pow(x1, 2) - pow(y1, 2) - 2 * g * x1 - 2 * f * y1

    # eqn of circle be x^2 + y^2 + 2*g*x + 2*f*y + c = 0
    # where centre is (h = -g, k = -f) and
    # radius r as r^2 = h^2 + k^2 - c
    h = -g
    k = -f
    sqr_of_r = h * h + k * k - c

    # r is the radius
    r = round(np.sqrt(sqr_of_r), 5)

    print("Centre = (", h, ", ", k, ")")
    print("Radius = ", r)

    return [[h, k], r]


# -----------------------------------------------------------------------------------------------------------------------
# Sweep path equations - Add future functions here
# which the given three points lie


def line_func(m=None, c=None, x=None, h=None, v=None, R=None):
    """
    Line function. Returns y position given x.
    """
    curve = False
    if not all([h is None, v is None, R is None]):
        curve = True

    if not curve:
        # straight line
        if type(x) is list:
            y = m * x[0] + c
        else:
            y = m * x + c
    elif curve:
        y = np.sqrt((R) ** 2 - (x - h) ** 2) + v
    else:
        raise Exception(
            "line function missing arguments for valid function selection: check arguments"
        )

    return y


def inv_line_func(m, c, y):
    x = (y - c) / m if all([m != 0, m is not None, c is not None]) else 0
    return x


def arc_func(h, v, R, x, r=0):
    # function to get y coordinate on an arc given the variables of the circle equation
    # option to add radius to circle , lowercase r
    y = np.sqrt((R + r) ** 2 - (x - h) ** 2) + v
    return y


def create_arc_points(point1, radius, length, num_inc):
    # function to create points along arc `length` of a sector with `angle`
    start_angle = np.pi / 2  # 90 degrees
    angle = length / radius  # calculate angle of sector
    end_angle = (
        start_angle - angle
    )  # difference is the end point's angle (about center_point)
    center_point = [point1.x, -radius]  # x z , model plane = 0 default
    # find point2
    angle_inc = np.linspace(start_angle, end_angle, num_inc)
    # point2 = [center_point[0] + radius*np.cos(end_angle), center_point[1] + radius * np.sin(end_angle)]

    x_curve = [center_point[0] + radius * np.cos(ang) for ang in angle_inc]
    z_curve = [center_point[1] + radius * np.sin(ang) for ang in angle_inc]

    return x_curve, z_curve


# -----------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------
def select_segment_function(curve_flag, d, x, r=0, m=0, c=0):
    if curve_flag:
        y = arc_func(h=d[0][0], v=d[0][1], R=d[1], x=x, r=r)
    else:
        y = line_func(m, c, x)
    return y


def find_dict_key(my_dict, key):
    return eval(list(my_dict.keys())[list(my_dict.values()).index(key)])


def x_intcp_two_lines(m1, m2, c1, c2):
    x = (c2 - c1) / (m1 - m2)
    return x


def line(p1, p2):
    A = p1[1] - p2[1]
    B = p2[0] - p1[0]
    C = p1[0] * p2[1] - p2[0] * p1[1]
    return A, B, -C


def intersection(L1, L2):
    D = L1[0] * L2[1] - L1[1] * L2[0]
    Dx = L1[2] * L2[1] - L1[1] * L2[2]
    Dy = L1[0] * L2[2] - L1[2] * L2[0]
    if D != 0:
        x = Dx / D
        y = Dy / D
        return x, y
    else:
        return False


def get_y_intcp(m, x, y):
    c = y - x * m if m is not None else None
    return c


def get_line_func(skew_angle, node_point):
    m = 1 / np.tan(-skew_angle / 180 * np.pi)
    if len(node_point) < 3:
        c = get_y_intcp(m=m, x=node_point[0], y=node_point[1])
    else:
        c = get_y_intcp(m=m, x=node_point[0], y=node_point[2])
    return m, c


def find_min_x_dist(const_point, ref_point):
    # constant point is node point on construction line
    # ref_point is roving point on the arbitrary line
    d = distance.cdist(const_point, ref_point)
    return d


def get_slope(pt1, pt2):
    # pt must be [x y z]
    # function claculates the slope for two points inthe 2-D plane, y= 0
    if (pt1[0] - pt2[0]) == 0:
        m = None
    else:
        m = (pt1[2] - pt2[2]) / (pt1[0] - pt2[0])

    # find phi angle
    if m is None:
        phi = np.pi / 2
    else:
        phi = np.arctan(m)
    return m, phi


def solve_zeta_eta(xp, zp, x1, z1, x2, z2, x3, z3, x4, z4):
    # create function to solve for eta and zeta - dynamically for varying parameters x1-x4, z1-z4, zp,xp

    # mapping of natural coordinate eta{-1:1}, zeta{-1:1} to global coordinate (x,z)
    def obj_func(x, xp, zp, x1, x2, x3, x4, z1, z2, z3, z4):
        eta = 4 * zp - (
            (1 - x[0]) * (1 - x[1]) * z1
            + (1 + x[0]) * (1 - x[1]) * z2
            + (1 + x[0]) * (1 + x[1]) * z3
            + (1 - x[0]) * (1 + x[1]) * z4
        )
        zeta = 4 * xp - (
            (1 - x[0]) * (1 - x[1]) * x1
            + (1 + x[0]) * (1 - x[1]) * x2
            + (1 + x[0]) * (1 + x[1]) * x3
            + (1 - x[0]) * (1 + x[1]) * x4
        )
        return eta, zeta

    # if initial xp zp is very close (order 1e-8) to the centre (0,0,0) of natural coordinate,
    # avoid fsolve RunTimeWarning by
    if all([np.isclose(xp, (x1 + x2) / 2), np.isclose(zp, (z1 + z3) / 2)]):
        root_func = [0, 0]

    else:
        root_func = fsolve(
            obj_func,
            np.array([-0.4444444444444, 0.99999999]),
            args=(xp, zp, x1, x2, x3, x4, z1, z2, z3, z4),
        )  # here the initial values are chosen to avoid RunTimeWarning where initial guess is very close
        # to the final solution of eta and zeta

    eta = root_func[0]
    zeta = root_func[1]
    return eta, zeta


def get_distance(a, b):
    return np.sqrt((a.x - b.x) ** 2 + (a.z - b.z) ** 2)


def is_between(a, c, b):
    return get_distance(a, c) + get_distance(c, b) == get_distance(a, b)


def calculate_area_given_vertices(p_list):
    # input list of namedtuple LoadPoint or Point
    # note: p_list must have been sorted in counter clockwise via sort_vertices function
    # (this is called prior to this function)
    x_list = []
    y_list = []
    z_list = []
    A_mag = 0
    for point in p_list:
        x_list.append(point.x)
        y_list.append(point.y)
        z_list.append(point.z)
    # add first point to list
    x_list.append(p_list[0].x)
    y_list.append(p_list[0].y)
    z_list.append(p_list[0].z)
    for count in range(len(x_list) - 1):
        A_mag += x_list[count] * z_list[count + 1] - x_list[count + 1] * z_list[count]
    A = np.abs(A_mag / 2)
    return A


def check_point_in_grid(inside_point, point_list):
    # ref: solution 3 https://www.eecs.umich.edu/courses/eecs380/HANDOUTS/PROJ2/InsidePoly.html
    # check counter clockwise and to the left (greater than 0)
    # put points in list
    pt0 = point_list  # list of point tuples
    # rotate point
    pt1 = pt0[1:] + [pt0[0]]
    inside = True
    if inside_point.z is None:
        inside = False
        return inside
    # check if point is clockwise via sign of signed_area
    signed_area = check_points_direction(
        point_list
    )  # sign area < 0 means points are clockwise, and vice versa
    for count, point0 in enumerate(pt0):
        side = (inside_point.z - point0.z) * (pt1[count].x - point0.x) - (
            inside_point.x - point0.x
        ) * (pt1[count].z - point0.z)
        # check if point is outside
        if any(
            [
                side
                < 0
                <= signed_area,  # side > 0 means left, side < 0 means right, side = 0 means on the line path
                side > 0 > signed_area,
            ]
        ):  # nodes are counterclockwise and point to right (outside)
            inside = False  # nodes are clockwise and point to the left (outside) these condition
    return inside  # return line = outside


def check_points_direction(point_list):
    # list of point tuples
    # ref http://mathworld.wolfram.com/PolygonArea.html
    signed_area = 0
    last_point = None
    first_point = None
    x2 = None
    z2 = None
    for counter, point in enumerate(point_list):
        x1 = point.x
        z1 = point.z
        if first_point is None:
            # save point as first point
            first_point = point

        if counter == len(point_list) - 1:
            x2 = first_point.x
            z2 = first_point.z
        else:
            x2 = point_list[counter + 1].x
            z2 = point_list[counter + 1].z
        signed_area += x1 * z2 - x2 * z1

        last_point = point  # set current point as last point
    return signed_area


# ----------------------------------------------------------------------------------------------------------
# function to check intersection of line segments
def onSegment(p, q, r):
    # point nameTuple p, q and r
    if (
        (q.x <= max(p.x, r.x))
        and (q.x >= min(p.x, r.x))
        and (q.y <= max(p.z, r.z))
        and (q.z >= min(p.z, r.z))
    ):
        return True
    return False


def orientation(p, q, r):
    # to find the orientation of an ordered triplet (p,q,r)
    # function returns the following values:
    # 0 : Colinear points
    # 1 : Clockwise points
    # 2 : Counterclockwise

    # See https://www.geeksforgeeks.org/orientation-3-ordered-points/amp/
    # for details of below formula.
    # modified - p, q, r must be point namedtuple
    val = (float(q.z - p.z) * (r.x - q.x)) - (float(q.x - p.x) * (r.z - q.z))
    if val > 0:
        # Clockwise orientation
        return 1
    elif val < 0:
        # Counterclockwise orientation
        return 2
    else:
        # Colinear orientation
        return 0


# Function returns true if the line segment 'p1q1' and 'p2q2' intersect.
def check_intersect(p1, q1, p2, q2):
    # ref https://www.geeksforgeeks.org/check-if-two-given-line-segments-intersect/
    general_intersect = False
    colinear = False
    # Find the 4 orientations required for
    # the general and special cases
    o1 = orientation(p1, q1, p2)
    o2 = orientation(p1, q1, q2)
    o3 = orientation(p2, q2, p1)
    o4 = orientation(p2, q2, q1)

    # General case
    if (o1 != o2) and (o3 != o4):
        general_intersect = True
        colinear = False
        return general_intersect, colinear

    # Special Cases
    # p1 , q1 and p2 are colinear and p2 lies on segment p1q1
    if (o1 == 0) and onSegment(p1, p2, q1):
        general_intersect = True
        colinear = True
        return general_intersect, colinear

    # p1 , q1 and q2 are colinear and q2 lies on segment p1q1
    if (o2 == 0) and onSegment(p1, q2, q1):
        general_intersect = True
        colinear = True
        return general_intersect, colinear

    # p2 , q2 and p1 are colinear and p1 lies on segment p2q2
    if (o3 == 0) and onSegment(p2, p1, q2):
        general_intersect = True
        colinear = True
        return general_intersect, colinear

    # p2 , q2 and q1 are colinear and q1 lies on segment p2q2
    if (o4 == 0) and onSegment(p2, q1, q2):
        general_intersect = True
        colinear = True
        return general_intersect, colinear

    # If none of the cases
    return general_intersect, colinear


# --------------------------------------------------------------------------------------------
def find_plane_centroid(point_list):
    """
    Function to find centroid given a set of vertices (for patch load). function calculates 2D plane x z - y plane is
    the model plane.
    :param point_list: list of Point() namedtuples
    :type point_list: list
    """
    x = 0
    z = 0
    for point in point_list:
        x += point.x
        z += point.z
    x_c = x / len(point_list)
    z_c = z / len(point_list)
    return [x_c, z_c]


def sort_vertices(point_list, node_tag_list=None):
    # note the node_tag_list must correspond to that of point_list, this is ensure in the higher level
    # functions which calls sort_vertices
    if node_tag_list is None:
        node_tag_list = []
    center_x_z = find_plane_centroid(point_list)
    angle_list = []
    for point in point_list:
        # calculate angle
        x = np.array(point.x - center_x_z[0])
        z = np.array(point.z - center_x_z[1])
        angle_list.append(np.arctan2(z, x))
        # angle_list.append(np.arctan((point.z - center_x_z[1]) / (point.x - center_x_z[0])))
    # angle_list[angle_list<0] = angle_list[angle_list<0] + 2*np.pi
    [i + 2 * np.pi for i in angle_list if i < 0]
    # sort for counter clockwise
    sorted_points = [x for _, x in sorted(zip(angle_list, point_list))]

    sorted_node_tag = [x for _, x in sorted(zip(angle_list, node_tag_list))]
    return sorted_points, sorted_node_tag


def get_patch_centroid(point_list):
    # function to find centroid on a plane (x-z) accounting for separate value of area load on each node point
    m_total = []
    mx = 0
    my = 0
    mz = 0
    for point in point_list:
        m_total.append(point.p)
        mx += point.x * point.p
        mz += point.z * point.p
        my += point.y * point.p
    sum_m = sum(m_total) if sum(m_total) > 0 else 1
    xc = mx / sum_m
    zc = mz / sum_m
    yc = my / sum_m
    return xc, yc, zc


# abstracted function for assigning patch loading
def check_dict_same_keys(d_1, d_2):
    merged = {**d_1, **d_2}
    # function to check if two dicts have same key
    same_key = [k in d_2 for k in d_1.keys()]
    if any(same_key):
        common_key = [k for (k, v) in zip(d_1, same_key) if v]
        # get val from d_1 and d_2
        for grid in common_key:  # key is grid number
            first_list = d_1[grid]
            second_list = d_2[grid]
            updated_list = dict()
            for key, val_1 in first_list.items():
                # if key == 'ends':
                #     val_end = val_1 if val_1 else second_list.get(key)
                #     updated_list.setdefault(key, val_end)
                # else:
                combine_val = []
                val_2 = second_list.get(key)
                for val in val_1 + val_2:
                    if val not in combine_val:
                        combine_val.append(val)

                updated_list.setdefault(key, combine_val)
            merged.update({grid: updated_list})

    return merged


def sort_list_into_four_groups(group_list: list, option: str = None):
    """
    Function to sort a list of group number into four groups , returns a dict with keys [0,1,2,3] placing the ordered
    group_list into each key. Purpose is to distinguish main grillage elements based on the group positioning
    e.g. if group_list = [0,1,2,3,4,5,6], returns {0:[0,6], 1:[1],2:[2,3,4],3:[5]}
    :param option: type of group sorting - default None for beam, "shell" for shell model
    :type option: str
    :param group_list:
    :return: dict with keys [0,1,2,3] and values be the sorted group list as shown in description
    """
    # sort asccending
    output_dict = dict()
    if option == "shell":
        # add two proxy element at start and end of group list
        group_list = [group_list[0] - 1] + group_list + [group_list[-1] + 1]

    # edges
    output_dict[0] = [group_list[0], group_list[-1]]
    # instantiate
    exterior_beam_group_1 = [group_list[1]]
    exterior_beam_group_2 = [group_list[-2]]
    interior_beam_group = group_list[2 : len(group_list) - 2]

    # check for special cases
    if len(group_list) > 2:
        if len(group_list) == 3:  # 2 edge and 1 interior
            interior_beam_group = [group_list[1]]
            exterior_beam_group_1 = []
            exterior_beam_group_2 = []
        elif len(group_list) == 4:  # 2 edge, ext_1 and ext_2
            interior_beam_group = []

    output_dict[1] = exterior_beam_group_1
    output_dict[2] = interior_beam_group
    output_dict[3] = exterior_beam_group_2
    return output_dict


def rotate_point_about_point(center_x, center_y, angle, point: list):
    """
    Rotates point about a second point at [center_x, center_y] by angle in the coordinate system

    param point: list containing the x and y coordinate
    type point: list
    param angle: Angle in radians
    type angle: int or float
    returns: list of coordinate for the rotated point
    """

    s = np.sin(angle)  # rad
    c = np.cos(angle)  # rad
    if isinstance(point, list):
        x_or = point[0] - center_x
        y_or = point[1] - center_y

        x_rot = x_or * c - y_or * s
        y_rot = x_or * s + y_or * c

        # translate back to origin and store to var
        rotated_point = [x_rot + center_x, y_rot + center_y]
    else:
        raise Exception("point= requires a valid list or tuple")

    return rotated_point
