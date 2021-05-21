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
                 transform_counter=0, global_x_grid_count=0, global_edge_count=0, mesh_origin=[0, 0, 0]):
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
        # counters to keep track of variables
        self.node_counter = element_counter
        self.element_counter = node_counter
        self.transform_counter = transform_counter
        self.global_x_grid_count = global_x_grid_count
        # variables for identifying edge of mesh/model
        self.global_edge_count = global_edge_count
        self.edge_node_recorder = dict()  # key: node tag, val: unique tag for edge
        # variables to remember counters for node tags
        assigned_node_tag = []
        self.decimal_lim = 3  # variable for floating point arithmetic error
        self.curve = False
        # initiate list for nodes and elements
        self.long_ele = []
        self.trans_ele = []
        self.edge_span_ele = []
        self.y_elevation = 0
        self.mesh_design_line = []
        # dict for node and ele transform
        self.transform_dict = dict()  # key: vector xz, val: transform tag
        self.node_spec = dict()  # key: node tag, val: dict of node details - see technical notes
        self.x_group_dict = dict()
        self.z_group_dict = dict()
        # variables for curve mesh
        self.curve_center = []
        self.curve_radius = []
        # line / circle equation variables
        self.m = 0
        self.c = 0
        self.r = 0
        self.R = 0
        # meshing properties
        self.mesh_origin = mesh_origin  # default origin

        # ------------------------------------------------------------------------------------------
        # Sweep path of mesh
        pt3 = [long_dim, 0.0]  # 3rd point for defining curve mesh

        # if defining an arc line segment, specify p2 such that pt2 is the point at the midpoint of the arc
        try:
            self.d = findCircle(x1=0, y1=0, x2=pt2[0], y2=pt2[1], x3=pt3[0], y3=pt3[1])
            self.curve = True
            # TODO find zeta for arbitrary function
            zeta = 0
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
            zeta = np.arctan(m)  # initial angle of inclination of sweep line about mesh origin
            # if abs(zeta) > abs(self.skew/180 * np.pi):
            # raise Exception("Initial inclination of sweep path at mesh origin ({}) too large - greater than skew of edge ({})".format(zeta,self.skew))

        # ------------------------------------------------------------------------------------------
        # edge construction line 1
        edge_ref_point = self.mesh_origin
        last_girder = (self.width - self.edge_width)  # coord of last girder
        nox_girder = np.linspace(start=self.edge_width, stop=last_girder, num=self.num_long_beam - 2)
        # array containing z coordinate of edge construction line
        self.noz = np.hstack((np.hstack((0, nox_girder)), self.width))
        edge_node_x = [np.abs((z * np.tan(self.skew / 180 * np.pi))) for z in self.noz]
        if self.skew <= 0:
            self.edge_construction_line = [[x + edge_ref_point[0], y + edge_ref_point[1], z + edge_ref_point[2]] for
                                           x, y, z in
                                           zip(edge_node_x, [self.y_elevation] * len(self.noz), self.noz)]
        else:
            self.edge_construction_line = [[x + edge_ref_point[0], y + edge_ref_point[1], z + edge_ref_point[2]] for
                                           x, y, z in
                                           zip(edge_node_x, [self.y_elevation] * len(self.noz), np.flip(self.noz))]
        # ------------------------------------------------------------------------------------------
        # edge construction line 2

        # ------------------------------------------------------------------------------------------
        # Sweep nodes
        self.sweeping_nodes = []
        if orthogonal:
            self.sweeping_nodes = self.__rotate_sweep_nodes(zeta)

        else:  # skew
            # sweep line of skew mesh == edge_construction line
            self.sweeping_nodes = self.edge_construction_line
        # ------------------------------------------------------------------------------------------
        # Sweep path
        # TODO: Self.nox becomes the sweep path, self.nox holds x coordinate along the sweep path
        self.nox = np.linspace(0, self.long_dim, self.num_trans_beam)

        # --------------------------------------------------------------------------------------------------
        # 2.1 check validity of construction line + sweep line
        # for all combination, zeta must be less than self.skew
        # if zeta >= self.skew
        # then it works
        # run section grouping for longitudinal and transverse members
        self.__identify_member_groups()

        # ------------------------------------------------------------------------------------------
        # create nodes and elements
        # if orthogonal, orthogonal mesh only be splayed onto a curve mesh, if skew mesh curved/arc line segment must be
        # false
        if self.orthogonal:
            # mesh start span construction line region
            self.__orthogonal_meshing()
            # mesh uniform region

            # mesh end span construction line region

        elif not self.curve:  # Skew mesh + angle
            self.__skew_meshing()

    def __skew_meshing(self):
        assigned_node_tag = []
        previous_node_tag = []
        for x_count, x_inc in enumerate(self.nox):
            for z_count, ref_point in enumerate(self.sweeping_nodes):
                # offset x and y in all points in ref points
                z_inc = np.round(
                    select_segment_function(curve_flag=self.curve, d=self.d, m=self.m, c=self.m, x=x_inc, r=self.r),
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
                # record
                for nodes in previous_node_tag:
                    self.edge_node_recorder.setdefault(nodes, self.global_edge_count)
                self.global_edge_count += 1
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
                if x_count == len(self.nox) - 1:
                    for nodes in previous_node_tag:
                        self.edge_node_recorder.setdefault(nodes, self.global_edge_count)
                    self.global_edge_count += 1
            # reset counter for next loop

            assigned_node_tag = []
        print("Meshing completed....")

    def __orthogonal_meshing(self):
        self.assigned_node_tag = []
        self.previous_node_tag = []
        self.edge_node_group = dict()

        # start at first construction line
        if self.skew < 0:
            m_edge, c_edge = get_line_func(self.skew, self.sweeping_nodes[0])
        else:
            m_edge, c_edge = get_line_func(self.skew, self.sweeping_nodes[-1])

        for z_count, int_point in enumerate(self.edge_construction_line):
            # search point on sweep path line whose normal intersects int_point.
            start_point_x = self.mesh_origin[0]
            ref_point_x, ref_point_z = self.__search_x_point(int_point, start_point_x)
            # find m' of line between intersect int_point and ref point on sweep path   #TODO here for straight line
            m_primt,phi = get_slope([ref_point_x,self.y_elevation,ref_point_z], int_point)
            # rotate sweep line such that parallel to m' line
            current_sweep_nodes = self.__rotate_sweep_nodes(np.pi/2 - np.abs(phi))
            # loop for each z count, assign
            if m_edge < 0:
                sweep_nodes = current_sweep_nodes[(z_count+1):]
            else:
                sweep_nodes = current_sweep_nodes[0:(z_count+1)]
            for (z_count_int, nodes) in enumerate(sweep_nodes):
                x_inc = ref_point_x
                z_inc = ref_point_z
                node_coordinate = [nodes[0] + x_inc, nodes[1],nodes[2]+z_inc]
                self.node_spec.setdefault(self.node_counter, {'tag': self.node_counter, 'coordinate': node_coordinate,
                                                              'x_group': self.global_x_grid_count,
                                                              'z_group': z_count_int})

                self.assigned_node_tag.append(self.node_counter)
                self.node_counter += 1
                # link transverse members
                if z_count_int > 0:
                    # element list [element tag, node i, node j, x/z group]

                    self.__assign_transverse_members(pre_node=self.assigned_node_tag[z_count_int - 1],
                                                     cur_node=self.assigned_node_tag[z_count_int])

            # link longitudinal elements and edge members
            if z_count == 0:
                self.previous_node_tag = self.assigned_node_tag
            if z_count > 0:
                for pre_node in self.previous_node_tag:
                    for cur_node in self.assigned_node_tag:
                        cur_z_group = self.node_spec[cur_node]['z_group']
                        prev_z_group = self.node_spec[pre_node]['z_group']
                        if cur_z_group == prev_z_group:
                            self.__assign_longitudinal_members(pre_node=pre_node, cur_node=cur_node,
                                                               cur_z_group=cur_z_group)
                            break  # break assign long ele loop (cur node)
                # link edge members
                self.edge_node_recorder.setdefault(self.previous_node_tag[-1], self.global_edge_count)
                self.edge_node_recorder.setdefault(self.assigned_node_tag[-1], self.global_edge_count)
                # for edge node - linking depends on slope of edge construction line
                if m_edge<0:
                    self.__assign_edge_trans_members(self.previous_node_tag[0], self.assigned_node_tag[0])
                else:
                    self.__assign_edge_trans_members(self.previous_node_tag[-1], self.assigned_node_tag[-1])
                # update recorder for previous node tag step
                self.previous_node_tag = self.assigned_node_tag
            # update and reset recorders for next sweep point x
            self.global_x_grid_count += 1
            self.ortho_previous_node_column = self.assigned_node_tag
            self.assigned_node_tag = []
        self.global_edge_count += 1

        print("Orthogonal meshing completed....")



    # ------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------
    def __assign_transverse_members(self, pre_node, cur_node):
        tag = self.__get_geo_transform_tag([pre_node, cur_node])
        self.trans_ele.append([self.element_counter, pre_node, cur_node, self.global_x_grid_count, tag])
        self.element_counter += 1

    def __assign_longitudinal_members(self, pre_node, cur_node, cur_z_group):
        tag = self.__get_geo_transform_tag([pre_node, cur_node])
        self.long_ele.append([self.element_counter, pre_node, cur_node, cur_z_group, tag])
        self.element_counter += 1

    def __assign_edge_trans_members(self, previous_node_tag, assigned_node_tag):
        tag = self.__get_geo_transform_tag([previous_node_tag, assigned_node_tag])
        self.edge_span_ele.append([self.element_counter, previous_node_tag, assigned_node_tag
                                      , self.edge_node_recorder, tag])
        self.element_counter += 1

    # ------------------------------------------------------------------------------------------
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

    # ------------------------------------------------------------------------------------------
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
        length = np.sqrt(x ** 2 + z ** 2)
        x1 = x / length

        z1 = z / length
        return [x1, 0, z1]  # here y axis is normal to model plane

    def __rotate_sweep_nodes(self,zeta):
        sweep_nodes_x = [0] * len(self.noz)  # line is orthogonal at the start of sweeping path
        # rotate for inclination at origin
        sweep_nodes_x = [x * np.cos(zeta) - y * np.sin(zeta) for x, y in zip(sweep_nodes_x, self.noz)]
        sweep_nodes_z = [y * np.cos(zeta) + x * np.sin(zeta) for x, y in zip(sweep_nodes_x, self.noz)]
        if self.skew <= 0:
            sweeping_nodes = [[x + self.mesh_origin[0], y + self.mesh_origin[1], z + self.mesh_origin[2]] for x, y, z
                                   in
                                   zip((sweep_nodes_x), [self.y_elevation] * len(self.noz), sweep_nodes_z)]
        else:
            sweeping_nodes = [[x + self.mesh_origin[0], y + self.mesh_origin[1], z + self.mesh_origin[2]] for x, y, z
                                   in
                                   zip(np.abs(sweep_nodes_x), [self.y_elevation] * len(self.noz),
                                       np.flip(sweep_nodes_z))]
        return sweeping_nodes

    def __search_x_point(self, int_point, start_point_y=0, line_function=None):
        start_point_x = int_point[0]
        min_found = False
        max_loop = 1000
        loop_counter = 0
        min_d = None
        # TODO magic number here
        inc = 0.001
        convergence_check = []
        bounds = []
        while not min_found:
            z0 = line_func(m=self.m, c=self.c, x=start_point_x)  # TODO HERE SET to allow search sweep line function
            d0 = find_min_x_dist([int_point], [[start_point_x, self.y_elevation, z0]]).tolist()

            z_ub = line_func(m=self.m, c=self.c, x=start_point_x+inc)
            d_ub = find_min_x_dist([int_point], [[start_point_x+inc, self.y_elevation, z_ub]]).tolist()

            z_lb = line_func(m=self.m, c=self.c, x=start_point_x-inc)
            d_lb = find_min_x_dist([int_point], [[start_point_x - inc, self.y_elevation, z_lb]]).tolist()

            if d_lb>d0 and d_ub>d0:
                min_found = True
            elif d_lb<d0 and d_ub>d0:
                start_point_x = start_point_x - inc
            elif d_lb>d0 and d_ub<d0:
                start_point_x = start_point_x + inc
            # perform convergence test
            # convergence_check.append([d[0] / np.abs(z) if z != 0 else 0])
            # if len(convergence_check) > 2:
            #     if convergence_check[loop_counter]< convergence_check[loop_counter-1]:
            #         pass
            #     else:
            #         raise Exception("value diverges")
            loop_counter += 1
            if loop_counter > max_loop:
                break

        return start_point_x, z0
