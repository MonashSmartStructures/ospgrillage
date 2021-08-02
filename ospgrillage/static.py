# -*- coding: utf-8 -*-
"""
Module description
"""

import numpy as np
from scipy.spatial import distance
from sympy import symbols, Eq, solve
from decimal import *


def diff(li1, li2):
    """
        Static method to determine the difference between two list. Called in set_member() function to check member
        assignment

        """
    return list(list(set(li1) - set(li2)) + list(set(li2) - set(li1)))


def search_grid_lines(node_line_list, position, position_bound="ub"):
    upper_grids = []
    lower_grids = []
    for count, node_position in enumerate(node_line_list):
        if node_position <= position:
            lower_grids.append(count)
        elif node_position >= position:
            upper_grids.append(count)

    lower_line = max(lower_grids)
    upper_line = min(upper_grids)

    lower_pos_diff = position - node_line_list[lower_line]
    upper_pos_diff = node_line_list[upper_line] - position
    spacing = (node_line_list[upper_line] - node_line_list[lower_line]) / 2
    if position_bound == "ub":
        if lower_pos_diff > spacing:
            upper_line_width = lower_pos_diff - spacing
            lower_line_width = spacing
        else:
            upper_line = []
            upper_line_width = 0
            lower_line_width = lower_pos_diff
    elif position_bound == "lb":
        if upper_pos_diff > spacing:
            lower_line_width = upper_pos_diff - spacing
            upper_line_width = spacing
        else:
            lower_line = []
            lower_line_width = 0
            upper_line_width = upper_pos_diff
    else:
        upper_line_width = upper_pos_diff
        lower_line_width = lower_pos_diff

    return [[upper_line, upper_line_width], [lower_line, lower_line_width]]


def findCircle(x1, y1, x2, y2, x3, y3):
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

    f = (((sx13) * (x12) + (sy13) *
          (x12) + (sx21) * (x13) +
          (sy21) * (x13)) // (2 *
                              ((y31) * (x12) - (y21) * (x13))))

    g = (((sx13) * (y12) + (sy13) * (y12) +
          (sx21) * (y13) + (sy21) * (y13)) //
         (2 * ((x31) * (y12) - (x21) * (y13))))

    c = (-pow(x1, 2) - pow(y1, 2) -
         2 * g * x1 - 2 * f * y1)

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

def line_func(m, c, x):
    if type(x) is list:
        y = m * x[0] + c
    else:
        y = m * x + c
    return y


def inv_line_func(m, c, y):
    x = (y - c) / m if all([m != 0, m is not None, c is not None]) else 0
    return x


def arc_func(h, v, R, x, r=0):
    # function to get y coordinate on an arc given the variables of the circle equation
    # option to add radius to circle , lowercase r
    y = np.sqrt((R + r) ** 2 - (x - h) ** 2) + v
    return y


# TODO
def transition_curve_func():
    pass


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
    A = (p1[1] - p2[1])
    B = (p2[0] - p1[0])
    C = (p1[0] * p2[1] - p2[0] * p1[1])
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
    # function to solve for eta and zeta of point in grid after mapping grid nodes (4) to four coordinate in
    # a reference quadrilateral
    x, z = symbols('x,z')

    eq1 = Eq(
        4 * zp - ((1 - x) * (1 - z) * z1 + (1 + x) * (1 - z) * z2 + (1 + x) * (1 + z) * z3 + (1 - x) * (1 + z) * z4), 0)
    eq2 = Eq(
        4 * xp - ((1 - x) * (1 - z) * x1 + (1 + x) * (1 - z) * x2 + (1 + x) * (1 + z) * x3 + (1 - x) * (1 + z) * x4), 0)
    sol = solve((eq1, eq2), (x, z))
    return sol[x], sol[z]  # sol[x] = eta, sol[z] = zeta


#
# def calculate_area_given_four_points(inside_point, point1, point2, point3, point4):
#     # inputs are namedtuple Point() of coordinates
#     # ref: <https://math.stackexchange.com/questions/190111/how-to-check-if-a-point-is-inside-a-rectangle>
#     # function typically assume plane of x and y. for usage in OpsGrillage, plane x z is taken instead, where y is z
#     a1 = np.sqrt((point1.x - point2.x) ** 2 + (point1.z - point2.z) ** 2)
#     a2 = np.sqrt((point2.x - point3.x) ** 2 + (point2.z - point3.z) ** 2)
#     a3 = np.sqrt((point3.x - point4.x) ** 2 + (point3.z - point4.z) ** 2)
#     a4 = np.sqrt((point4.x - point1.x) ** 2 + (point4.z - point1.z) ** 2)
#     b1 = np.sqrt((point1.x - inside_point.x) ** 2 + (point1.z - inside_point.z) ** 2)
#     b2 = np.sqrt((point2.x - inside_point.x) ** 2 + (point2.z - inside_point.z) ** 2)
#     b3 = np.sqrt((point3.x - inside_point.x) ** 2 + (point3.z - inside_point.z) ** 2)
#     b4 = np.sqrt((point4.x - inside_point.x) ** 2 + (point4.z - inside_point.z) ** 2)
#     # Herons formula
#     u1 = (a1 + b1 + b2) / 2
#     u2 = (a2 + b2 + b3) / 2
#     u3 = (a3 + b3 + b4) / 2
#     u4 = (a4 + b4 + b1) / 2
#     A1 = np.sqrt(u1 * (u1 - a1) * (u1 - b1) * (u1 - b2))
#     A2 = np.sqrt(u2 * (u2 - a2) * (u2 - b2) * (u2 - b3))
#     A3 = np.sqrt(u3 * (u3 - a3) * (u3 - b3) * (u3 - b4))
#     A4 = np.sqrt(u4 * (u4 - a4) * (u4 - b4) * (u4 - b1))
#     A = a1 * a2
#     return [A1, A2, A3, A4], A
#
#
# def calculate_area_given_three_points(point1, point2, point3):
#     # ref: https://ncalculators.com/geometry/triangle-area-by-3-points.htm
#     A = 0.5 * (point1.x * (point2.z - point3.z) + point2.x * (point3.z - point1.z) + point3.x * (point1.z - point2.z))
#     return A

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
    signed_area = check_points_direction(point_list)  # sign area < 0 means points are clockwise, and vice versa
    for count, point0 in enumerate(pt0):
        side = (inside_point.z - point0.z) * (pt1[count].x - point0.x) - (inside_point.x - point0.x) * (
                pt1[count].z - point0.z)
        # check if point is outside
        if any([side < 0 <= signed_area,  # side > 0 means left, side < 0 means right, side = 0 means on the line path
                side > 0 > signed_area]):  # nodes are counterclockwise and point to right (outside)
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
        signed_area += (x1 * z2 - x2 * z1)

        last_point = point  # set current point as last point
    return signed_area


# ----------------------------------------------------------------------------------------------------------
# function to check intersection of line segments
def onSegment(p, q, r):
    # point nameTuple p, q and r
    if ((q.x <= max(p.x, r.x)) and (q.x >= min(p.x, r.x)) and
            (q.y <= max(p.z, r.z)) and (q.z >= min(p.z, r.z))):
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
    xc = mx / sum(m_total)
    zc = mz / sum(m_total)
    yc = my / sum(m_total)
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
                if key == 'ends':
                    val_end = val_1 if val_1 else second_list.get(key)
                    updated_list.setdefault(key, val_end)
                else:
                    val_2 = second_list.get(key)
                    updated_list.setdefault(key, val_1 + val_2)
            merged.update({grid: updated_list})

    return merged
