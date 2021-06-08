import math
import openseespy.opensees as ops
from datetime import datetime
from collections import defaultdict
from Load import *
from Material import *
from member_sections import *
from Mesh import *
from itertools import combinations
from scipy import integrate


class OpsGrillage:
    """
    Main class of Openseespy grillage model wrapper. Outputs an executable py file which generates the prescribed
    Opensees grillage model based on user input.

    The class provides an interface for the user to specify the geometry of the grillage model. A keyword argument
    allows for users to select between skew/oblique or orthogonal mesh. Methods in this class allows users to input
    properties for various elements in the grillage model.
    """

    def __init__(self, bridge_name, long_dim, width, skew, num_long_grid,
                 num_trans_grid, edge_beam_dist, mesh_type="Ortho", op_instance=True, model="3D", **kwargs):
        """

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

        # model information
        self.mesh_type = mesh_type
        self.model_name = bridge_name
        self.op_instance_flag = op_instance

        # global dimensions of grillage
        self.long_dim = long_dim  # span , also c/c between support bearings
        self.width = width  # length of the bearing support - if skew  = 0 , this corresponds to width of bridge

        if isinstance(skew, list):
            self.skew_a = skew[0]
            if len(skew) >= 2:
                self.skew_b = skew[1]
        else:
            self.skew_a = skew  # angle in degrees
            self.skew_b = skew  # angle in degrees

        # Variables for grillage grillage
        self.num_long_gird = num_long_grid  # number of longitudinal beams
        self.num_trans_grid = num_trans_grid  # number of grids for transverse members
        self.edge_width = edge_beam_dist  # width of cantilever edge beam
        self.edge_beam_nodes = []
        # instantiate matrices for geometric dependent properties
        self.trans_dim = None  # to be calculated automatically based on skew
        self.breadth = None  # to be calculated automatically based on skew

        # initialize lists
        self.global_mat_object = []  # material matrix

        # initialize tags of grillage elements - default tags are for standard elements of grillage
        # Section placeholders
        self.section_arg = None
        self.section_tag = None
        self.section_type = None

        # dict
        self.group_ele_dict = None  # dictionary of ele groups e.g. [ "name of group": tag ]
        self.global_element_list = None  # list of all elements in grillage
        self.ele_group_assigned_list = []  # list recording assigned ele groups in grillage model
        self.section_dict = {}  # dictionary of section tags
        self.material_dict = {}  # dictionary of material tags

        # collect mesh groups
        self.mesh_group = []
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

        self.y_elevation = 0  # default elevation of grillage wrt OPmodel coordinate system
        self.min_grid_ortho = 3  # for orthogonal mesh (skew>skew_threshold) region of orthogonal area default 3
        self.while_loop_max = 100
        if model == "2D":
            self.__ndm = 2  # num model dimension - default 3
            self.__ndf = 3  # num degree of freedom - default 6
        else:
            self.__ndm = 3  # num model dimension - default 3
            self.__ndf = 6  # num degree of freedom - default 6

        # default vector for support (for 2D grillage in x - z plane)
        self.fix_val_pin = [1, 1, 1, 0, 0, 0]  # pinned
        self.fix_val_roller_x = [0, 1, 1, 0, 0, 0]  # roller
        # special rules for grillage - alternative to Properties of grillage definition - use for special dimensions
        self.skew_threshold = [10, 30]  # threshold for grillage to allow option of mesh choices
        self.deci_tol = 4  # tol of decimal places

        # dict for load cases and load types
        self.load_case_dict = defaultdict(lambda: 1)
        self.nodal_load_dict = defaultdict(lambda: 1)
        self.ele_load_dict = defaultdict(lambda: 1)

        # counters to keep track of objects for loading
        self.load_case_counter = 1
        self.load_combination_counter = 1
        self.line_grid_intersect = dict()  # keep track of grids
        # Initiate py file output
        self.filename = "{}_op.py".format(self.model_name)
        # create namedtuples

        # calculate edge length of grillage
        self.trans_dim = self.width / math.cos(self.skew_a / 180 * math.pi)

        # objects and pyfile flag
        self.Mesh_obj = None
        self.pyfile = None

    def create_ops(self, pyfile=False):
        # function to handle Opensees
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

    def __run_mesh_generation(self):
        # function to run mesh generation
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

    # abstraction to write ops commands to output py file
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

    def set_member(self, grillage_member_obj, member=None):
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

    def set_material(self, material_obj):
        """
        Function to define a global material model. This function proceeds to write write the material() command to
        output file.

        :return: Function populates object variables: (1) mat_matrix, and (2) mat_type_op.
        """
        # set material to global material object
        self.global_mat_object = material_obj  # material matrix for

        # write uniaxialMaterial() command to output file
        self.__write_uniaxial_material(material=material_obj)

    def run_check(self):
        """
        Test output file

        """
        try:
            __import__(self.filename[:-3])  # run file
            print("File successfully imported and run")
        except:
            print("File executed with error exceptions")

    # ---------------------------------------------------------------
    # Function to find nodes or grids correspond to a point or line - called within OpsGrillage for distributing
    # loads to grillage nodes

    # Getter for elements within a grid
    def __get_elements(self, node_tag_combo):
        # abstracted procedure to find and return the long and trans elements within a grid of 4 or 3 nodes
        record_long = []
        record_trans = []
        for combi in node_tag_combo:
            long_mem_index = [i for i, x in
                              enumerate([combi[0] in n[1:3] and combi[1] in n[1:3] for n in self.Mesh_obj.long_ele])
                              if x]
            trans_mem_index = [i for i, x in enumerate(
                [combi[0] in n[1:3] and combi[1] in n[1:3] for n in self.Mesh_obj.trans_ele]) if x]
            record_long = record_long + long_mem_index  # record
            record_trans = record_trans + trans_mem_index  # record
        return record_long, record_trans

    # Getter for Points Loads nodes and above
    def get_point_load_nodes(self, point):
        # procedure
        # 1 find the closest node 2 find the respective grid within the closest node
        # extract points
        loading_point = None
        if type(point) is float or type(point) is list:
            x = point[0]
            y = point[1]  # default y = self.y_elevation = 0
            z = point[2]
            # set point to tuple
            loading_point = Point(x, y, z)  # TODO change this next time when converting to use Point() tuple
        elif isinstance(point, LoadPoint):
            loading_point = point
        node_distance = []
        # find node closest to point
        for tag, subdict in self.Mesh_obj.node_spec.items():
            node = subdict['coordinate']
            dis = np.sqrt((node[0] - loading_point.x) ** 2 + 0 + (node[2] - loading_point.z) ** 2)
            node_distance.append([tag, dis])
        node_distance.sort(key=lambda x: x[1])
        closest_node = node_distance[0]
        x_closest = self.Mesh_obj.node_spec[closest_node[0]]['coordinate'][0]
        y_closest = self.Mesh_obj.node_spec[closest_node[0]]['coordinate'][1]  # defined herein for future consideration
        z_closest = self.Mesh_obj.node_spec[closest_node[0]]['coordinate'][2]

        # get vicinity nodes
        x_vicinity_nodes = self.Mesh_obj.node_connect_x_dict[closest_node[0]]
        z_vicinity_nodes = self.Mesh_obj.node_connect_z_dict[closest_node[0]]

        xg = []
        zg = []
        n1 = closest_node[0]
        n2 = []  # z vici node
        n3 = []
        n4 = []  # x vici node

        if loading_point.x >= x_closest:
            n4 = [x_node for x_node in x_vicinity_nodes if self.Mesh_obj.node_spec[x_node]['coordinate'][0] > x_closest]
            if loading_point.z >= z_closest:
                n2 = [z_node for z_node in z_vicinity_nodes if
                      self.Mesh_obj.node_spec[z_node]['coordinate'][2] > z_closest]
            elif loading_point.z <= z_closest:
                n2 = [z_node for z_node in z_vicinity_nodes if
                      self.Mesh_obj.node_spec[z_node]['coordinate'][2] <= z_closest]
        elif loading_point.x <= x_closest:
            n4 = [x_node for x_node in x_vicinity_nodes if
                  self.Mesh_obj.node_spec[x_node]['coordinate'][0] <= x_closest]
            if loading_point.z >= z_closest:
                n2 = [z_node for z_node in z_vicinity_nodes if
                      self.Mesh_obj.node_spec[z_node]['coordinate'][2] > z_closest]
            elif loading_point.z <= z_closest:
                n2 = [z_node for z_node in z_vicinity_nodes if
                      self.Mesh_obj.node_spec[z_node]['coordinate'][2] <= z_closest]
        # if point is not within the grid
        if not n2 and not n4:  # point is not in the grid ,
            return None
        else:  # run check
            if not n2:  # if n2 is empty - search using n1 and n4
                n3 = [k for k, v in enumerate(self.Mesh_obj.grid_number_dict.values()) if n1 in v and n4[0] in v]
                # if multiple elements of n3, check if point lies within
            elif not n4:  # in mesh,  impossible for n4 == [] - search using n1 and n2
                n3 = [k for k, v in enumerate(self.Mesh_obj.grid_number_dict.values()) if n1 in v and n2[0] in v]
            else:
                n3 = [k for k, v in enumerate(self.Mesh_obj.grid_number_dict.values()) if
                      n2[0] in v and n1 in v and n4[0] in v]

            if len(n3) > 1:
                # get node coordinate
                for grid_number in n3:
                    node_tags = self.Mesh_obj.grid_number_dict[grid_number]
                    coordinate = [self.Mesh_obj.node_spec[tag]["coordinate"] for tag in node_tags]
                    point_list = [Point(coord[0], coord[1], coord[2]) for coord in coordinate]
                    # check if point within
                    inside_flag = check_point_in_grid(loading_point, point_list)
                    if inside_flag:
                        n3 = [grid_number]  # overwrite n3 as grid where node is situated inside
                        continue
            node_list = self.Mesh_obj.grid_number_dict[n3[0]]

        return node_list, n3[0]  # n3 = grid number

        # pass shape function to distribute load to 4 points

    # Getter for Line loads nodes and above
    def get_line_load_nodes(self, line_load_obj):
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
        if start_nd is None:  # if point is not present (returned None), point lies outside of mesh, set
            # x_start and z_start be the point which line intersects the start span edge node line
            x_start = x_intcp_two_lines(m1=self.Mesh_obj.start_edge_line.slope, c1=self.Mesh_obj.start_edge_line.c,
                                        m2=m,
                                        c2=c)
            z_start = line_func(m=m, c=c, x=x_start)
            nd, current_grid = self.get_point_load_nodes([x_start, self.y_elevation, z_start])  # list of nodes on grid
        else:
            x_start = line_load_obj.load_point_1.x
            z_start = line_load_obj.load_point_1.z
            nd = start_nd

        # find last grid where the line load ends
        last_nd, last_grid = self.get_point_load_nodes(line_load_obj.line_end_point)
        x_end = line_load_obj.line_end_point.x
        z_end = line_load_obj.line_end_point.z
        # while loop counter
        counter = 1
        # initiate flags
        long_intersect = False
        trans_intersect = False
        line_on = True
        subdict = {}

        # begin loop
        while line_on:
            # find indices for long member and transverse member
            node_tag_combo = combinations(nd, 2)
            if counter > 1:
                current_grid = next_grid
            long_ele_tags, trans_ele_tags = self.__get_elements(node_tag_combo)

            # for each long and trans member in record, find if intersect long or trans ele
            for long_ele in [self.Mesh_obj.long_ele[i] for i in long_ele_tags]:
                pz1 = self.Mesh_obj.node_spec[long_ele[1]]['coordinate']  # point z 1
                pz2 = self.Mesh_obj.node_spec[long_ele[2]]['coordinate']  # point z 2
                pz1 = Point(pz1[0], pz1[1], pz1[2])  # convert to point namedtuple
                pz2 = Point(pz2[0], pz2[1], pz2[2])  # convert to point namedtuple
                intersect_z = check_intersect(pz1, pz2, line_load_obj.load_point_1, line_load_obj.line_end_point)

                if intersect_z:
                    # use decimal lib to remove floating point errors for logic comparison
                    L1 = line([pz1.x, pz1.z], [pz2.x, pz2.z])
                    L2 = line([x_start, z_start], [x_end, z_end])
                    R_z = intersection(L1, L2)
                    # if all([Rx <= max(pz1x_d, pz2x_d), Rx >= min(pz1x_d, pz2x_d), Rz <= max(pz1z_d, pz2z_d),
                    #         Rz >= min(pz1z_d, pz2z_d)]):
                    next_grid_z = []
                    # if true, line intersects, find next grid using the vicinity_dict of Mesh_obj
                    vicinity_grid = self.Mesh_obj.grid_vicinity_dict[current_grid]
                    # check if nodes is in either "top" or bottom keyword
                    if long_ele[1] in self.Mesh_obj.grid_number_dict.get(vicinity_grid.get("top", None), []) \
                            and long_ele[2] in self.Mesh_obj.grid_number_dict.get(vicinity_grid.get("top", None),
                                                                                  []):
                        next_grid_z = vicinity_grid.get("top", None)
                    elif long_ele[1] in self.Mesh_obj.grid_number_dict.get(vicinity_grid.get("bottom", None), []) \
                            and long_ele[2] in self.Mesh_obj.grid_number_dict.get(vicinity_grid.get("bottom", None),
                                                                                  []):
                        next_grid_z = vicinity_grid.get("bottom", None)
                    long_intersect = True

                    if next_grid_z in self.line_grid_intersect.keys():
                        long_intersect = False
                    else:
                        subdict['points'] = [[x_start, z_start], list(R_z)]
                        break
                    # else:
                    #     long_intersect = False
                elif current_grid in self.line_grid_intersect.keys():
                    long_intersect = False
            # check if intersects trans member
            for trans_ele in [self.Mesh_obj.trans_ele[i] for i in trans_ele_tags]:
                px1 = self.Mesh_obj.node_spec[trans_ele[1]]['coordinate']  # point z 1
                px2 = self.Mesh_obj.node_spec[trans_ele[2]]['coordinate']  # point z 2
                px1 = Point(px1[0], px1[1], px1[2])  # convert to point namedtuple
                px2 = Point(px2[0], px2[1], px2[2])  # convert to point namedtuple
                intersect_x = check_intersect(px1, px2, line_load_obj.load_point_1, line_load_obj.line_end_point)

                if intersect_x:
                    L1 = line([px1.x, px1.z], [px2.x, px2.z])
                    L2 = line([x_start, z_start], [x_end, z_end])
                    R_x = intersection(L1, L2)

                    next_grid_x = []
                    # if true, line intersects, find next grid using the vicinity_dict of Mesh_obj
                    vicinity_grid = self.Mesh_obj.grid_vicinity_dict[current_grid]
                    # check if nodes is in either "top" or bottom keyword
                    if trans_ele[1] in self.Mesh_obj.grid_number_dict.get(vicinity_grid.get("left", None), []) \
                            and trans_ele[2] in self.Mesh_obj.grid_number_dict.get(vicinity_grid.get("left", None),
                                                                                   []):
                        next_grid_x = vicinity_grid.get("left", None)
                    elif trans_ele[1] in self.Mesh_obj.grid_number_dict.get(vicinity_grid.get("right", None), []) \
                            and trans_ele[2] in self.Mesh_obj.grid_number_dict.get(vicinity_grid.get("right", None),
                                                                                   []):
                        next_grid_x = vicinity_grid.get("right", None)
                    trans_intersect = True
                    # if next grid has already been recorded (line tracks the previous intersecting grid),
                    # exclude this intersection and move to next
                    if next_grid_x in self.line_grid_intersect.keys():
                        trans_intersect = False
                    else:  # the new grid is not been crossed, record this grid as the intersecting
                        subdict['points'] = [[x_start, z_start], list(R_x)]
                        break
                else:
                    trans_intersect = False
            # setting properties of next loop
            # if intersects transverse member, set intersection point R_x as start point of next step
            if trans_intersect:
                next_grid = next_grid_x
                x_start = R_x[0]
                z_start = R_x[1]
            elif long_intersect:  # if intersect long member, set respective intersection point R_z
                next_grid = next_grid_z
                x_start = R_z[0]
                z_start = R_z[1]
            else:  # intersects neither - check if crosses edge
                subdict['points'] = [[x_start, z_start], [x_end, z_end]]
                next_grid = current_grid

            # if no longer intersects any edges, set loop to false
            if not any([trans_intersect, long_intersect]):
                line_on = False
            if counter > self.while_loop_max:  # measure to prevent infinite loop - default 100 steps
                line_on = False

            if len(self.Mesh_obj.grid_number_dict[current_grid]) < 4 and counter > 2:
                # intersect with end edge span
                line_on = False

            # save intersection point as x_intcp and z_intcp, repeat loop
            self.line_grid_intersect.setdefault(current_grid, subdict)
            # check if next grid is the final grid
            if set(nd) == set(last_nd):
                line_on = False
                # last grid achieved
                subdict = dict()
                subdict['points'] = [[x_start, z_start],
                                     [line_load_obj.line_end_point.x, line_load_obj.line_end_point.z]]
                self.line_grid_intersect.setdefault(next_grid, subdict)
            # update nd, x_start, z_start for next loop
            nd = self.Mesh_obj.grid_number_dict[next_grid]
            counter += 1
            subdict = dict()  # reset subdict
        return self.line_grid_intersect

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

    # Setter for Point loads and above
    def assign_point_to_four_node(self, point, mag):
        """
        Function to assign point load to nodes of grid where the point load lies in.
        :param point: [x,y=0,z] coordinates of point load
        :param mag: Vertical (y axis direction) magnitude of point load
        :return:
        """

        # search grid where the point lies in
        grid_nodes,_ = self.get_point_load_nodes(point=point)
        # if corner or edge grid with 3 nodes, run specific assignment for triangular grids
        # extract coordinates
        x1 = self.Mesh_obj.node_spec[grid_nodes[0]]['coordinate'][0]
        x2 = self.Mesh_obj.node_spec[grid_nodes[1]]['coordinate'][0]
        x3 = self.Mesh_obj.node_spec[grid_nodes[2]]['coordinate'][0]
        z1 = self.Mesh_obj.node_spec[grid_nodes[0]]['coordinate'][2]
        z2 = self.Mesh_obj.node_spec[grid_nodes[1]]['coordinate'][2]
        z3 = self.Mesh_obj.node_spec[grid_nodes[2]]['coordinate'][2]
        if len(grid_nodes) == 3:
            Nv = ShapeFunction.linear_triangular(x=point[0], z=point[2], x1=x1, z1=z1, x2=x2, z2=z2, x3=x3, z3=z3)
            node_load = [mag * n for n in Nv]
        else:  # else run assignment for quadrilateral grids

            # extract coordinates of fourth point
            x4 = self.Mesh_obj.node_spec[grid_nodes[3]]['coordinate'][0]
            z4 = self.Mesh_obj.node_spec[grid_nodes[3]]['coordinate'][2]
            # mapping coordinates to natural coordinate, then finds eta (x) and zeta (z) of the point xp,zp
            eta, zeta = solve_zeta_eta(xp=point[0], zp=point[2], x1=x1, z1=z1, x2=x2, z2=z2, x3=x3, z3=z3, x4=x4, z4=z4)

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
            load_str.append("ops.load({pt}, *{val})\n".format(pt=node, val=[0, node_load[count], 0, 0, 0]))
        return load_str

    # Setter for Line loads and above
    def assign_line_to_four_node(self, line_load_obj):
        """
        Function to assign line load to mesh. Procedure to assign line load is as follows:
        #. get properties of line on the grid
        #. convert line load to equivalent point load
        #. Find position of equivalent point load
        #. Runs assignment for point loads function (assign_point_to_four_node) using equivalent point load
         properties

        :param line_load_obj: Lineloading class object containing the line load properties
        :type line_load_obj: LineLoading class
        :return load_str_line: list containing strings of ops commands to be handled either - write to file
                                or eval()
        """

        # loop each grid
        load_str_line = []
        for grid, points in self.line_grid_intersect.items():
            # grid_nodes = self.Mesh_obj.grid_number_dict[grid]

            # extract points [x,z], default y = 0 plane
            p1 = points['points'][0]
            p2 = points['points'][1]
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

    # ----------------------------------------------------------------------------------------------------------
    #  functions to add load case and load combination

    def add_load_case(self, load_case_obj, analysis_type='Static'):
        """
        Functions to add loads or load cases
        :param name:
        :param load_case_obj:
        :param analysis_type:
        :return:
        """

        with open(self.filename, 'a') as file_handle:
            # if no load cases have been defined previously, create time series object for the first time
            if not bool(self.load_case_dict):
                time_series = "ops.timeSeries('Constant', 1)\n"
                if self.pyfile:
                    file_handle.write(time_series)
                else:
                    eval(time_series)
                load_case_counter = 0  # if dict empty, start counter at 1
            else:  # set load_case_counter variable as the latest
                load_case_counter = self.load_case_dict[list(self.load_case_dict)[-1]]
                wipe_command = "ops.wipeAnalysis()\n"
                if self.pyfile:
                    file_handle.write(wipe_command)  # write wipeAnalysis for current load case
                else:
                    eval(wipe_command)

            # set load case to load_case_dict
            load_case_tag = self.load_case_dict.setdefault(load_case_obj.name, load_case_counter + 1)
            # write header
            file_handle.write("#===========================\n# create load case {}\n#==========================\n"
                              .format(load_case_obj.name))
            # create pattern obj for load case
            pattern_command = "ops.pattern('Plain', {}, 1)\n".format(load_case_tag)
            if self.pyfile:
                file_handle.write(pattern_command)
            else:
                eval(pattern_command)

            # loop through each load object
            for loads in load_case_obj.load_groups:
                if isinstance(loads, NodalLoad):
                    load_str = loads.get_nodal_load_str()
                    for lines in load_str:
                        if self.pyfile:
                            file_handle.write(lines)
                        else:
                            eval(lines)
                    # print to terminal com
                    print("Nodal load - {loadname} - added to load case: {loadcase}".format(loadname=loads.name,
                                                                                            loadcase=load_case_obj.name))
                elif isinstance(loads, PointLoad):
                    # TODO
                    load_str = self.assign_point_to_four_node(point=list(loads.load_point_1)[:-1], mag=loads.Fy)

                elif isinstance(loads, LineLoading):
                    self.get_line_load_nodes(loads)  # returns self.line_grid_intersect
                    load_str = self.assign_line_to_four_node(loads)
                    for lines in load_str:
                        file_handle.write(lines)
                    print("Line load - {loadname} - added to load case: {name}".format(loadname=loads.name,
                                                                                       name=load_case_obj.name))

                elif isinstance(loads, PatchLoading):

                    load_str = self.assign_patch_load(loads)
                    pass
            # Create instance and write command to output py file
            file_handle.write("ops.integrator('LoadControl', 1)\n")  # Header
            file_handle.write("ops.numberer('Plain')\n")
            file_handle.write("ops.system('BandGeneral')\n")
            file_handle.write("ops.constraints('Plain')\n")
            file_handle.write("ops.algorithm('Linear')\n")
            file_handle.write("ops.analysis(\"{}\")\n".format(analysis_type))
            file_handle.write("ops.analyze(1)\n")

            # print to terminal
            print("Load Case {} created".format(load_case_obj.name))

    # setter for patch loads
    def assign_patch_load(self, patch_load_obj: object) -> PatchLoading:
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
                p = patch_load_obj.patch_mag_interpolate(coord[0], coord[2])[0] # object function returns array like
                p_list.append(LoadPoint(coord[0], coord[1], coord[2], p))
            # get centroid of patch on grid
            xc,yc,zc = get_patch_centroid(p_list)
            inside_point = LoadPoint(xc,yc,zc,0)
            # volume = area of base x average height
            _, A = calculate_area_given_four_points(inside_point, p_list[0], p_list[1], p_list[2], p_list[3])
            mag = A*sum([point.p for point in p_list])/len(p_list)
            # assign point and mag to 4 nodes of grid
            self.assign_point_to_four_node(point = [xc,yc,zc],mag=mag)

        # assign patch load to intersecting grids
        intersect_grid_1 = self.get_line_load_nodes(patch_load_obj.line_1)
        # all lines are ordered in path counter clockwise (sort in PatchLoading)
        # get nodes in grid that are left (check inside variable greater than 0)
        # for each grid, calculate
        for grid, int_points in intersect_grid_1.items():
            grid_nodes = self.Mesh_obj.grid_number_dict[grid]  # read grid nodes
            # get two grid nodes bounded by patch
            node_in_grid = [node in bound_node for node in grid_nodes]
            [x for x, y in zip(grid_nodes, node_in_grid) if y]
            pass

        # 1 area of patch in the grid

        # 2. find midpoint of area

        pass
