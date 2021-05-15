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


def search_grid_lines(node_line_list, position):
    upper_grids = []
    lower_grids = []
    for count, node_position in enumerate(node_line_list):
        if node_position <= position:
            lower_grids.append(count)
        elif node_position >= position:
            upper_grids.append(count)
    lower_line = max(lower_grids)
    upper_line = min(upper_grids)
    return upper_line, lower_line
