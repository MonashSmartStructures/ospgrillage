import math
import openseespy.opensees as ops
from datetime import datetime
from collections import defaultdict
from Load import *
from Material import *
from member_sections import *
from Mesh import *
from itertools import combinations


class OpsGrillage:
    """
    Main class of Openseespy grillage model wrapper. Outputs an executable py file which generates the prescribed
    Opensees grillage model based on user input.

    The class provides an interface for the user to specify the geometry of the grillage model. A keyword argument
    allows for users to select between skew/oblique or orthogonal mesh. Methods in this class allows users to input
    properties for various elements in the grillage model.

    Example usage:
    example_bridge = OpsGrillage(bridge_name="SuperT_10m", long_dim=10, width=7, skew=-42,
                             num_long_grid=7, num_trans_grid=5, edge_beam_dist=1, mesh_type="Ortho")
    """

    def __init__(self, bridge_name, long_dim, width, skew, num_long_grid,
                 num_trans_grid, edge_beam_dist, mesh_type="Ortho", op_instance=True, model="3D", **kwargs):
        """
        Variables pertaining model information
        :param bridge_name: Name of bridge model and output .py file
        :type bridge_name: str
        :param long_dim: Length of the model in the longitudinal direction (default: x axis)
        :type long_dim: int or float
        :param width: Width of the model in the transverse direction (default: z axis)
        :type width: int or float
        :param skew: Skew angle of model
        :type skew: int or float
        :param num_long_grid: Number of node points in the longitudinal direction
        :type num_long_grid: int
        :param num_trans_grid: Number of node points in the transverse direction
        :type num_trans_grid: int
        :param edge_beam_dist: Distance of edge beam node lines to exterior main beam node lines
        :type edge_beam_dist: int or float
        :param mesh_type: Type of mesh
        :type mesh_type: string

        """

        self.global_load_str = []
        self.global_patch_int_dict = dict()
        self.mesh_type = mesh_type
        self.model_name = bridge_name
        self.op_instance_flag = op_instance
        self.long_dim = long_dim  # span , also c/c between support bearings
        self.width = width  # length of the bearing support - if skew  = 0 , this corresponds to width of bridge
        # if skew is a list containing 2 skew angles, set start and end edge of span to have respective angles
        if isinstance(skew, list):
            self.skew_a = skew[0]
            if len(skew) >= 2:
                self.skew_b = skew[1]
        else:  # set skew_a and skew_b variables to equal
            self.skew_a = skew  # angle in degrees
            self.skew_b = skew  # angle in degrees

        self.num_long_gird = num_long_grid  # number of longitudinal beams
        self.num_trans_grid = num_trans_grid  # number of grids for transverse members
        self.edge_width = edge_beam_dist  # width of cantilever edge beam
        # instantiate matrices for geometric dependent properties
        self.trans_dim = None  # to be calculated automatically based on skew
        self.global_mat_object = []  # material matrix
        self.global_line_int_dict = []
        # Section placeholders
        self.section_arg = None
        self.section_tag = None
        self.section_type = None

        # dict
        self.ele_group_assigned_list = []  # list recording assigned ele groups in grillage model
        self.section_dict = {}  # dictionary of section tags
        self.material_dict = {}  # dictionary of material tags

        # collect mesh groups
        self.mesh_group = []  # for future release
        if self.mesh_type == "Ortho":
            self.ortho_mesh = True
        else:
            self.ortho_mesh = False
        # rules for grillage automation - default values are in place, use keyword during class instantiation
        self.grillage_rules_dict = dict()
        self.grillage_rules_dict['min_long_spacing'] = kwargs.get('min_long_spacing', 1)
        self.grillage_rules_dict['max_long_spacing'] = kwargs.get('max_long_spacing', 1)
        self.grillage_rules_dict['min_trans_spacing'] = kwargs.get('min_trans_spacing', 1)
        self.grillage_rules_dict['max_trans_spacing'] = kwargs.get('max_trans_spacing', 1)
        self.grillage_rules_dict['aspect_ratio'] = kwargs.get('aspect_ratio', 1)

        self.y_elevation = 0  # default model plane is orthogonal plane of y = 0
        self.min_grid_ortho = 3  # for orthogonal mesh (skew>skew_threshold) region of orthogonal area default 3

        if model == "2D":
            self.__ndm = 2  # num model dimension - default 3
            self.__ndf = 3  # num degree of freedom - default 6
        else:
            self.__ndm = 3  # num model dimension - default 3
            self.__ndf = 6  # num degree of freedom - default 6

        # default vector for standard (for 2D grillage in x - z plane) - 1 represent fix for [Vx,Vy,Vz, Mx, My, Mz]
        self.fix_val_pin = [1, 1, 1, 0, 0, 0]  # pinned
        self.fix_val_roller_x = [0, 1, 1, 0, 0, 0]  # roller
        # special rules for grillage - alternative to Properties of grillage definition - use for special dimensions
        self.skew_threshold = [10, 30]  # threshold for grillage to allow option of mesh choices
        self.deci_tol = 4  # tol of decimal places
        self.while_loop_max = 100

        # dict for load cases and load types
        self.load_case_list = []  # list of dict, example [{'loadcase':LoadCase object, 'load_command': list of str}..]
        self.load_combination_dict = dict()  # example {0:[{'loadcase':LoadCase object, 'load_command': list of str},
        # {'loadcase':LoadCase object, 'load_command': list of str}....]}
        self.moving_load_case_dict = dict()  # example [ list of load_case_dict]
        self.moving_load_case_list = []  # list of dict  # example [ list of load_case_dict]
        # counters to keep track of objects for loading
        self.load_case_counter = 1
        self.load_combination_counter = 1
        self.moving_load_case_counter = 1

        # Initiate py file output
        self.filename = "{}_op.py".format(self.model_name)
        # create namedtuples

        # calculate edge length of grillage
        self.trans_dim = self.width / math.cos(self.skew_a / 180 * math.pi)

        # objects and pyfile flag
        self.Mesh_obj = None
        self.pyfile = None

    def create_ops(self, pyfile=False):
        """
        Main function to create ops model instance or output pyfile for model instance
        :param pyfile: Boolean to flag either ops instance or pyfile output

        """
        self.pyfile = pyfile

        if self.pyfile:
            with open(self.filename, 'w') as file_handle:
                # create py file or overwrite existing
                # writing headers and description at top of file
                file_handle.write("# Grillage generator wizard\n# Model name: {}\n".format(self.model_name))
                # time
                now = datetime.now()
                dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
                file_handle.write("# Constructed on:{}\n".format(dt_string))
                # write imports
                file_handle.write("import numpy as np\nimport math\nimport openseespy.opensees as ops"
                                  "\nimport openseespy.postprocessing.Get_Rendering as opsplt\n")
        # model() command
        self.__write_op_model()
        # create grillage mesh object
        self.__run_mesh_generation()

    # function to run mesh generation
    def __run_mesh_generation(self):

        self.Mesh_obj = Mesh(self.long_dim, self.width, self.trans_dim, self.edge_width, self.num_trans_grid,
                             self.num_long_gird,
                             self.skew_a, skew_2=self.skew_b, orthogonal=self.ortho_mesh)

        # 2 generate command lines in output py file
        self.__write_op_node(self.Mesh_obj)  # write node() commands
        self.__write_op_fix(self.Mesh_obj)  # write fix() command for support nodes
        self.__write_geom_transf(self.Mesh_obj)  # x dir members
        # 3 identify boundary of mesh

    def set_boundary_condition(self, edge_group_counter=[1], restraint_vector=[0, 1, 0, 0, 0, 0], group_to_exclude=[0]):
        """
        Function for user to modify boundary conditions of the grillage model. Edge nodes are automatically detected
        and recorded as having fixity in vertical y direction.
        """
        pass

    # abstracted procedures to write ops commands to output py file. All functions are private and named with "__write"
    def __write_geom_transf(self, mesh_obj, transform_type="Linear"):
        """
        Abstracted procedure to write ops.geomTransf() to output py file.
        :param transform_type: transformation type
        :type transform_type: str

        :return: Writes ops.geomTransf() line to output py file
        """

        for k, v in mesh_obj.transform_dict.items():
            if self.pyfile:
                with open(self.filename, 'a') as file_handle:
                    file_handle.write("# create transformation {}\n".format(v))
                    file_handle.write("ops.geomTransf(\"{type}\", {tag}, *{vxz})\n".format(
                        type=transform_type, tag=v, vxz=eval(k)))
            else:
                ops.geomTransf(transform_type, v, *eval(k))

    def __write_op_model(self):
        """
        Sub-abstracted procedure handled by create_nodes() function. This method creates the model() command
        in the output py file.

        :return: Output py file with wipe() and model() commands

        Note: For 3-D model, the default model dimension and node degree-of-freedoms are 3 and 6 respectively.
        This method automatically sets the aforementioned parameters to 2 and 4 respectively, for a 2-D problem.
        """
        # write model() command
        if self.pyfile:
            with open(self.filename, 'a') as file_handle:
                file_handle.write("ops.wipe()\n")
                file_handle.write(
                    "ops.model('basic', '-ndm', {ndm}, '-ndf', {ndf})\n".format(ndm=self.__ndm, ndf=self.__ndf))
        else:
            ops.wipe()
            ops.model('basic', '-ndm', self.__ndm, '-ndf', self.__ndf)

    def __write_op_node(self, mesh_obj):
        """
        Sub-abstracted procedure handled by create_nodes() function. This method create node() command for each node
        point generated during meshing procedures.

        :return: Output py file populated with node() commands to generated the prescribed grillage model.
        """
        # write node() command
        if self.pyfile:
            with open(self.filename, 'a') as file_handle:
                file_handle.write("# Model nodes\n")

        for k, nested_v, in mesh_obj.node_spec.items():
            coordinate = nested_v['coordinate']
            if self.pyfile:
                with open(self.filename, 'a') as file_handle:
                    file_handle.write("ops.node({tag}, {x:.4f}, {y:.4f}, {z:.4f})\n".format(tag=nested_v['tag'],
                                                                                            x=coordinate[0],
                                                                                            y=coordinate[1],
                                                                                            z=coordinate[2]))
            else:  # 0 - x , 1 - y, 2 - z
                ops.node(nested_v['tag'], coordinate[0], coordinate[1], coordinate[2])

    def __write_op_fix(self, mesh_obj):
        """
        Abstracted procedure handed by create_nodes() function. This method writes the fix() command for
        boundary condition definition in the grillage model.

        :return: Output py file populated with fix() command for boundary condition definition.
        """
        if self.pyfile:
            with open(self.filename, 'a') as file_handle:
                file_handle.write("# Boundary condition implementation\n")
            # TODO generalize for user input of boundary condition
        for node_tag, edge_group_num in mesh_obj.edge_node_recorder.items():
            # if node is an edge beam - is part of common group z ==0 ,do not assign any fixity
            if mesh_obj.node_spec[node_tag]["z_group"] in mesh_obj.common_z_group_element[0]:  # here [0] is first group
                pass  # move to next node in edge recorder
            elif edge_group_num == 0:  # 0 is edge of start of span
                if self.pyfile:  # if writing py file
                    with open(self.filename, 'a') as file_handle:
                        file_handle.write("ops.fix({}, *{})\n".format(node_tag, self.fix_val_pin))
                else:  # run instance
                    ops.fix(node_tag, *self.fix_val_pin)
            elif edge_group_num == 1:  # 1 is edge of end of span
                if self.pyfile:  # if writing py file
                    with open(self.filename, 'a') as file_handle:
                        file_handle.write("ops.fix({}, *{})\n".format(node_tag, self.fix_val_roller_x))
                else:  # run instance
                    ops.fix(node_tag, *self.fix_val_roller_x)

    def __write_uniaxial_material(self, member=None, material=None):
        """
        Sub-abstracted procedure to write uniaxialMaterial command for the material properties of the grillage model.

        :return: Output py file with uniaxialMaterial() command
        """
        # function to generate uniaxialMaterial() command in output py file
        # ops.uniaxialMaterial(self.mat_type_op, 1, *self.mat_matrix)

        if member is None and material is None:
            raise Exception("Uniaxial material has no input GrillageMember or Material Object")
        if member is None:
            material_obj = material  # str of section type - Openseespy convention

        elif material is None:
            material_obj = member.material  # str of section type - Openseespy convention
        material_type = material_obj.mat_type
        op_mat_arg = material_obj.mat_vec

        # - write unique material tag and input argument as keyword of dict
        material_str = [material_type, op_mat_arg]  # repr both variables as a list for keyword definition
        # if section is specified, get the materialtagcounter for material() assignment
        if not bool(self.material_dict):
            lastmaterialtag = 0  # if dict empty, start counter at 1
        else:  # set materialtagcounter as the latest defined element - i.e. max of section_dict
            lastmaterialtag = self.material_dict[list(self.material_dict)[-1]]

        # if section has been assigned
        material_tag = self.material_dict.setdefault(repr(material_str), lastmaterialtag + 1)
        if material_tag != lastmaterialtag:
            mat_str = "ops.uniaxialMaterial(\"{type}\", {tag}, *{vec})\n".format(
                type=material_type, tag=material_tag, vec=op_mat_arg)
            if self.pyfile:
                with open(self.filename, 'a') as file_handle:
                    file_handle.write("# Material definition \n")
                    file_handle.write(mat_str)
            else:
                eval(mat_str)
        else:
            print("Material {} with tag {} has been previously defined"
                  .format(material_type, material_tag))
            return material_tag

    def __write_section(self, op_section_obj):
        """
        Abstracted procedure handled by set_member() function to write section() command for the elements. This method
        is ran only when GrillageMember object requires section() definition following convention of Openseespy.

        """
        # extract section variables from Section class
        section_type = op_section_obj.op_section_type  # str of section type - Openseespy convention
        # section argument
        section_arg = op_section_obj.get_asterisk_arguments()  # list of argument for section - Openseespy convention
        section_str = [section_type, section_arg]  # repr both variables as a list for keyword definition
        # if section is specified, get the sectiontagcounter for section assignment
        if not bool(self.section_dict):
            lastsectioncounter = 0  # if dict empty, start counter at 0
        else:  # dict not empty, get default value as latest defined tag
            lastsectioncounter = self.section_dict[list(self.section_dict)[-1]]
        # if section has been assigned
        sectiontagcounter = self.section_dict.setdefault(repr(section_str), lastsectioncounter + 1)
        if sectiontagcounter != lastsectioncounter:
            sec_str = "ops.section(\"{}\", {}, *{})\n".format(section_type, sectiontagcounter, section_arg)
            if self.pyfile:
                with open(self.filename, 'a') as file_handle:
                    file_handle.write("# Create section: \n")
                    file_handle.write(
                        sec_str)
            else:
                eval(sec_str)
            # print to terminal
            print("Section {}, of tag {} created".format(section_type, sectiontagcounter))
        else:
            print("Section {} with tag {} has been previously defined"
                  .format(section_type, sectiontagcounter))
        return sectiontagcounter

    # Function to set grillage elements
    def set_member(self, grillage_member_obj, member=None):
        """
        Function to set grillage member class object to elements of grillage members.
        :param grillage_member_obj: Grillage_member class object
        :param member: str of member category - select from standard grillage elements
                        - interior beam
                        - exterior beam
                        - edge beam
                        - slab
                        - diaphragm
        :return: sets member object to element of grillage in OpsGrillage instance
        """
        # if write flag, write header of element assignment
        if self.pyfile:
            with open(self.filename, 'a') as file_handle:
                file_handle.write("# Element generation for section: {}\n".format(member))
        z_flag = False
        x_flag = False
        edge_flag = False
        common_member_tag = []
        if member == "interior_main_beam":
            common_member_tag = 2
            z_flag = True
        elif member == "exterior_main_beam_1":
            common_member_tag = 1
            z_flag = True
        elif member == "exterior_main_beam_2":
            common_member_tag = 3
            z_flag = True
        elif member == "edge_beam":
            common_member_tag = 0
            z_flag = True
        elif member == "start_edge":
            common_member_tag = 0
            edge_flag = True
        elif member == "end_edge":
            common_member_tag = 1
            edge_flag = True
        else:
            common_member_tag = None

        ele_width = 1
        # if member is transverse, assign slab elements
        if grillage_member_obj.section.unit_width and common_member_tag is None:
            for ele in self.Mesh_obj.trans_ele:
                n1 = ele[1]
                n2 = ele[2]
                # get node_i and node_j spacing
                lis_1 = self.Mesh_obj.node_width_x_dict[n1]
                lis_2 = self.Mesh_obj.node_width_x_dict[n2]
                ele_width = 1
                ele_width_record = []
                for lis in [lis_1, lis_2]:
                    if len(lis) == 1:
                        ele_width_record.append(np.sqrt(lis[0][0] ** 2 + lis[0][1] ** 2 + lis[0][2] ** 2) / 2)
                    elif len(lis) == 2:
                        ele_width_record.append((np.sqrt(lis[0][0] ** 2 + lis[0][1] ** 2 + lis[0][2] ** 2) +
                                                 np.sqrt(lis[1][0] ** 2 + lis[1][1] ** 2 + lis[1][2] ** 2)) / 2)
                    else:
                        break
                ele_width = max(
                    ele_width_record)  # TODO Check here, if member lies between a triangular and quadrilateral grid
                # currently here assumed the width of rectangular grid for entrie element width

                ele_str = grillage_member_obj.section.get_element_command_str(
                    ele_tag=ele[0], n1=n1, n2=n2, transf_tag=ele[4], ele_width=ele_width)
                if self.pyfile:
                    with open(self.filename, 'a') as file_handle:
                        file_handle.write(ele_str)
                else:
                    eval(ele_str)
        else:
            # loop each element z group assigned under common_member_tag
            if z_flag:
                for z_groups in self.Mesh_obj.common_z_group_element[common_member_tag]:
                    # assign properties to elements in z group
                    for ele in self.Mesh_obj.z_group_to_ele[z_groups]:
                        ele_str = grillage_member_obj.section.get_element_command_str(
                            ele_tag=ele[0], n1=ele[1], n2=ele[2], transf_tag=ele[4], ele_width=ele_width)
                        if self.pyfile:
                            with open(self.filename, 'a') as file_handle:
                                file_handle.write(ele_str)
                        else:
                            eval(ele_str)
                    self.ele_group_assigned_list.append(z_groups)
            elif edge_flag:

                for ele in self.Mesh_obj.edge_span_ele:
                    if ele[3] == common_member_tag:
                        ele_str = grillage_member_obj.section.get_element_command_str(
                            ele_tag=ele[0], n1=ele[1], n2=ele[2], transf_tag=ele[4], ele_width=ele_width)
                        if self.pyfile:
                            with open(self.filename, 'a') as file_handle:
                                file_handle.write(ele_str)
                        else:
                            eval(ele_str)
                    self.ele_group_assigned_list.append("edge: {}".format(common_member_tag))
        # write member's section command
        if grillage_member_obj.section.section_command_flag:
            section_tag = self.__write_section(grillage_member_obj.section)
        # write member's material command
        material_tag = self.__write_uniaxial_material(member=grillage_member_obj)

    # function to set material obj of grillage model. When called by user,
    def set_material(self, material_obj):
        """
        Function to define a global material model. This function proceeds to write write the material() command to
        output file. By default, function is only called and handled within set_member function. When called by user,
        function creates a material object instance to be set for the ops-grillage instance.

        :return: Function populates object variables: (1) mat_matrix, and (2) mat_type_op.
        """
        # set material to global material object
        self.global_mat_object = material_obj  # material matrix for

        # write uniaxialMaterial() command to output file
        self.__write_uniaxial_material(material=material_obj)

    # ---------------------------------------------------------------
    # Function to find nodes or grids correspond to a point or line - called within OpsGrillage for distributing
    # loads to grillage nodes

    # private procedure to find elements within a grid
    def __get_elements(self, node_tag_combo):
        # abstracted procedure to find and return the long and trans elements within a grid of 4 or 3 nodes
        record_long = []
        record_trans = []
        record_edge = []
        for combi in node_tag_combo:
            long_mem_index = [i for i, x in
                              enumerate([combi[0] in n[1:3] and combi[1] in n[1:3] for n in self.Mesh_obj.long_ele])
                              if x]
            trans_mem_index = [i for i, x in enumerate(
                [combi[0] in n[1:3] and combi[1] in n[1:3] for n in self.Mesh_obj.trans_ele]) if x]
            edge_mem_index = [i for i, x in enumerate(
                [combi[0] in n[1:3] and combi[1] in n[1:3] for n in self.Mesh_obj.edge_span_ele]) if x]
            record_long = record_long + long_mem_index  # record
            record_trans = record_trans + trans_mem_index  # record
            record_edge = record_edge + edge_mem_index
        return record_long, record_trans, record_edge

    # Getter for Points Loads nodes
    def get_point_load_nodes(self, point):
        # procedure
        # 1 find the closest node 2 find the respective grid within the closest node
        # extract points
        loading_point = None
        grid = None
        if type(point) is float or type(point) is list:
            x = point[0]
            y = point[1]  # default y = self.y_elevation = 0
            z = point[2]
            # set point to tuple
            loading_point = Point(x, y, z)
        elif isinstance(point, LoadPoint):
            loading_point = point
        for grid_tag, grid_nodes in self.Mesh_obj.grid_number_dict.items():
            # get grid nodes coordinate as named tuple Point
            point_list = []
            for node_tag in grid_nodes:
                coord = self.Mesh_obj.node_spec[node_tag]['coordinate']
                coord_point = Point(coord[0], coord[1], coord[2])
                point_list.append(coord_point)
            if check_point_in_grid(loading_point, point_list):
                node_list = point_list
                grid = grid_tag

        node_list = self.Mesh_obj.grid_number_dict.get(grid, None)
        return node_list, grid  # n3 = grid number

    # Getter for Line loads nodes
    def get_line_load_nodes(self, line_load_obj) -> dict:
        # uses a modified Bresenham's Line Algorithm to search for grids which lineload intersects
        # from starting point of line load
        # initiate variables
        current_grid = []
        next_grid = []
        x = 0
        z = 0
        x_start = []
        z_start = []
        m = line_load_obj.m
        c = line_load_obj.c
        # find grids where start point of line load lies in
        start_nd, current_grid = self.get_point_load_nodes(line_load_obj.load_point_1)
        last_nd, last_grid = self.get_point_load_nodes(line_load_obj.line_end_point)

        line_grid_intersect = dict()
        # loop each grid check if line has segments within the grids
        for grid_tag, grid_nodes in self.Mesh_obj.grid_number_dict.items():
            point_list = []
            # get coordinates of node points in grids - point_list
            for node_tag in grid_nodes:
                coord = self.Mesh_obj.node_spec[node_tag]['coordinate']
                coord_point = Point(coord[0], coord[1], coord[2])
                point_list.append(coord_point)
            # get long, trans and edge elements in the grids, # get index to lookup respective lists in Mesh.obj
            element_combi = combinations(grid_nodes, 2)
            long_ele_index, trans_ele_index, edge_ele_index = self.__get_elements(element_combi)

            # loop through four nodes in grid
            for points in point_list:
                if line_load_obj.m is None:
                    z_start = points.z
                    x_start = line_load_obj.get_line_segment_given_z(z_start)
                    if x_start is None:
                        continue
                else:
                    x_start = points.x
                    z_start = line_load_obj.get_line_segment_given_x(x_start)
                    if z_start is None:
                        continue

                grid_inter_points = []
                line_point = Point(x_start, points.y, z_start)

                if check_point_in_grid(inside_point=line_point, point_list=point_list):

                    # find intersecting points within grid
                    Rz, Rx, Redge = self.__get_intersecting_elements(grid_tag, current_grid, last_grid, line_load_obj,
                                                                     long_ele_index, trans_ele_index, edge_ele_index)

                    grid_inter_points += Rz + Rx + Redge
                    # check if point is not double assigned
                    if grid_tag not in line_grid_intersect.keys():
                        line_grid_intersect.setdefault(grid_tag, grid_inter_points)

        # update line_grid_intersect by removing grids if line conincide with elements and multiple grids of vicinity
        # grids are returned with same values
        removed_key = []
        edited_dict = line_grid_intersect.copy()
        for grid_key, int_list in line_grid_intersect.items():
            if grid_key not in removed_key:
                check_dup_list = [int_list == val for val in line_grid_intersect.values()]
                if sum(check_dup_list) > 1:
                    # check if grid key is a vicinity grid of current grid_key
                    for dup_key in [key for (count, key) in enumerate(line_grid_intersect.keys()) if
                                    check_dup_list[count] and key is not grid_key]:
                        if dup_key in [current_grid, last_grid]:
                            continue
                        elif dup_key in self.Mesh_obj.grid_vicinity_dict[grid_key].values():
                            removed_key.append(dup_key)
                            del edited_dict[dup_key]

        # update line_grid_intersect adding start and end points into the lists
        for grid_key, int_list in edited_dict.items():
            if grid_key == current_grid:
                edited_dict[grid_key] += [
                    [line_load_obj.load_point_1.x, line_load_obj.load_point_1.y,
                     line_load_obj.load_point_1.z]]
            elif grid_key == last_grid:
                edited_dict[grid_key] += [
                    [line_load_obj.line_end_point.x, line_load_obj.line_end_point.y,
                     line_load_obj.line_end_point.z]]
        return edited_dict

    # private function to find intersection points of line/patch edge within grid
    def __get_intersecting_elements(self, current_grid, line_start_grid, line_end_grid, line_load_obj, long_ele_index,
                                    trans_ele_index, edge_ele_index):
        R_z = []
        Rz = []
        R_x = []
        Rx = []
        R_edge = []
        Redge = []
        for long_ele in [self.Mesh_obj.long_ele[i] for i in long_ele_index]:
            pz1 = self.Mesh_obj.node_spec[long_ele[1]]['coordinate']  # point z 1
            pz2 = self.Mesh_obj.node_spec[long_ele[2]]['coordinate']  # point z 2
            pz1 = Point(pz1[0], pz1[1], pz1[2])  # convert to point namedtuple
            pz2 = Point(pz2[0], pz2[1], pz2[2])  # convert to point namedtuple
            x_1, x_2, z_1, z_2 = self.__check_line_ends_in_grid(pz1, pz2, current_grid, line_start_grid, line_end_grid,
                                                                line_load_obj)
            p_1 = Point(x_1, pz1.y, z_1)  # Assume same plane
            p_2 = Point(x_2, pz2.y, z_2)  # Assume same plane
            # check if special case - (1) one either is none, line segment does not exist
            if any([x_1 is None, x_2 is None, z_1 is None, z_2 is None]):
                continue
            if p_1 == p_2:  # (2) if both points of line are the exact point, point equates to an intersection point
                Rz.append([p_1.x, p_1.y, p_1.z])
                continue
            # if neither special case, check intersection
            intersect_z, colinear_z = check_intersect(pz1, pz2, p_1, p_2)
            if colinear_z:
                # line is colinear to long ele, start and end points are
                if pz1.x < p_1.x:
                    subdict_long = [[p_1.x, p_1.z], [pz2.x, pz2.z]]
                else:
                    subdict_long = [[p_1.x, p_1.z], [pz1.x, pz1.z]]
            elif intersect_z:
                L1 = line([pz1.x, pz1.z], [pz2.x, pz2.z])
                L2 = line([x_1, z_1], [x_2, z_2])
                R_z = intersection(L1, L2)
                Rz.append([R_z[0], pz1.y, R_z[1]])
        for trans_ele in [self.Mesh_obj.trans_ele[i] for i in trans_ele_index]:
            px1 = self.Mesh_obj.node_spec[trans_ele[1]]['coordinate']  # point z 1
            px2 = self.Mesh_obj.node_spec[trans_ele[2]]['coordinate']  # point z 2
            px1 = Point(px1[0], px1[1], px1[2])  # convert to point namedtuple
            px2 = Point(px2[0], px2[1], px2[2])  # convert to point namedtuple
            x_1, x_2, z_1, z_2 = self.__check_line_ends_in_grid(px1, px2, current_grid, line_start_grid, line_end_grid,
                                                                line_load_obj)
            p_1 = Point(x_1, px1.y, z_1)  # Assume same plane
            p_2 = Point(x_2, px2.y, z_2)  # Assume same plane
            # if any x or z value is null, line segment does not exist for the range, continue to next trans ele
            if any([x_1 is None, x_2 is None, z_1 is None, z_2 is None]):
                continue
            if p_1 == p_2:  # (2) if both points of line are the exact point, point equates to an intersection point
                Rx.append([p_1.x, p_1.y, p_1.z])
                continue
            intersect_x, colinear_x = check_intersect(px1, px2, p_1, p_2)
            if colinear_x:
                # line is colinear to long ele, start and end points are
                if p_1.z == p_2.z:  # colinear and two points are identical points
                    subdict_trans = [[px1.x, px1.z], [px2.x, px2.z]]
                elif px1.x < p_1.x:
                    subdict_trans = [[p_1.x, p_1.z], [px2.x, px2.z]]
                else:  # px1.x > p_1.x
                    subdict_trans = [[p_1.x, p_1.z], [px1.x, px1.z]]
            elif intersect_x:
                L1 = line([px1.x, px1.z], [px2.x, px2.z])
                L2 = line([x_1, z_1], [x_2, z_2])
                R_x = intersection(L1, L2)
                Rx.append([R_x[0], px1.y, R_x[1]])
        # for edge ele
        for edge_ele in [self.Mesh_obj.edge_span_ele[i] for i in edge_ele_index]:
            p_edge_1 = self.Mesh_obj.node_spec[edge_ele[1]]['coordinate']  # point z 1
            p_edge_2 = self.Mesh_obj.node_spec[edge_ele[2]]['coordinate']  # point z 2
            p_edge_1 = Point(p_edge_1[0], p_edge_1[1], p_edge_1[2])  # convert to point namedtuple
            p_edge_2 = Point(p_edge_2[0], p_edge_2[1], p_edge_2[2])  # convert to point namedtuple
            x_1, x_2, z_1, z_2 = self.__check_line_ends_in_grid(p_edge_1, p_edge_2, current_grid, line_start_grid,
                                                                line_end_grid, line_load_obj)
            p_1 = Point(x_1, p_edge_1.y, z_1)  # Assume same plane
            p_2 = Point(x_2, p_edge_2.y, z_2)  # Assume same plane
            # if any x or z value is null, line segment does not exist for the range, continue to next trans ele
            if any([x_1 is None, x_2 is None, z_1 is None, z_2 is None]):
                continue
            if p_1 == p_2:  # (2) if both points of line are the exact point, point equates to an intersection point
                R_edge.append([p_1.x, p_1.y, p_1.z])
                continue
            intersect_x, colinear_edge = check_intersect(p_edge_1, p_edge_2, p_1, p_2)
            if colinear_edge:
                # line is colinear to long ele, start and end points are
                if p_1.z == p_2.z:  # colinear and two points are identical points
                    subdict_trans = [[p_edge_1.x, p_edge_1.z], [p_edge_2.x, p_edge_2.z]]
                elif p_edge_1.x < p_1.x:
                    subdict_trans = [[p_1.x, p_1.z], [p_edge_2.x, p_edge_2.z]]
                else:  # px1.x > p_1.x
                    subdict_trans = [[p_1.x, p_1.z], [p_edge_1.x, p_edge_1.z]]
            elif intersect_x:
                L1 = line([p_edge_1.x, p_edge_1.z], [p_edge_2.x, p_edge_2.z])
                L2 = line([x_1, z_1], [x_2, z_2])
                R_edge = intersection(L1, L2)
                Redge.append([R_edge[0], p_edge_1.y, R_edge[1]])
        return Rz, Rx, Redge

    # private function to check if the ends of a line load obj lies within the mesh bounds
    @staticmethod
    def __check_line_ends_in_grid(p1, p2, current_grid, line_start_grid, line_end_grid, line_load_obj):
        # function to check if line load segment starts/ends within the bounds of the mesh. To do this, check if
        # coordinate range of element points, p1 p2, is within bounds of line load segment. If true, proceed return p1
        # p2 as points in the grid. If False (line segment does not exist for p1 p2), overwrite p1 p2 as the start/end
        # point where line segment exist.
        x_1 = p1.x
        z_1 = line_load_obj.get_line_segment_given_x(x_1)
        x_2 = p2.x
        z_2 = line_load_obj.get_line_segment_given_x(x_2)

        if line_load_obj.m is None:
            z_1 = p1.z
            x_1 = line_load_obj.get_line_segment_given_z(z_1)
            z_2 = p2.z
            x_2 = line_load_obj.get_line_segment_given_z(z_2)
            if x_1 is None:
                if current_grid == line_start_grid:
                    z_1 = line_load_obj.load_point_1.z
                    x_1 = line_load_obj.load_point_1.x
                elif current_grid == line_end_grid:
                    z_1 = line_load_obj.line_end_point.z
                    x_1 = line_load_obj.line_end_point.x
            elif x_2 is None:
                if current_grid == line_start_grid:
                    z_2 = line_load_obj.load_point_1.z
                    x_2 = line_load_obj.load_point_1.x
                elif current_grid == line_end_grid:
                    z_2 = line_load_obj.line_end_point.z
                    x_2 = line_load_obj.line_end_point.x
        else:
            x_1 = p1.x
            z_1 = line_load_obj.get_line_segment_given_x(x_1)
            x_2 = p2.x
            z_2 = line_load_obj.get_line_segment_given_x(x_2)
            if z_1 is None:
                if current_grid == line_start_grid:
                    z_1 = line_load_obj.load_point_1.z
                    x_1 = line_load_obj.load_point_1.x
                elif current_grid == line_end_grid:
                    z_1 = line_load_obj.line_end_point.z
                    x_1 = line_load_obj.line_end_point.x
            elif z_2 is None:
                if current_grid == line_start_grid:
                    z_2 = line_load_obj.load_point_1.z
                    x_2 = line_load_obj.load_point_1.x
                elif current_grid == line_end_grid:
                    z_2 = line_load_obj.line_end_point.z
                    x_2 = line_load_obj.line_end_point.x
        # special rule if z_1 or z_2 is None and slope of line load obj is inf (vertical), set x_1 = x_2

        return x_1, x_2, z_1, z_2

    # Getter for Patch loads
    def get_bounded_nodes(self, patch_load_obj):
        point_list = [patch_load_obj.load_point_1, patch_load_obj.load_point_2, patch_load_obj.load_point_3,
                      patch_load_obj.load_point_4]
        bounded_node = []
        bounded_grids = []
        for node_tag, node_spec in self.Mesh_obj.node_spec.items():
            coordinate = node_spec['coordinate']
            node = Point(coordinate[0], coordinate[1], coordinate[2])
            flag = check_point_in_grid(node, point_list)
            if flag:
                # node is inside
                bounded_node.append(node_tag)
        # check if nodes form grid
        for grid_number, grid_nodes in self.Mesh_obj.grid_number_dict.items():
            check = all([nodes in bounded_node for nodes in grid_nodes])
            if check:
                bounded_grids.append(grid_number)

        return bounded_node, bounded_grids

    # Setter for Point loads
    def assign_point_to_four_node(self, point, mag):
        """
        Function to assign point load to nodes of grid where the point load lies in.
        :param point: [x,y=0,z] coordinates of point load
        :param mag: Vertical (y axis direction) magnitude of point load
        :return:
        """
        node_mx = []
        node_mz = []
        # search grid where the point lies in
        grid_nodes, _ = self.get_point_load_nodes(point=point)
        if grid_nodes is None:
            load_str = []
            return load_str
        # if corner or edge grid with 3 nodes, run specific assignment for triangular grids
        # extract coordinates
        p1 = self.Mesh_obj.node_spec[grid_nodes[0]]['coordinate']
        p2 = self.Mesh_obj.node_spec[grid_nodes[1]]['coordinate']
        p3 = self.Mesh_obj.node_spec[grid_nodes[2]]['coordinate']

        point_list = [Point(p1[0], p1[1], p1[2]), Point(p2[0], p2[1], p2[2]), Point(p3[0], p3[1], p3[2])]
        if len(grid_nodes) == 3:
            sorted_list = sort_vertices(point_list)
            Nv = ShapeFunction.linear_triangular(x=point[0], z=point[2], x1=sorted_list[0].x, z1=sorted_list[0].z,
                                                 x2=sorted_list[1].x, z2=sorted_list[1].z, x3=sorted_list[2].x,
                                                 z3=sorted_list[2].z)
            node_load = [mag * n for n in Nv]
            node_mx = np.zeros(len(node_load))
            node_mz = np.zeros(len(node_load))
        else:  # else run assignment for quadrilateral grids

            # extract coordinates of fourth point
            p4 = self.Mesh_obj.node_spec[grid_nodes[3]]['coordinate']
            point_list.append(Point(p4[0], p4[1], p4[2]))
            sorted_list = sort_vertices(point_list)
            # mapping coordinates to natural coordinate, then finds eta (x) and zeta (z) of the point xp,zp
            eta, zeta = solve_zeta_eta(xp=point[0], zp=point[2], x1=sorted_list[0].x, z1=sorted_list[0].z,
                                       x2=sorted_list[1].x, z2=sorted_list[1].z, x3=sorted_list[2].x,
                                       z3=sorted_list[2].z, x4=sorted_list[3].x, z4=sorted_list[3].z)

            # access shape function of line load
            N = ShapeFunction.linear_shape_function(eta, zeta)
            Nv, Nmx, Nmz = ShapeFunction.hermite_shape_function_2d(eta, zeta)
            # Fy
            node_load = [mag * n for n in N]
            # Mx
            node_mx = [mag * n for n in Nmx]
            # Mz
            node_mz = [mag * n for n in Nmz]

        load_str = []
        for count, node in enumerate(grid_nodes):
            load_str.append("ops.load({pt}, *{val})\n".format(pt=node, val=[0, node_load[count], 0, node_mx[count], 0,
                                                                            node_mz[count]]))
        return load_str

    # Setter for Line loads and above
    def assign_line_to_four_node(self, line_load_obj, line_grid_intersect) -> list:
        """
        Function to assign line load to mesh. Procedure to assign line load is as follows:
        #. get properties of line on the grid
        #. convert line load to equivalent point load
        #. Find position of equivalent point load
        #. Runs assignment for point loads function (assign_point_to_four_node) using equivalent point load
         properties

        :param line_load_obj: Lineloading class object containing the line load properties
        :param line_grid_intersect: dict containing intersecting grid as key and intersecting points as values (list)
        :type line_load_obj: LineLoading class
        :return load_str_line: list containing strings of ops commands to be handled either - write to file
                                or eval()
        """

        # loop each grid
        load_str_line = []
        for grid, points in line_grid_intersect.items():
            # grid_nodes = self.Mesh_obj.grid_number_dict[grid]

            # extract two point of intersections within the grid
            p1 = points[0]
            p2 = points[1]
            # get length of line
            L = np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

            # get magnitudes at point 1 and point 2
            w1 = line_load_obj.interpolate_udl_magnitude([p1[0], 0, p1[1]])
            w2 = line_load_obj.interpolate_udl_magnitude([p2[0], 0, p2[1]])
            W = (w1 + w2) * L / 2
            # get mid point of line
            x_bar = ((2 * w1 + w2) / (w1 + w2)) * L / 3  # from p2
            load_point = line_load_obj.get_point_given_distance(xbar=x_bar,
                                                                point_coordinate=[p2[0], self.y_elevation, p2[1]])

            # uses point load assignment function to assign load point and mag to four nodes in grid
            load_str = self.assign_point_to_four_node(point=load_point, mag=W)
            load_str_line += load_str  # append to major list for line load
        return load_str_line

    # setter for patch loads
    def assign_patch_load(self, patch_load_obj: PatchLoading) -> list:
        # searches grid that encompass the patch load
        # use getter for line load, 4 times for each point
        # between 4 dictionaries record the common grids as having the corners of the patch - to be evaluated different
        bound_node, bound_grid = self.get_bounded_nodes(patch_load_obj)
        # assign patch for grids fully bounded by patch
        for grid in bound_grid:
            nodes = self.Mesh_obj.grid_number_dict[grid]  # read grid nodes
            # get p value of each node
            p_list = []
            for tag in nodes:
                coord = self.Mesh_obj.node_spec[tag]["coordinate"]
                p = patch_load_obj.patch_mag_interpolate(coord[0], coord[2])[0]  # object function returns array like
                p_list.append(LoadPoint(coord[0], coord[1], coord[2], p))
            # get centroid of patch on grid
            xc, yc, zc = get_patch_centroid(p_list)
            inside_point = Point(xc, yc, zc)
            # volume = area of base x average height
            A = self.get_node_area(inside_point=inside_point, p_list=p_list)
            # _, A = calculate_area_given_four_points(inside_point, p_list[0], p_list[1], p_list[2], p_list[3])
            mag = A * sum([point.p for point in p_list]) / len(p_list)
            # assign point and mag to 4 nodes of grid
            load_str = self.assign_point_to_four_node(point=[xc, yc, zc], mag=mag)
            self.global_load_str += load_str
        # apply patch for full bound grids completed

        # search the intersecting grids using line load function
        intersect_grid_1 = self.get_line_load_nodes(patch_load_obj.line_1)
        intersect_grid_2 = self.get_line_load_nodes(patch_load_obj.line_2)
        intersect_grid_3 = self.get_line_load_nodes(patch_load_obj.line_3)
        intersect_grid_4 = self.get_line_load_nodes(patch_load_obj.line_4)
        # merging process of the interesct grid dicts
        merged = check_dict_same_keys(intersect_grid_1, intersect_grid_2)
        merged = check_dict_same_keys(merged, intersect_grid_3)
        merged = check_dict_same_keys(merged, intersect_grid_4)
        self.global_patch_int_dict.update(merged)  # save intersect grid dict to global dict

        # all lines are ordered in path counter clockwise (sort in PatchLoading)
        # get nodes in grid that are left (check inside variable greater than 0)
        for grid, int_point_list in merged.items():  # [x y z]
            grid_nodes = self.Mesh_obj.grid_number_dict[grid]  # read grid nodes
            # get two grid nodes bounded by patch
            node_in_grid = [x for x, y in zip(grid_nodes, [node in bound_node for node in grid_nodes]) if y]
            node_list = int_point_list  # sort
            p_list = []
            # loop each int points
            for int_point in int_point_list:  # [x y z]
                p = patch_load_obj.patch_mag_interpolate(int_point[0], int_point[2])[
                    0]  # object function returns array like
                p_list.append(LoadPoint(int_point[0], int_point[1], int_point[2], p))
            # loop each node in grid points
            for items in node_in_grid:
                coord = self.Mesh_obj.node_spec[items]['coordinate']
                p = patch_load_obj.patch_mag_interpolate(coord[0], coord[2])[0]  # object function returns array like
                p_list.append(LoadPoint(coord[0], coord[1], coord[2], p))
            # sort points in counterclockwise
            p_list = sort_vertices(p_list)
            # get centroid of patch on grid
            xc, yc, zc = get_patch_centroid(p_list)
            inside_point = Point(xc, yc, zc)
            # volume = area of base x average height
            _, A = calculate_area_given_four_points(inside_point, p_list[0], p_list[1], p_list[2], p_list[3])
            mag = A * sum([point.p for point in p_list]) / len(p_list)
            # assign point and mag to 4 nodes of grid
            load_str = self.assign_point_to_four_node(point=[xc, yc, zc], mag=mag)
            self.global_load_str += load_str
        return self.global_load_str

    @staticmethod
    def get_node_area(inside_point, p_list) -> float:
        A = []
        if len(p_list) == 3:
            A = calculate_area_given_three_points(p_list[0], p_list[1], p_list[2])
        elif len(p_list) == 4:
            _, A = calculate_area_given_four_points(inside_point, p_list[0], p_list[1], p_list[2], p_list[3])
        return A

    # ----------------------------------------------------------------------------------------------------------
    #  functions to add load case and load combination
    def distribute_load_types_to_model(self, load_case_obj: Union[LoadCase, CompoundLoad]) -> list:
        """
        Functions to distribute load types to OpsGrillage model.
        :param load_case_obj:
        :return: list of str containing ops.load() command for distributing the load object parameter to nodes of model.
        """
        global load_groups
        load_str = []
        # check the input parameter type, set load_groups parameter according to its type
        if isinstance(load_case_obj, LoadCase):
            load_groups = load_case_obj.load_groups
        elif isinstance(load_case_obj, CompoundLoad):
            load_groups = load_case_obj.compound_load_obj_list
        # loop through each load object
        for load_dict in load_groups:
            load_obj = load_dict['load']
            if isinstance(load_obj, NodalLoad):
                load_str = load_dict.get_nodal_load_str()
                self.global_load_str.append(load_str)

            elif isinstance(load_obj, PointLoad):
                load_str = self.assign_point_to_four_node(point=list(load_obj.load_point_1)[:-1],
                                                          mag=load_obj.load_point_1.p)
                self.global_load_str.append(load_str)
            elif isinstance(load_obj, LineLoading):
                line_grid_intersect = self.get_line_load_nodes(load_obj)  # returns self.line_grid_intersect
                self.global_line_int_dict.append(line_grid_intersect)
                load_str = self.assign_line_to_four_node(load_obj, line_grid_intersect)
                self.global_load_str.append(load_str)

            elif isinstance(load_obj, PatchLoading):
                load_str = self.assign_patch_load(load_obj)

        return load_str

    def add_load_case(self, load_case_obj: Union[LoadCase, CompoundLoad], load_factor=1):
        """
        Function to add individual load cases to OpsGrillage instance.
        :param load_factor:
        :param load_case_obj:
        :return: Populate self.load_case_list with input load case object. Distributes loads/groups within load case
                 to grillage model. This returns a list of ops.load() commands and assigns to its respective load case
                 object

        A typical load_case_dict within load_case_dict list has the following format
        .. code:
            load_case_dict = {'name':load_case_obj.name, 'loadcase': load_case_obj, 'load_command': load_str,
                          'load_factor': load_factor}
        """
        # update the load command list of load case object
        load_str = self.distribute_load_types_to_model(load_case_obj=load_case_obj)
        # load_case_obj.set_load_case_load_command(load_str=load_str)
        # store load case + load command in dict and add to load_case_list
        load_case_dict = {'name':load_case_obj.name, 'loadcase': load_case_obj, 'load_command': load_str,
                          'load_factor': load_factor}  # FORMATTING HERE
        self.load_case_list.append(load_case_dict)
        print("Load Case {} added".format(load_case_obj.name))

    def analyse_load_case(self):
        # analyse all load case defined in self.load_case_dict for OpsGrillage instance
        # loop each load case dict
        for load_case_dict in self.load_case_list:
            # create analysis object, run and get results
            load_case_obj = load_case_dict['loadcase']
            load_command = load_case_dict['load_command']
            load_factor = load_case_dict['load_factor']
            load_case_analysis = Analysis(analysis_name=load_case_obj.name, ops_grillage_name=self.model_name,
                                          pyfile=self.pyfile)
            load_case_analysis.add_load_command(load_command, load_factor=load_factor)
            # run the Analysis object, collect results, and store Analysis object in the list for Analysis load case
            load_case_analysis.evaluate_analysis()

    def add_load_combination(self, load_combination_name: str, load_case_name_dict: dict):
        """
        Function to create load combinations out of the defined load cases.
        :param load_combination_name: name of load combination
        :param load_case_name_dict: dict with load case name as key, and load factor as value
                                    Format example:
                                        {"DL":1.2, "LL":1.7}
        .. note:
            Load cases in load_case_name_dict must be added to OpsGrillage instance through add_load_case() function.
            If load case name not found in defined load cases, return
        :return: populate self.load_combination_dict , with key being the load_combination name parameter and value
                    being a list of dict for load cases

            A typical load_case_dict within load_case_dict list has the following format
        .. code:
            load_case_dict = {'name':load_case_obj.name, 'loadcase': load_case_obj, 'load_command': load_str,
                          'load_factor': load_factor}
        """

        load_case_dict_list = [] # list of dict: structure of dict See line
        # create dict with key (combination name) and val (list of dict of load cases)
        for load_case_name, load_factor in load_case_name_dict.items():
            # lookup the defined load cases for load_case_name
            a = [index for (index,val) in enumerate(self.load_case_list) if val['name']==load_case_name]
            if a:
                ind = a[0]
            else:
                ind = None
                continue
            # get
            load_case_dict = self.load_case_list[ind]
            # update load factor of load_case
            load_case_dict['load_factor'] = load_factor
            # add load case dict to new list for load combination
            load_case_dict_list.append(load_case_dict)

        self.load_combination_dict.setdefault(load_combination_name,load_case_dict_list)
        print("Load Combination: {} created".format(load_combination_name))

    def analyse_load_combination(self, selected_load_combination: str=None):
        # create analysis object, add each factored load case to analysis object
        for load_combination_name,load_case_dict_list in self.load_combination_dict.items():
            load_combination_analysis = Analysis(analysis_name=load_combination_name, ops_grillage_name=self.model_name,
                                          pyfile=self.pyfile)
            for load_case_dict in load_case_dict_list:
                load_case_obj = load_case_dict['loadcase']    # maybe unused
                load_command = load_case_dict['load_command']
                load_factor = load_case_dict['load_factor']
                load_combination_analysis.add_load_command(load_command, load_factor=load_factor)
            load_combination_analysis.evaluate_analysis()

    def add_moving_load_case(self, moving_load_obj: MovingLoad, load_factor=1):
        """
        Function to add Moving load case to OpsGrillage instance.
        :param moving_load_obj:
        :return:
        """
        # get the list of individual load cases
        list_of_incr_load_case_dict = []
        # for each load case, find the load commands of load distribution
        for moving_load_case_list in moving_load_obj.moving_load_case:
            for increment_load_case in moving_load_case_list:
                load_str = self.distribute_load_types_to_model(load_case_obj=increment_load_case)
                increment_load_case_dict = {'name': increment_load_case.name, 'loadcase': increment_load_case, 'load_command': load_str,
                                    'load_factor': load_factor}
                list_of_incr_load_case_dict.append(increment_load_case_dict)
            self.moving_load_case_dict[moving_load_obj.name] = list_of_incr_load_case_dict

        # set the individual load case - get the corresponding load_str for each load cases using add load case function
        # set the load str to the individual loadcase via loadcase.set_load_case_load_command


    def analyse_moving_load_case(self, moving_load_case_name: str):
        # functino to analyse individual moving load case
        # create analysis object for each load case correspond to increment of moving paths

        for moving_load_obj, load_case_dict_list in self.moving_load_case_dict.items():
            for load_case_dict in load_case_dict_list:
                load_case_obj = load_case_dict['loadcase']  # maybe unused
                load_command = load_case_dict['load_command']
                load_factor = load_case_dict['load_factor']
                incremental_analysis = Analysis(analysis_name=load_case_obj.name,
                                                     ops_grillage_name=self.model_name,
                                                     pyfile=self.pyfile)
                incremental_analysis.add_load_command(load_command)
                incremental_analysis.evaluate_analysis()


