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
                 orthogonal=False, pt1=[0, 0], pt2=[0, 0], pt3=[0, 0]):
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
        self.node_counter = 1
        self.element_counter = 1
        self.transform_counter = 0
        self.decimal_lim = 4
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

        # define starting line segment for the length of the mesh (@ z = 0)
        pt3 = [long_dim, 0]
        try:
            d = findCircle(x1=0, y1=0, x2=pt2[0], y2=pt2[1], x3=pt3[0], y3=pt3[1])
            # arc_func()
            self.curve = True
        except ZeroDivisionError:
            print("3 points result in straight line - not a circle")
            d = None
            # procedure to identify straight line segment pinpointing length of grillage
            points = [(pt1[0], pt1[1]), (pt1[0], pt1[1])]
            x_coords, y_coords = zip(*points)
            A = np.vstack([x_coords, np.ones(len(x_coords))]).T
            m, c = np.linalg.lstsq(A, y_coords, rcond=None)[0]

        # define the nodes of construction lines for end spans - left and right ends
        last_girder = (self.width - self.edge_width)  # coord of last girder
        nox_girder = np.linspace(start=self.edge_width, stop=last_girder, num=self.num_long_beam - 2)
        self.noz = np.hstack((np.hstack((0, nox_girder)), self.width))  # array containing z coordinate
        self.ref_node_coor = []
        # x coordinates of ref_node lines
        const_line_x = [z * np.tan(-self.skew / 180 * math.pi) for z in noz]
        # define coordinates of ref nodes on construction line (end span line)
        for (count, xcor) in enumerate(const_line_x):
            self.ref_node_coor.append([xcor, self.y_elevation, self.noz[count]])
        self.nox = np.linspace(0, self.long_dim, self.num_trans_beam)

        # run section grouping for longitudinal and transverse members
        self.__identify_member_groups()
        # create elements
        if self.orthogonal:
            pass
        else:
            for x_count, x_inc in enumerate(self.nox):  #
                for z_count, ref_point in enumerate(self.ref_node_coor):
                    # offset x and y in all points in ref points
                    z_inc = select_segment_function(curve_flag=self.curve, d=d, m=m, c=c, x=x_inc)
                    node_coordinate = [ref_point[0] + x_inc, ref_point[1], ref_point[2] + z_inc]
                    node_tag = self.node_spec.setdefault(self.node_counter,
                                                         {'coordinate': node_coordinate, 'x_group': x_count,
                                                          'z_group': z_count})
                    self.node_counter += 1
        print("t")





    def __skew_mesh(self):
        self.nox = np.linspace(0, self.long_dim, self.num_trans_beam)  # array like containing node x coordinate
        self.breadth = self.trans_dim * math.sin(self.skew / 180 * math.pi)  # length of skew edge in x dir
        self.noz = self.get_long_grid_nodes()  # mesh points in z direction
        # identify member groups based on nox and noz
        self.__identify_member_groups()  # returns section_group_nox and section_group_noz

        # create node map
        for zcount, pointz in enumerate(self.noz):  # loop for each mesh point in z dir
            noxupdate = self.nox - pointz * np.tan(
                self.skew / 180 * math.pi)  # get nox for current step in transverse mesh
            for xcount, pointx in enumerate(noxupdate):  # loop for each mesh point in x dir (nox)
                # populate nodedata array - inputs [nodetag,x,y,z, gridz tag, gridx tag]
                self.node_map.append(
                    [self.node_counter, pointx, self.y_elevation, pointz, zcount,
                     xcount])  # NOTE here is where to change X Y plane
                self.node_counter += 1
        # print to terminal
        print("Nodes created. Number of nodes = {}".format(self.node_counter - 1))

        # create grillage elements by linking nodes
        for node_row_z in range(0, len(self.noz)):  # loop for each line mesh in z direction
            for node_col_x in range(1, len(self.nox)):  # loop for each line mesh in x direction
                current_row_z = node_row_z * len(self.nox)  # get current row's (z axis) node tag
                next_row_z = (node_row_z + 1) * len(self.nox)  # get next row's (z axis) node tag
                # link nodes along current row (z axis), in the x direction
                # elements in a element list: [node_i, node_j, element group, ele tag, geomTransf (1,2 or 3), grid tag]
                tag = self.__get_geo_transform_tag([current_row_z + node_col_x, current_row_z + node_col_x + 1])
                self.long_ele.append([current_row_z + node_col_x, current_row_z + node_col_x + 1,
                                      self.section_group_noz[node_row_z], self.element_counter, tag, node_row_z])
                self.element_counter += 1

                # if looping last row of line mesh z
                if next_row_z == self.node_counter - 1:
                    pass  # do nothing (exceeded the z axis edge of the grillage)
                else:  # assigning elements in transverse direction (z)
                    tag = self.__get_geo_transform_tag([current_row_z + node_col_x, next_row_z + node_col_x])
                    self.trans_ele.append([current_row_z + node_col_x, next_row_z + node_col_x,
                                           self.section_group_nox[node_col_x - 1], self.element_counter, tag,
                                           node_col_x - 1])
                    self.element_counter += 1
            if next_row_z >= len(self.nox) * len(self.noz):  # check if current z coord is last row
                pass  # last column (x = self.nox[-1]) achieved, no more assignment
            else:  # assign last transverse member at last column (x = self.nox[-1])
                tag = self.__get_geo_transform_tag([current_row_z + node_col_x + 1, next_row_z + node_col_x + 1])
                self.trans_ele.append([current_row_z + node_col_x + 1, next_row_z + node_col_x + 1,
                                       self.section_group_nox[node_col_x], self.element_counter, tag, node_col_x])
                # after counting section_group_nox 0 to 11, this line adds the counter of 12
                self.element_counter += 1
        # combine long and trans member elements to global list
        self.global_element_list = self.long_ele + self.trans_ele
        print("Element generation completed. Number of elements created = {}".format(self.element_counter - 1))
        # save elements and nodes to mesh object
        # return
        # element_dict
        # node dict

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
        node_i = [x for x in self.node_map if x[0] == ele_nodes[0]]
        node_j = [x for x in self.node_map if x[0] == ele_nodes[1]]
        vxz = self.__get_vector_xz(node_i[0], node_j[0])
        vxz = np.round(vxz, decimals=self.decimal_lim)
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
        xi = node_j[1] - node_i[1]
        zi = node_j[3] - node_i[3]
        x = zi
        z = -(-xi)
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
