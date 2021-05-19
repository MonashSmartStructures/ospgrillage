# ----------------------------------------------------------------------------------------------------------------
# Mesh class
# ----------------------------------------------------------------------------------------------------------------
import numpy as np
import math
from static import *


class Mesh:
    """
    Class for mesh groups. The class holds information pertaining the mesh group such as element connectivity and nodes
    of the mesh object.


    """

    def __init__(self, long_dim, width, trans_dim, edge_width, num_trans_beam, num_long_beam, skew, nox, noz,
                 orthogonal=False, pt1=[0, 0], pt2=[0, 0], pt3=[0, 0], element_counter=1, node_counter=1,
                 transform_counter=0):
        # inputs from OpsGrillage required to create mesh
        self.long_dim = long_dim
        self.trans_dim = trans_dim
        self.edge_width = edge_width
        self.width = width
        self.num_trans_beam = num_trans_beam
        self.num_long_beam = num_long_beam
        # angle and mesh type
        self.skew = skew
        self.orthogonal = orthogonal
        # counter to keep track of variables
        self.node_counter = element_counter
        self.element_counter = node_counter
        self.transform_counter = transform_counter
        # variables to remember counters for node tags
        assigned_node_tag = []
        previous_node_tag = []
        self.decimal_lim = 4  # variable for floating point arithmetic error
        self.curve = False
        # initiate list for nodes and elements
        self.node_map = []
        self.long_ele = []
        self.trans_ele = []
        self.y_elevation = 0
        # dict to record mesh variables
        self.transform_dict = dict()
        self.node_spec = dict()
        # variables for curve mesh
        self.curve_center = []
        self.curve_radius = []
        # line / circle equation variables
        self.m = 0
        self.c = 0
        self.r = 0
        self.R = 0

        # ------------------------------------------------------------------------------------------
        # Procedure to define line segment for the length of the mesh (@ z = 0)
        pt3 = [long_dim, 0.1]  # 3rd point for defining curve mesh
        # if defining an arc line segment, specify p2 such that pt2 is the point at the midpoint of the arc
        try:
            self.d = findCircle(x1=0, y1=0, x2=pt2[0], y2=pt2[1], x3=pt3[0], y3=pt3[1])
            self.curve = True
        except ZeroDivisionError:
            print("3 points result in straight line - not a circle")
            self.d = None
            # procedure to identify straight line segment pinpointing length of grillage
            points = [(pt1[0], pt1[1]), (pt3[0], pt3[1])]
            x_coords, y_coords = zip(*points)
            A = np.vstack([x_coords, np.ones(len(x_coords))]).T
            m, c = np.linalg.lstsq(A, y_coords, rcond=None)[0]
            self.m = round(m, self.decimal_lim)
            # self.c = 0  # default 0  to avoid arithmetic error
            zeta = np.arctan(m)  # angle of inclination of line segment
        # ------------------------------------------------------------------------------------------

        # define the nodes of construction lines for end spans - left and right ends
        last_girder = (self.width - self.edge_width)  # coord of last girder
        nox_girder = np.linspace(start=self.edge_width, stop=last_girder, num=self.num_long_beam - 2)
        # array containing z coordinate
        self.noz = np.hstack((np.hstack((0, nox_girder)), self.width))

        # define edge construction line - line to be swept along line/curve segment
        self.edge_constr_line = []
        edge_const_line_x = [z * np.tan(-self.skew / 180 * math.pi) for z in self.noz]
        # define coordinates of ref nodes on construction line (end span line)
        for (count, xcor) in enumerate(edge_const_line_x):
            self.edge_constr_line.append([xcor, self.y_elevation, self.noz[count]])

        # identify *1 points of variable x spacing of transverse members
        # *2 list of points correspond to points orthogonal to line/curve segment.
        variable_x_spacing = [] # initiate list
        ortho_sweeping_points = [] # initiate list
        if orthogonal:
            mref = self.m  # see note on meshing
            cref = self.c  # see note on meshing
            for points in self.edge_constr_line:
                if math.isinf(-1/self.m):
                    # item 1
                    variable_x_spacing.append([points[0]])
                    # item 2
                    ortho_sweeping_points.append([0, self.y_elevation, points[2]])
                else:
                    # item 1
                    c_item_1 = get_y_intcp(m=-1/self.m, x=points[0], y=points[2])
                    x_item_1 = x_intcp_two_lines(m1=mref, c1=cref, m2=-1 / self.m, c2=c_item_1)
                    variable_x_spacing.append([x_item_1])
                    # item 2
                    c_item_2 = get_y_intcp(m=mref,x=points[0], y=points[2])
                    x_item_2 = x_intcp_two_lines(m1=mref, c1=c_item_2, m2=-1 / self.m, c2=0)
                    ortho_sweeping_points.append([x_item_2, self.y_elevation, line_func(m=-1/self.m,c=0,x=x_item_2)])

            # finish

        # NOTES
        # combined with x variable transverse to define the sweep points
        # input x coordinate of sweep points, return y coordinate, all points in orthogonal sweep construction lines
        # offset by x and y , set point as node.

        # IF angle is positive, sweep for first region is backward
        # else, if skew angle is negative, all three region is forward

        # if variable_spacings goes into the negative x, axis, set node points for uniform spacing grid to start
        # from 0 and end at remaining length (long_dim - max variable_spacing magnitude).
        if variable_x_spacing[np.argmax(np.abs(variable_x_spacing))][0] < 0:
            remaining_length = self.long_dim - max([np.abs(x) for x in variable_x_spacing])
            add_nodes_x = np.linspace(0, remaining_length, self.num_trans_beam)
            variable_x_spacing.reverse()
            sweep_line_seg_x = variable_x_spacing + add_nodes_x.tolist()[1:]
        else:
            add_nodes_x = np.linspace(max([np.abs(x) for x in variable_x_spacing])[0], self.long_dim, self.num_trans_beam)
            sweep_line_seg_x = variable_x_spacing + add_nodes_x.tolist()[1:]

        #
        self.nox = np.linspace(0, self.long_dim, self.num_trans_beam)


        # run section grouping for longitudinal and transverse members
        self.__identify_member_groups()

        # ------------------------------------------------------------------------------------------
        # create nodes and elements
        # if orthogonal, orthogonal mesh only be splayed onto a curve mesh, if skew mesh curved/arc line segment must be
        # false
        if self.orthogonal:
            # first loop sweep ortho_const_line across
            if self.skew < 0:
                loop_x = edge_const_line_x
                # TODO

                loop_z = np.flip(self.noz)
            else:
                loop_x = edge_const_line_x
                loop_x.reverse()
                loop_z = self.noz
            for x_count, x_inc in enumerate(loop_x):
                for z_count, z_point in enumerate(loop_z[0:x_count]):
                    node_coordinate = [x_inc, self.y_elevation, z_point]
                    self.node_spec.setdefault(self.node_counter,
                                              {'tag': self.node_counter, 'coordinate': node_coordinate,
                                               'x_group': x_count, 'z_group': z_count})
                    assigned_node_tag.append(self.node_counter)
                    self.node_counter += 1

            # Second for loop ( across linear region of sweep line)

            # third for loop ( across variable transverse spacing region - mirrors first for loop)

        elif not self.curve:  # Skew mesh + angle
            self.__skew_meshing()

    def __skew_meshing(self):
        assigned_node_tag = []
        for x_count, x_inc in enumerate(self.nox):
            for z_count, ref_point in enumerate(self.edge_constr_line):
                # offset x and y in all points in ref points
                z_inc = np.round(select_segment_function(curve_flag=self.curve, d=self.d, m=self.m, c=self.m, x=x_inc, r=self.r),
                                 self.decimal_lim)
                node_coordinate = [ref_point[0] + x_inc, ref_point[1], ref_point[2] + z_inc]
                self.node_spec.setdefault(self.node_counter,
                                          {'tag': self.node_counter, 'coordinate': node_coordinate,
                                           'x_group': x_count, 'z_group': z_count})
                assigned_node_tag.append(self.node_counter)
                self.node_counter += 1
                # link transverse elements
                if z_count > 0:
                    # element list [element tag, node i, node j, x/z group]
                    tag = self.__get_geo_transform_tag([assigned_node_tag[z_count - 1], assigned_node_tag[z_count]])
                    self.trans_ele.append([self.element_counter, assigned_node_tag[z_count - 1],
                                           assigned_node_tag[z_count], x_count, tag])
                    self.element_counter += 1

            # link longitudinal elements
            if x_count == 0:
                previous_node_tag = assigned_node_tag
            elif x_count > 0:
                for pre_node in previous_node_tag:
                    for cur_node in assigned_node_tag:
                        cur_z_group = self.node_spec[cur_node]['z_group']
                        prev_z_group = self.node_spec[pre_node]['z_group']
                        if cur_z_group == prev_z_group:
                            tag = self.__get_geo_transform_tag([pre_node, cur_node])
                            self.long_ele.append([self.element_counter, pre_node, cur_node, cur_z_group, tag])
                            self.element_counter += 1
                            break  # break assign long ele loop (cur node)
                # update record for previous node tag step
                previous_node_tag = assigned_node_tag
            # reset counter for next loop
            assigned_node_tag = []
        print("Meshing completed....")

    def __identify_member_groups(self):
        """
        Abstracted method handled by either orthogonal_mesh() or skew_mesh() function
        to identify member groups based on node spacings in orthogonal directions.

        :return: Set variable `group_ele_dict` according to
        """
        # identify element groups in grillage based on line mesh vectors self.nox and self.noz

        # get the grouping properties of nox
        # grouping number, dictionary of unique groups, dict of spacing values for given group as key, list of trib
        # area of nodes
        self.section_group_noz, self.spacing_diff_noz, self.spacing_val_noz, self.noz_trib_width \
            = characterize_node_diff(self.noz, self.decimal_lim)
        self.section_group_nox, self.spacing_diff_nox, self.spacing_val_nox, self.nox_trib_width \
            = characterize_node_diff(self.nox, self.decimal_lim)
        # update self.section_group_nox counter to continue after self.section_group_noz
        self.section_group_nox = [x + max(self.section_group_noz) for x in self.section_group_nox]

    def __get_geo_transform_tag(self, ele_nodes):
        # function called for each element, assign
        node_i = self.node_spec[ele_nodes[0]]['coordinate']
        node_j = self.node_spec[ele_nodes[1]]['coordinate']
        vxz = self.__get_vector_xz(node_i, node_j)
        vxz = [np.round(num, decimals=self.decimal_lim) for num in vxz]
        tag_value = self.transform_dict.setdefault(repr(vxz), self.transform_counter + 1)
        self.transform_counter = tag_value
        return tag_value

    @staticmethod
    def __get_vector_xz(node_i, node_j):
        """
        Encapsulated function to identify a vector parallel to the plane of local x and z axis of the element. The
        vector is required for geomTransf() command
        - see geomTransf_.

        .. _geomTransf: https://openseespydoc.readthedocs.io/en/latest/src/geomTransf.html

        """
        # Function to calculate vector xz used for geometric transformation of local section properties
        # return: vector parallel to plane xz of member (see geotransform Opensees) for skew members (member tag 5)

        # vector rotate 90 deg clockwise (x,y) -> (y,-x)
        # [breadth width] is a vector parallel to skew
        xi = node_j[0] - node_i[0]
        zi = node_j[2] - node_i[2]
        x = zi
        z = -xi
        # normalize vector
        length = math.sqrt(x ** 2 + z ** 2)
        vec = [x / length, z / length]
        return [vec[0], 0, vec[1]]  # here y axis is normal to model plane

    def get_long_grid_nodes(self):
        """
        Abstracted procedure to define the node lines along the transverse (z) direction. Nodes are calculated based on
        number of longitudinal members and edge beam distance. Function is callable from outside class if user requires
        - does not affect the abstracted procedural call in the class.

        return: noz: list of nodes along line in the transverse direction.
        """
        # Function to output array of grid nodes along longitudinal direction
        last_girder = (self.width - self.edge_width)  # coord of last girder
        nox_girder = np.linspace(start=self.edge_width, stop=last_girder, num=self.num_trans_grid)
        noz = np.hstack((np.hstack((0, nox_girder)), self.width))  # array containing z coordinate
        return noz
