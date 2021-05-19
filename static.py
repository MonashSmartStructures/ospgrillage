import numpy as np


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


# Function to find the circle on
# which the given three points lie
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


def line_func(m, c, x):
    y = m * x + c
    return y


def inv_line_func(m, c, y):
    x = (y - c) / m
    return x


def arc_func(h, v, R, x, r=0):
    # function to get y coordinate on an arc given the variables of the circle equation
    # option to add radius to circle , lowercase r
    y = np.sqrt((R + r) ** 2 - (x - h) ** 2) + v
    return y


def select_segment_function(curve_flag, d, x, r=0, m=0, c=0):
    if curve_flag:
        return arc_func(h=d[0][0], v=d[0][1], R=d[1], x=x, r=r)
    else:
        return line_func(m, c, x)


def find_dict_key(my_dict, key):
    return eval(list(my_dict.keys())[list(my_dict.values()).index(key)])


def x_intcp_two_lines(m1, m2, c1, c2):
    x = (c2 - c1) / (m1 - m2)
    return x


def get_y_intcp(m, x, y):
    c = y - x*m
    return c
