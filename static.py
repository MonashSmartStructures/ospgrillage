import numpy as np
from scipy.spatial import distance
from sympy import symbols, Eq, solve
from decimal import *


def characterize_node_diff(node_list, tol):
    """
    Abstracted method handled by identify_member_groups() to characterize the groups of elements based on spacings
    of node points in node_list.

    :param tol: float of tolerance for checking spacings in np.diff() function
    :param node_list: list containing node points along orthogonal axes (x and z)

    :return ele_group: list of int indicating the groups of the elements along the orthogonal axes (either x or z)
    :return spacing_diff_set: dict with the unique spacings on easting and westing of node (e.g. [0.5,0.6]  \
    as keyword, returns the int of ele group.
    :return spacing_val_set: dict with int of ele group as keyword, returns sum of the spacings
    of easting and westing with
    """
    ele_group = [1]  # initiate element group list, first default is group 1 edge beam
    spacing_diff_set = {}  # initiate set recording the diff in spacings
    spacing_val_set = {}  # initiate set recoding spacing value
    diff_list = np.round(np.diff(node_list), decimals=tol)  # spacing of the node list- checked with tolerance

    counter = 1
    # first item of
    node_tributary_width = [diff_list[0] / 2]
    for count in range(1, len(node_list)):

        # calculate the spacing diff between left and right node of current node
        if count >= len(diff_list):  # counter exceed the diff_list (size of diff list = size of node_list - 1)
            break  # break from loop, return list
        # procedure to get node tributary area
        node_tributary_width.append(diff_list[count - 1] / 2 + diff_list[count] / 2)
        spacing_diff = [diff_list[count - 1], diff_list[count]]
        if repr(spacing_diff) in spacing_diff_set:
            # spacing recorded in spacing_diff_set
            # set the tag
            ele_group.append(spacing_diff_set[repr(spacing_diff)])
        else:
            # record new spacing in spacing_diff_set
            spacing_diff_set[repr(spacing_diff)] = counter + 1
            spacing_val_set[counter + 1] = sum(spacing_diff)
            # set tag
            ele_group.append(spacing_diff_set[repr(spacing_diff)])
            counter += 1
    ele_group.append(1)  # add last element of list (edge beam group 1)
    node_tributary_width.append(diff_list[-1] / 2)  # add last element (last spacing divide by 2)
    return ele_group, spacing_diff_set, spacing_val_set, node_tributary_width


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
                              ((y31) * (x12) - (y21) * (x13))));

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
    y = []
    if type(x) is list:
        y = m * x[0] + c
    else:
        y = m * x + c
    return y


def inv_line_func(m, c, y):
    x = (y - c) / m if m != 0 else 0
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
    y = []
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
    x, z = symbols('x,z')
    # eta
    # eq1 = Eq((4 * zp - (z1 + z2 + z3 + z4) - z * (-z1 - z2 + z3 + z4)) / (
    #              x * (z1 * (z - 1) + z2 * (1 - z) + z3 * (z + 1) + z4 * (-z - 1))))
    # eq2 = Eq((4 * xp - (x1 + x2 + x3 + x4) - z * (-x1 - x2 + x3 + x4)) / (
    #              x * (x1 * (z - 1) + x2 * (1 - z) + x3 * (z + 1) + x4 * (-z - 1))))
    eq1 = Eq(
        4 * zp - ((1 - x) * (1 - z) * z1 + (1 + x) * (1 - z) * z2 + (1 + x) * (1 + z) * z3 + (1 - x) * (1 + z) * z4), 0)
    eq2 = Eq(
        4 * xp - ((1 - x) * (1 - z) * x1 + (1 + x) * (1 - z) * x2 + (1 + x) * (1 + z) * x3 + (1 - x) * (1 + z) * x4), 0)
    sol = solve((eq1, eq2), (x, z))
    return sol[x], sol[z]


def calculate_area_given_four_points(inside_point, point1, point2, point3, point4):
    # inputs are namedtuple Point() of coordinates
    # ref: <https://math.stackexchange.com/questions/190111/how-to-check-if-a-point-is-inside-a-rectangle>
    # function typically assume plane of x and y. for usage in OpsGrillage, plane x z is taken instead, where y is z
    a1 = np.sqrt((point1.x - point2.x) ** 2 + (point1.z - point2.z) ** 2)
    a2 = np.sqrt((point2.x - point3.x) ** 2 + (point2.z - point3.z) ** 2)
    a3 = np.sqrt((point3.x - point4.x) ** 2 + (point3.z - point4.z) ** 2)
    a4 = np.sqrt((point4.x - point1.x) ** 2 + (point4.z - point1.z) ** 2)
    b1 = np.sqrt((point1.x - inside_point.x) ** 2 + (point1.z - inside_point.z) ** 2)
    b2 = np.sqrt((point2.x - inside_point.x) ** 2 + (point2.z - inside_point.z) ** 2)
    b3 = np.sqrt((point3.x - inside_point.x) ** 2 + (point3.z - inside_point.z) ** 2)
    b4 = np.sqrt((point4.x - inside_point.x) ** 2 + (point4.z - inside_point.z) ** 2)
    # Herons formula
    u1 = (a1 + b1 + b2) / 2
    u2 = (a2 + b2 + b3) / 2
    u3 = (a3 + b3 + b4) / 2
    u4 = (a4 + b4 + b1) / 2
    A1 = np.sqrt(u1 * (u1 - a1) * (u1 - b1) * (u1 - b2))
    A2 = np.sqrt(u2 * (u2 - a2) * (u2 - b2) * (u2 - b3))
    A3 = np.sqrt(u3 * (u3 - a3) * (u3 - b3) * (u3 - b4))
    A4 = np.sqrt(u4 * (u4 - a4) * (u4 - b4) * (u4 - b1))
    A = a1 * a2
    return [A1, A2, A3, A4], A


def check_point_in_grid(inside_point, point_list):
    # ref: solution 3 https://www.eecs.umich.edu/courses/eecs380/HANDOUTS/PROJ2/InsidePoly.html
    # check counter clockwise and to the left (greater than 0)
    # put points in list
    pt0 = point_list  # list of point tuples
    # rotate point
    pt1 = pt0[1:] + [pt0[0]]
    inside = True
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
# TODO refractor
def onSegment(p, q, r):
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
    # Find the 4 orientations required for
    # the general and special cases
    o1 = orientation(p1, q1, p2)
    o2 = orientation(p1, q1, q2)
    o3 = orientation(p2, q2, p1)
    o4 = orientation(p2, q2, q1)

    # General case
    if (o1 != o2) and (o3 != o4):
        return True

    # Special Cases
    # p1 , q1 and p2 are colinear and p2 lies on segment p1q1
    if (o1 == 0) and onSegment(p1, p2, q1):
        return True

    # p1 , q1 and q2 are colinear and q2 lies on segment p1q1
    if (o2 == 0) and onSegment(p1, q2, q1):
        return True

    # p2 , q2 and p1 are colinear and p1 lies on segment p2q2
    if (o3 == 0) and onSegment(p2, p1, q2):
        return True

    # p2 , q2 and q1 are colinear and q1 lies on segment p2q2
    if (o4 == 0) and onSegment(p2, q1, q2):
        return True

    # If none of the cases
    return False
# --------------------------------------------------------------------------------------------


# def change_to_decimal(number):
# return Decimal(number).quantize(Decimal('1.000'))