# ---------------------------------------------------------------------------------------------------------------------
class Analysis:
    """
    Analysis class objected to handle the run/execution of load case + load combination + moving load analysis


    """

    def __init__(self, analysis_name: str, ops_grillage_name: str, pyfile: bool, analysis_type='Static'):
        self.analysis_name = analysis_name
        self.ops_grillage_name = ops_grillage_name
        self.time_series_tag = None
        self.pattern_tag = None
        self.analysis_type = analysis_type
        self.pyfile = pyfile
        self.analysis_file_name = self.analysis_name + "of" + self.ops_grillage_name + ".py"  # py file name
        # list recording load commands, time series and pattern for the input load case
        self.load_cases_dict_list = []  # keys # [{time_series,pattern,load_command},... ]
        # counters
        self.time_series_counter = 1
        self.plain_counter = 1

        # recorder variables to store results of analysis
        # TODO
        # preset ops analysis commands
        self.wipe_command = "ops.wipeAnalysis()\n"
        self.numberer_command = "ops.numberer('Plain')\n"  # default plain
        self.system_command = "ops.system('BandGeneral')\n"  # default band general
        self.constraint_command = "ops.constraints('Plain')\n"  # default plain
        self.algorithm_command = "ops.algorithm('Linear')\n"  # default linear
        self.analyze_command = "ops.analyze(1)\n"  # default 1 step
        self.analysis_command = "ops.analysis(\"{}\")\n".format(analysis_type)
        self.intergrator_command = "ops.integrator('LoadControl', 1)\n"

        # if true for pyfile, create pyfile for analysis command
        if self.pyfile:
            with open(self.analysis_file_name, 'w') as file_handle:
                # create py file or overwrite existing
                # writing headers and description at top of file
                file_handle.write("# Grillage generator wizard\n# Model name: {}\n".format(self.analysis_name))
                # time
                now = datetime.now()
                dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
                file_handle.write("# Constructed on:{}\n".format(dt_string))
                # write imports
                file_handle.write("import numpy as np\nimport math\nimport openseespy.opensees as ops"
                                  "\nimport openseespy.postprocessing.Get_Rendering as opsplt\n")

    def time_series_command(self, load_factor):
        time_series = "ops.timeSeries('Constant', {}, '-factor',{})\n".format(self.time_series_counter, load_factor)
        self.time_series_counter += 1  # update counter by 1
        return time_series

    def pattern_command(self):
        pattern_command = "ops.pattern('Plain', {}, {})\n".format(self.plain_counter, self.time_series_counter - 1)
        # minus 1 to time series counter for time_series_command() precedes pattern_command() and incremented the time
        # series counter
        self.plain_counter += 1
        return pattern_command

    def add_load_command(self, load_str: list, load_factor):
        # create time series for added load case
        time_series = self.time_series_command(load_factor)  # get time series command
        pattern_command = self.pattern_command()  # get pattern command
        time_series_dict = {'time_series': time_series, 'pattern': pattern_command, 'load_command': load_str}
        self.load_cases_dict_list.append(time_series_dict)  # add dict to list

    def evaluate_analysis(self):
        # write/execute ops.load commands for all static loads of each loadcases
        if self.pyfile:
            with open(self.analysis_file_name, 'a') as file_handle:
                for load_dict in self.load_cases_dict_list:
                    file_handle.write(load_dict['time_series'])
                    file_handle.write(load_dict['pattern'])
                    for load_command in load_dict['load_command']:
                        file_handle.write(load_command)
                file_handle.write(self.intergrator_command)
                file_handle.write(self.numberer_command)
                file_handle.write(self.system_command)
                file_handle.write(self.constraint_command)
                file_handle.write(self.algorithm_command)
                file_handle.write(self.analysis_command)
                file_handle.write(self.analyze_command)
        else:
            for load_dict in self.load_cases_dict_list:
                eval(load_dict['time_series'])
                eval(load_dict['pattern'])
                for load_command in load_dict['load_command']:
                    eval(load_command)
            eval(self.intergrator_command)
            eval(self.numberer_command)
            eval(self.system_command)
            eval(self.constraint_command)
            eval(self.algorithm_command)
            eval(self.analysis_command)
            eval(self.analyze_command)

        print("Analysis: {} completed".format(self.analysis_name))
        # record analyzed results
