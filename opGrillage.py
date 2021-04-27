import pandas as pd
import numpy as np
import math
import openseespy.opensees as ops
from datetime import datetime


class opGrillage:
    """
    Grillage Generator class
    """

    def __init__(self, bridge_name, long_dim, width, skew, num_long_grid,
                 num_trans_grid, cantilever_edge, mesh_type):
        """Initialize the GrillageGenerator class"""
        # Section placeholders
        self.section_arg = None
        self.section_tag = None
        self.section_type = None
        self.section_group_noz = []     # list of tag representing ele groups of long mem
        self.section_group_nox = []     # list of tag representing ele groups of trans mem
        self.group_ele_dict = None      # dictionary of ele groups e.g. [ "name of group": tag ]
        self.global_element_list = None   # list of all elements in grillage
        self.ele_group_assigned_list = None # list recording assigned ele groups in grillage model
        # model information
        self.mesh_type = mesh_type
        self.model_name = bridge_name
        # global dimensions of grillage
        self.long_dim = long_dim  # span , also c/c between support bearings
        self.width = width  # length of the bearing support - if skew  = 0 , this corresponds to width of bridge
        self.skew = skew  # angle in degrees
        # Properties of grillage
        self.num_long_gird = num_long_grid  # number of longitudinal beams
        self.num_trans_grid = num_trans_grid  # number of grids for transverse members
        self.edge_width = cantilever_edge  # width of cantilever edge beam

        # instantiate matrices for geometric dependent properties
        self.trans_dim = None  # to be calculated automatically based on skew
        self.breadth = None  # to be calculated automatically based on skew
        self.spclonggirder = None  # to be automated
        self.spctransslab = None  # to be automated
        # initialize lists
        self.Nodedata = []  # array like to be populated
        self.nox = []  # line mesh in x direction
        self.noz = []  # line mesh in z direction
        # initiate list of various elements of grillage model, each entry of list is a sublist [node_i, node_j, eletag]
        self.long_mem = []  # longitudinal members
        self.trans_mem = []  # transverse members
        self.support_nodes = []  # list of nodes at support regions
        self.concrete_prop = []  # list of concrete properties arguments
        self.steel_prop = []  # list of steel properties arguments
        self.vxz_skew = []  # vector xz of skew elements - for section transformation

        # initialize tags of grillage elements - default tags are for standard elements of grillage
        # tags are used to link set properties to appropriate elements for element() command

        # later change these to match the transformation tag of either: (1) global orthogonal direction (x and z) or
        # (2) skew
        self.longitudinal_tag = 1
        self.longitudinal_edge_1_tag = 2
        self.longitudinal_edge_2_tag = 3
        self.transverse_tag = 4
        self.transverse_edge_1_tag = 5
        self.transverse_edge_2_tag = 6

        # rules for grillage automation - default values are in place, use keyword during class instantiation
        self.min_long_spacing = 1  # default 1m
        self.max_long_spacing = 2  # default 1m
        self.min_trans_spacing = 1  # default 1m
        self.max_trans_spacing = 2  # default 2m
        self.trans_to_long_spacing = 1  # default 1m
        self.min_grid_long = 9  # default 9 mesh odd number
        self.min_grid_trans = 5  # default 5 mesh odd number
        self.ortho_mesh = True  # boolean for grillages with skew < 15-20 deg
        self.y_elevation = 0  # default elevation of grillage wrt OPmodel coordinate system
        self.min_grid_ortho = 3  # for orthogonal mesh (skew>skew_threshold) region of orthogonal area default 3
        self.ndm = 3  # num model dimension - default 3
        self.ndf = 6  # num degree of freedom - default 6
        # rules for material definition
        self.mat_type_op = "Concrete01"  # material tag of concrete (default uniaxial Concrete01)
        self.mat_matrix = []  # list of argument for material - user define based on Openseespy convention
        # default vector for support (for 2D grillage in x - z plane)
        self.fix_val_pin = [1, 1, 1, 0, 0, 0]  # pinned
        self.fix_val_roller_x = [0, 1, 1, 0, 0, 0]  # roller
        # special rules for grillage - alternative to Properties of grillage definition - use for special dimensions
        self.nox_special = None  # array specifying custom coordinate of longitudinal nodes
        self.noz_special = None  # array specifying custom coordinate of transverse nodes
        self.skew_threshold = [10, 30]  # threshold for grillage to allow option of mesh choices
        self.member_group_tol = 0.001
        self.deci_tol = 4  # tol of decimal places
        # to be added
        # - special rule for multiple skew
        # - rule for multiple span + multi skew
        # - rule for pier

        # Initiate py file output
        self.filename = "{}_op.py".format(self.model_name)
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
        # generate nodes and elements of model
        self.create_nodes()

    # node procedure
    def create_nodes(self):
        # calculate edge length of grillage
        self.trans_dim = self.width / math.cos(self.skew / 180 * math.pi)
        # check for orthogonal mesh requirement
        self.check_skew()

        # 1 create Opensees model space
        self.op_model_space()
        # check mesh type and run procedure accordingly
        if self.ortho_mesh:
            print("Mesh type = Orthogonal. Valid angle {} greater than threshold {} ".format(self.skew,
                                                                                             self.skew_threshold))
            # perform orthogonal meshing
            self.orthogonal_mesh()
            v = self.get_vector_xz()
            # generate command lines for 3 ele transformation in orthogonal mesh
            self.op_ele_transform_input(1, [0, 0, 1])  # x dir members
            self.op_ele_transform_input(2, [v[0], 0, v[1]])  # z dir members (skew)
            self.op_ele_transform_input(3, [1, 0, 0])  # z dir members orthogonal
        else:  # skew mesh requirement
            print(
                "Mesh type = Skew. Valid skew angle: {} less than threshold {} ".format(self.skew, self.skew_threshold))
            # perform skewed meshing
            self.skew_mesh()
            v = self.get_vector_xz()
            # generate command lines for 2 ele transformation in skew mesh
            self.op_ele_transform_input(1, [0, 0, 1])  # x dir members
            self.op_ele_transform_input(2, [v[0], 0, v[1]])  # z dir members (skew)

        # 2 generate command lines in output py file
        self.op_create_nodes()  # write node() commands
        self.get_trans_edge_nodes()  # get support nodes
        self.op_fix()  # write fix() command for support nodes

    #
    def boundary_cond_input(self, restraint_nodes, restraint_vector):
        """
        Function to define support boundary conditions for fix command arguments

        :param restraint_nodes: list of node tags to be restrained
        :param restraint_vector: list representing node restraint for Nx Ny Nz, Mx My Mz respectively.
                                    represented by 1 (fixed), and 0 (free)
        :return:
        """
        for nodes in restraint_nodes:
            self.support_nodes.append([nodes, restraint_vector])

    def section_property_input(self, section_tag, section_type, section_arg):
        """
        Function to define section variables for section command arguments.

        :param section_tag: tag argument of section
        :param section_type: type argument of section - see Opensees for appropriate types
        :param section_arg: list of arguments for section command - see Opensees for conventions of arguments
        :return:
        """
        self.section_type = section_type
        self.section_tag = section_tag
        self.section_arg = section_arg
        # run and generate code line for section
        self.op_section_generate()

    # functions to write ops commands to output py file
    def op_ele_transform_input(self, trans_tag, vector_xz, transform_type="Linear"):
        ops.geomTransf(transform_type, trans_tag, *vector_xz)
        with open(self.filename, 'a') as file_handle:
            file_handle.write("# create transformation {}\n".format(trans_tag))
            file_handle.write("ops.geomTransf(\"{type}\", {tag}, *{vxz})\n".format(
                type=transform_type, tag=trans_tag, vxz=vector_xz))

    def op_model_space(self):
        ops.model('basic', '-ndm', self.ndm, '-ndf', self.ndf)
        with open(self.filename, 'a') as file_handle:
            file_handle.write("ops.wipe()\n")
            file_handle.write("ops.model('basic', '-ndm', {ndm}, '-ndf', {ndf})\n".format(ndm=self.ndm, ndf=self.ndf))

    def op_create_nodes(self):
        with open(self.filename, 'a') as file_handle:
            file_handle.write("# Node generation procedure\n")
        for node_point in self.Nodedata:
            ops.node(node_point[0], node_point[1], node_point[2], node_point[3])
            with open(self.filename, 'a') as file_handle:
                file_handle.write("ops.node({tag}, {x:.4f}, {y:.4f}, {z:.4f})\n".format(tag=node_point[0],
                                                                                        x=node_point[1],
                                                                                        y=node_point[2],
                                                                                        z=node_point[3]))
            # print("Node number: {} created".format(node_point[0]))
        # create node recorder line
        # with open(self.filename, 'a') as file_handle:
        #     file_handle.write("ops.recorder('Node', '-file', \'{}.txt\')\n".format(self.filename[:-3]))

    def set_grillage_long_mem(self, op_member_prop_class, beam_ele_type, group=1):
        """
        Function to set section properties to longitudinal element groups of grillage model
        :param op_member_prop_class:
        :param trans_tag:
        :param beam_ele_type:
        :param group:
        :return:
        Note: for longitudinal members, transform tag is 1 (preset) - see op_ele_transform_input
        """
        with open(self.filename, 'a') as file_handle:
            file_handle.write("# Element generation for section: {}\n".format(group))
        # get output string - sorted according to convention of Openseespy
        prop = op_member_prop_class.output_arguments()
        for ele in self.long_mem:
            if ele[2] == group:
                with open(self.filename, 'a') as file_handle:
                    file_handle.write("ops.element(\"{type}\", {tag}, *[{i}, {j}], *{memberprop}, {transtag})\n"
                                      .format(type=beam_ele_type, tag=ele[3], i=ele[0], j=ele[1],
                                              memberprop=prop, transtag=1))

    def set_grillage_trans_mem(self, op_member_prop_class, beam_ele_type, group=1):
        """
        Function to set section properties to transverse element groups of grillage model
        :param op_member_prop_class:
        :param trans_tag:
        :param beam_ele_type:
        :param group:
        :return:

        Note: for transverse members, transform tag is 2 (preset) - see op_ele_transform_input
        """
        with open(self.filename, 'a') as file_handle:
            file_handle.write("# Element generation for section: {}\n".format(group))
        # get output string - sorted according to convention of Openseespy
        prop = op_member_prop_class.output_arguments()
        for ele in self.trans_mem:
            if ele[2] == group:
                with open(self.filename, 'a') as file_handle:
                    file_handle.write("ops.element(\"{type}\", {tag}, *[{i}, {j}], *{memberprop}, {transtag})\n"
                                      .format(type=beam_ele_type, tag=ele[3], i=ele[0], j=ele[1],
                                              memberprop=prop, transtag=2))

    def set_grillage_members(self, op_member_prop_class, beam_ele_type, member='long_mem'):

        # get list of elements for specified element member of grillage
        with open(self.filename, 'a') as file_handle:
            file_handle.write("# Element generation for section: {}\n".format(member))
        #         element  tag   *[ndI ndJ]  A  E  G  Jx  Iy   Iz  transfOBJs
        # get output string - sorted according to convention of Openseespy
        prop = op_member_prop_class.output_arguments()
        # loop each element in list, assign and write element() command
        for ele in self.global_element_list:
            # ops.element(beam_ele_type, ele[3],
            #            *[ele[0], ele[1]], *op_member_prop_class, trans_tag)  ###
            if ele[2] == self.group_ele_dict[member]:
                with open(self.filename, 'a') as file_handle:
                    file_handle.write("ops.element(\"{type}\", {tag}, *[{i}, {j}], *{memberprop}, {transtag})\n"
                                      .format(type=beam_ele_type, tag=ele[3], i=ele[0], j=ele[1],
                                              memberprop=prop, transtag=ele[4]))

    def op_section_generate(self):
        with open(self.filename, 'a') as file_handle:
            file_handle.write("# Create section: \n")
            file_handle.write(
                "ops.section({}, {}, *{})\n".format(self.section_type, self.section_tag, self.section_arg))

    def op_fix(self):
        with open(self.filename, 'a') as file_handle:
            file_handle.write("# Boundary condition implementation\n")
        for boundary in self.support_nodes:
            # ops.fix(boundary[0], *boundary[1])
            with open(self.filename, 'a') as file_handle:
                file_handle.write("ops.fix({}, *{})\n".format(boundary[0], boundary[1]))

    def op_uniaxial_material(self):
        # function to generate uniaxialMaterial() command in output py file
        # ops.uniaxialMaterial(self.mat_type_op, 1, *self.mat_matrix)
        with open(self.filename, 'a') as file_handle:
            file_handle.write("# Material definition \n")
            file_handle.write("ops.uniaxialMaterial(\"{}\", 1, *{})\n".format(self.global_mat_object.mat_type,
                                                                              self.global_mat_object.mat_vec))

    # Functions related to mesh generation
    def get_vector_xz(self):
        # Function to calculate vector xz used for geometric transformation of local section properties
        # return: vector parallel to plane xz of member (see geotransform Opensees) for skew members (member tag 5)

        # vector rotate 90 deg clockwise (x,y) -> (y,-x)
        # [breadth width] is a vector parallel to skew
        x = self.width
        y = -(-self.breadth)
        # normalize vector
        length = math.sqrt(x ** 2 + y ** 2)
        vec = [x / length, y / length]
        return vec

    def get_trans_edge_nodes(self):
        # function to identify nodes at edges of the model along transverse direction (trans_edge_1 and trans_edge_2)
        # function then assigns pinned support and roller support to nodes in trans_edge_1 and trans_edge_2 respectively
        assign_list = [] # list recording assigned elements to check against double assignment
        for (count, ele) in enumerate(self.trans_mem):
            if ele[2] == 5:  # if its a support node (tag = 5 default for skew)
                if not ele[0] in assign_list: # check if ele is not in the assign list
                    assign_list.append(ele[0])
                    self.support_nodes.append([ele[0], self.fix_val_pin])
                else: # node not in list, assign
                    pass
                # if true, assign ele as support
                if not ele[1] in assign_list:  # check if ele is not in the assign list
                    assign_list.append(ele[1])
                    self.support_nodes.append([ele[1], self.fix_val_pin])
                else:  # node not in list, assign
                    pass

    def get_region_b(self, reg_a_end, step):

        # Function to calculate the node coordinate for skew region B
        # -> triangular breadth along the longitudinal direction
        # :param step: list containing transverse nodes (along z dir)
        # :param reg_a_end: last node from regA (quadrilateral region)
        # :return: node coordinate for skew triangular area (region B1 or B2)

        regB = [reg_a_end]  # initiate array regB
        for node in range(2, len(step)):  # minus 2 to ignore first and last element of step
            regB.append(self.long_dim - step[-node] * np.abs(np.tan(self.skew / 180 * math.pi)))
        # after append, add last element - self.long_dim
        regB.append(self.long_dim)
        regB = np.array(regB)
        return regB

    def check_skew(self):
        # function: (1) controlling boolean for mesh type and (2) check mesh threshold
        if self.mesh_type == "Ortho":
            self.ortho_mesh = True
        else:
            self.ortho_mesh = False

        # checks mesh type options are within the allowance threshold
        if np.abs(self.skew) <= self.skew_threshold[0] and self.ortho_mesh:
            # print
            raise Exception('Orthogonal mesh not allowed for angle less than {}'.format(self.skew_threshold[0]))
        elif np.abs(self.skew) >= self.skew_threshold[1] and not self.ortho_mesh:
            raise Exception('Oblique mesh not allowed for angle greater than {}'.format(self.skew_threshold[1]))

    def get_long_grid_nodes(self):
        # Function to output array of grid nodes along longitudinal direction
        last_girder = (self.width - self.edge_width)  # coord of last girder
        nox_girder = np.linspace(start=self.edge_width, stop=last_girder, num=self.num_long_gird)
        step = np.hstack((np.hstack((0, nox_girder)), self.width))  # array containing z coordinate
        return step

    def identify_member_groups(self):
        # identify element groups in grillage based on line mesh vectors self.nox and self.noz

        # get the groups of elements
        self.section_group_noz = self.characterize_node_diff(self.noz, self.deci_tol)
        self.section_group_nox = self.characterize_node_diff(self.nox, self.deci_tol)
        # update self.section_group_nox
        self.section_group_nox = [x+max(self.section_group_noz) for x in self.section_group_nox]
        # set groups dictionary
        if not self.ortho_mesh:  # if skew mesh
            if max(self.section_group_nox) <= 6:  # if true set standard section for variable
                self.group_ele_dict = {"edge_beam": 1, "exterior_main_beam_1": 2, "interior_main_beam": 3,
                                  "exterior_main_beam_2": 4, "edge_slab": 5, "transverse_slab": 6}
        else:  # orthogonal mesh, generate respective group dictionary
            pass
        # print groups to terminal
        print("Total groups of elements in longitudinal : {}".format(max(self.section_group_noz)))
        print("Total groups of elements in transverse : {}".format(max(self.section_group_nox)))

    @staticmethod
    def characterize_node_diff(node_list, tol):
        """
        Function to characterize the groups of elements based on spacings of node points in the node point list
        :param tol: float of tolerance for checking spacings in np.diff() function
        :param node_list: list containing node points along orthogonal axes (x and z)
        :return ele_group: list containing integers representing the groups of elements
        """
        ele_group = [1]  # initiate element group list, first element is group 1 edge beam
        spacing_diff_set = {} # initiate set recording the diff in spacings
        diff_list = np.round(np.diff(node_list), decimals=tol)  # spacing of the node list- checked with tolerance
        counter = 1
        for count in range(1, len(node_list)):
            # calculate the spacing diff between left and right node of current node
            if count >= len(diff_list):  # counter exceed the diff_list (size of diff list = size of node_list - 1)
                break  # break from loop, return list
            # spacing_diff = diff_list[count - 1] - diff_list[count]
            spacing_diff = [diff_list[count - 1], diff_list[count]]
            if repr(spacing_diff) in spacing_diff_set:
                # spacing recorded in spacing_diff_set
                # set the tag
                ele_group.append(spacing_diff_set[repr(spacing_diff)])
            else:
                # record new spacing in spacing_diff_set
                spacing_diff_set[repr(spacing_diff)] = counter + 1
                # set tag
                ele_group.append(spacing_diff_set[repr(spacing_diff)])
                counter += 1
        ele_group.append(1)  # add last element of list (edge beam group 1)
        return ele_group

    # skew meshing function
    def skew_mesh(self):
        # automate skew meshing
        if self.nox_special is None:  # check  special rule for slab spacing, else proceed automation of node
            self.nox = np.linspace(0, self.long_dim, self.num_trans_grid)  # array like containing node x coordinate
        else:
            self.nox = self.nox_special  # assign custom array to nox array
        self.breadth = self.trans_dim * math.sin(self.skew / 180 * math.pi)  # length of skew edge in x dir
        self.noz = self.get_long_grid_nodes()  # mesh points in z direction
        # identify member groups based on nox and noz
        self.identify_member_groups()  # returns section_group_nox and section_group_noz
        # initiate tag counters for node and elements
        nodetagcounter = 1  # counter for nodetag
        eletagcounter = 1  # counter for eletag

        for pointz in self.noz:  # loop for each mesh point in z dir
            noxupdate = self.nox - pointz * np.tan(
                self.skew / 180 * math.pi)  # get nox for current step in transverse mesh
            for pointx in noxupdate:  # loop for each mesh point in x dir (nox)
                # populate nodedata array - inputs [nodetag,x,y,z]
                self.Nodedata.append(
                    [nodetagcounter, pointx, self.y_elevation, pointz])  # NOTE here is where to change X Y plane
                nodetagcounter += 1
        # print to terminal
        print("Nodes created. Number of nodes = {}".format(nodetagcounter - 1))

        # procedure to link nodes to form Elements of grillage model
        # each element is then assigned a "standard element tag" e.g. self.longitudinal_tag = 1
        for node_row_z in range(0, len(self.noz)):  # loop for each line mesh in z direction
            for node_col_x in range(1, len(self.nox)):  # loop for each line mesh in x direction
                current_row_z = node_row_z * len(self.nox)  # get current row's (z axis) nodetagcounter
                next_node_row_z = (node_row_z + 1) * len(self.nox)  # get next row's (z axis) nodetagcounter
                # link nodes along current row (z axis), in the x direction
                self.long_mem.append([current_row_z + node_col_x, current_row_z + node_col_x + 1,
                                      self.section_group_noz[node_row_z], eletagcounter, 1])
                eletagcounter += 1
                # if node_row_z == 0:  # first row (z axis) of nodes
                #     self.long_edge_1.append([cumulative_row_z + node_col_x, cumulative_row_z + node_col_x + 1,
                #                              self.longitudinal_edge_1_tag, eletagcounter])
                #     # record as edge beam with tag 2
                #     eletagcounter += 1
                # elif node_row_z == len(self.noz) - 1:  # last row (z axis) of nodes
                #     self.long_edge_2.append([cumulative_row_z + node_col_x, cumulative_row_z + node_col_x + 1,
                #                              self.longitudinal_edge_2_tag,
                #                              eletagcounter])  # record as edge beam with section 3
                #     eletagcounter += 1
                # else:  # row of nodes in between edges of grillage ( 0 < z < z max)
                #     self.long_mem.append([cumulative_row_z + node_col_x, cumulative_row_z + node_col_x + 1,
                #                           self.longitudinal_tag, eletagcounter])
                #     # record as longitudinal beam with section tag 1
                #     eletagcounter += 1

                # link nodes in the z direction (e.g. transverse members)
                if next_node_row_z == nodetagcounter - 1:  # if looping last row of line mesh z
                    pass  # do nothing (exceeded the z axis edge of the grillage)
                # elif current_row_z + node_col_x - node_row_z * len(
                #         self.nox) == 1:  # check if coincide with edge of line mesh z
                #     self.trans_edge_1.append(
                #         [current_row_z + node_col_x, next_node_row_z + node_col_x,
                #          self.transverse_tag, eletagcounter])  # record as edge slab with section 4
                #     eletagcounter += 1
                else:  # assigning elements in transverse direction (z)
                    self.trans_mem.append([current_row_z + node_col_x, next_node_row_z + node_col_x,
                                           self.section_group_nox[node_col_x - 1], eletagcounter, 2])
                    # section_group_nox counts from 1 to 12, therefore -1 to start counter 0 to 11
                    eletagcounter += 1
            if next_node_row_z >= len(self.nox) * len(self.noz):  # check if current z coord is last row
                pass  # last column (x = self.nox[-1]) achieved, no more assignment
            else:  # assign last transverse member at last column (x = self.nox[-1])
                self.trans_mem.append([current_row_z + node_col_x + 1, next_node_row_z + node_col_x + 1,
                                       self.section_group_nox[node_col_x], eletagcounter, 2])
                # after counting section_group_nox 0 to 11, this line adds the counter of 12
                eletagcounter += 1
        # combine long and trans member elements to global list
        self.global_element_list = self.long_mem+self.trans_mem
        print("Element generation completed. Number of elements created = {}".format(eletagcounter - 1))


    # orthogonal meshing method
    def orthogonal_mesh(self):
        # Note special rule for nox does not apply to orthogonal mesh - automatically calculates the optimal ortho mesh
        #             o o o o o o
        #           o
        #         o
        #       o o o o o o
        #         b    +  ortho
        self.breadth = self.trans_dim * np.abs(math.sin(self.skew / 180 * math.pi))  # length of skew edge in x dir
        self.noz = self.get_long_grid_nodes()  # mesh points in transverse direction

        # Generate nox based on two orthogonal region: (A)  quadrilateral area, and (B)  triangular area
        regA = np.linspace(0, self.long_dim - self.breadth, self.num_trans_grid)
        # RegA consist of overlapping last element
        # RegB first element overlap with RegA last element
        regB = self.get_region_b(regA[-1], self.noz)  # nodes @ region B startswith last entry of region A up to
        self.nox = np.hstack((regA[:-1], regB))  # removed overlapping element
        # identify member groups based on nox and noz
        self.identify_member_groups()  # returns section_group_nox and section_group_noz
        # mesh region A quadrilateral area
        nodetagcounter = 1  # counter for nodetag, updates after creating each nodes
        eletagcounter = 1  # counter for element, updates after creating each elements
        for pointz in self.noz:  # loop for each mesh point in z dir
            for pointx in regA[:-1]:  # loop for each mesh point in x dir (nox)
                # populate nodedata array - inputs [nodetag,x,y,z]
                self.Nodedata.append([nodetagcounter, pointx, self.y_elevation, pointz])
                nodetagcounter += 1
        print('Number of elements in Region A: {}'.format(nodetagcounter - 1))

        # create elements of region A
        for node_row_z in range(0, len(self.noz)):
            for node_col_x in range(1, len(regA[:-1])):
                inc = node_row_z * len(regA[:-1])  # incremental nodes per self.noz (node grid along transverse)
                next_inc = (node_row_z + 1) * len(
                    regA[:-1])  # increment nodes after next self.noz (node grid along transverse)
                if node_row_z == 0:  # first and last row are edge beams
                    self.long_edge_1.append(
                        [inc + node_col_x, inc + node_col_x + 1, self.longitudinal_edge_1_tag, eletagcounter])
                    # record as edge beam with section 2
                    eletagcounter += 1
                elif node_row_z == len(self.noz) - 1:
                    self.long_edge_2.append(
                        [inc + node_col_x, inc + node_col_x + 1, self.longitudinal_edge_2_tag, eletagcounter])
                    # record as edge beam with section 2
                    eletagcounter += 1
                else:
                    self.long_mem.append(
                        [inc + node_col_x, inc + node_col_x + 1, self.longitudinal_tag, eletagcounter])
                    # record as longitudinal beam with section 1
                    eletagcounter += 1
                if node_row_z != len(self.noz) - 1:  # last row
                    self.trans_mem.append([inc + node_col_x, next_inc + node_col_x, self.transverse_tag, eletagcounter])
                    # record as slab with section 3
                    eletagcounter += 1
            # last column of parallel
            if node_row_z != len(self.noz) - 1:
                self.trans_mem.append(
                    [inc + node_col_x + 1, next_inc + node_col_x + 1, self.transverse_tag, eletagcounter])
                # record as slab with section 3
                eletagcounter += 1
        print('Elements automation complete for region A: Number of elements = {}'.format(eletagcounter - 1))

        # mesh region B triangular area
        # B1 @ right support
        b1_node_tag_start = nodetagcounter - 1  # last node tag of region A
        regBupdate = regB  # initiate list for line mesh of region B1 - updated each loop by removing last element
        if self.skew < 0:  # check for angle sign
            line_mesh_z_b1 = reversed(self.noz)  # (0 to ascending for positive angle,descending for -ve)
        else:
            line_mesh_z_b1 = self.noz
        for pointz in line_mesh_z_b1:  # loop for each line mesh in z dir
            for pointx in regBupdate:  # loop for each line mesh in x dir (nox)
                self.Nodedata.append([nodetagcounter, pointx, self.y_elevation, pointz])
                nodetagcounter += 1
            regBupdate = regBupdate[:-1]  # remove last element for next self.noz (skew boundary)

        # Elements mesh for region B1
        regBupdate = regB  # reset placeholder
        row_start = b1_node_tag_start  # last nodetag of region A
        if self.skew < 0:
            reg_a_col = row_start  # nodetag of last node in last row of region A (last nodetag of region A)
        else:  # nodetag of last node in first row of region A
            reg_a_col = len(regA[:-1])  # the last node of a single row + ignore last element of reg A (overlap regB)
        for num_z in range(0, len(self.noz)):
            # element that link nodes with those from region A
            if self.skew < 0:  # if negative skew, loop starts from the last row (@ row = width)
                if num_z == 0:
                    self.long_edge_2.append([reg_a_col, row_start + 1, self.longitudinal_edge_2_tag, eletagcounter])
                    eletagcounter += 1
                elif num_z == len(self.noz) - 1:
                    self.long_edge_1.append([reg_a_col, row_start + 1, self.longitudinal_edge_1_tag, eletagcounter])
                    eletagcounter += 1
                else:
                    self.long_mem.append([reg_a_col, row_start + 1, self.longitudinal_tag, eletagcounter])
                    eletagcounter += 1
            else:  # skew is positive,
                if num_z == 0:
                    self.long_edge_1.append([reg_a_col, row_start + 1, self.longitudinal_edge_1_tag, eletagcounter])
                    eletagcounter += 1
                elif num_z == len(self.noz) - 1:
                    self.long_edge_2.append([reg_a_col, row_start + 1, self.longitudinal_edge_2_tag, eletagcounter])
                    eletagcounter += 1
                else:
                    self.long_mem.append([reg_a_col, row_start + 1, self.longitudinal_tag, eletagcounter])
                    eletagcounter += 1
            # loop for each column node in x dir
            # create elements for each nodes in current row (z axis) in the x direction (list regBupdate)
            for num_x in range(1, len(regBupdate)):
                if num_z == 0:  # first and last row are edge beams
                    if self.skew < 0:
                        self.long_edge_2.append(
                            [row_start + num_x, row_start + num_x + 1, self.longitudinal_edge_2_tag, eletagcounter])
                        eletagcounter += 1
                        # record as edge beam with section 2
                    else:
                        self.long_edge_1.append(
                            [row_start + num_x, row_start + num_x + 1, self.longitudinal_edge_1_tag, eletagcounter])
                        eletagcounter += 1
                        # record as edge beam with section 2
                elif num_z != len(self.noz) - 1:
                    self.long_mem.append(
                        [row_start + num_x, row_start + num_x + 1, 1, eletagcounter])
                    # record as longitudinal beam with section 1
                    eletagcounter += 1
                # transverse member
                self.trans_mem.append([row_start + num_x, row_start + num_x + len(regBupdate),
                                       self.transverse_tag, eletagcounter])
                eletagcounter += 1
            if num_z != len(self.noz) - 1:  # last node of skew is single node, no element, break self.noz
                self.trans_edge_2.append([row_start + num_x + 1, row_start + num_x + len(regBupdate),
                                          self.transverse_edge_2_tag, eletagcounter])  # support skew
                eletagcounter += 1

            row_start = row_start + len(regBupdate)  # update next self.noz start node of region B
            regBupdate = regBupdate[:-1]  # remove last element for next self.noz (skew boundary)
            # check for skew angle varients of region B1 loop (positive or negative)
            if self.skew < 0:
                reg_a_col = reg_a_col - len(regA[:-1])  # update row node number correspond with region A (decreasing)
            else:
                reg_a_col = reg_a_col + len(regA[:-1])  # update row node number correspond with region A (increasing)
        print('Elements automation complete for region B1 and A')

        # B2 left support
        regBupdate = -regB + regA[-1]  # left side of quadrilateral area, regB can lie in negative x axis
        if self.skew < 0:  # check for angle sign
            line_mesh_z_b2 = self.noz  # (descending for positive angle,ascending for -ve)
        else:
            line_mesh_z_b2 = reversed(self.noz)
        for pointz in line_mesh_z_b2:
            for pointx in regBupdate[1:]:  # remove counting first element overlap with region A
                self.Nodedata.append([nodetagcounter, pointx, self.y_elevation, pointz])
                nodetagcounter += 1
            regBupdate = regBupdate[:-1]  # remove last element (skew boundary) for next self.noz

        # Element meshing for region B2
        # takes row_start from B1 auto meshing loop
        if self.skew < 0:
            reg_a_col = 1  # links to first node (region A)
        else:
            reg_a_col = 1 + (len(self.noz) - 1) * len(regA[:-1])  # links to first node last row of region A
        regBupdate = -regB + regA[-1]  # reset placeholder
        for num_z in range(0, len(self.noz)):
            # link nodes from region A
            if num_z == 0:
                if self.skew < 0:
                    self.long_edge_1.append([reg_a_col, row_start + 1, self.longitudinal_edge_1_tag, eletagcounter])
                    eletagcounter += 1
                else:
                    self.long_edge_2.append([reg_a_col, row_start + 1, self.longitudinal_edge_2_tag, eletagcounter])
                    eletagcounter += 1
            elif num_z != len(self.noz) - 1:
                self.long_mem.append([row_start + 1, reg_a_col, self.longitudinal_tag, eletagcounter])
                eletagcounter += 1
            # loop for each column node in x dir
            for num_x in range(1, len(regBupdate[1:])):
                if num_z == 0:  # first and last row are edge beams
                    if self.skew < 0:
                        self.long_edge_1.append([row_start + num_x + 1, row_start + num_x, self.longitudinal_edge_1_tag
                                                    , eletagcounter])
                        eletagcounter += 1
                    else:
                        self.long_edge_2.append([row_start + num_x + 1, row_start + num_x, self.longitudinal_edge_2_tag
                                                    , eletagcounter])
                        eletagcounter += 1
                    # record as edge beam with section 2
                elif num_z != len(self.noz) - 1:
                    self.long_mem.append(
                        [row_start + num_x + 1, row_start + num_x, self.longitudinal_tag, eletagcounter])
                    # record as longitudinal beam with section 1
                    eletagcounter += 1
                # transverse member
                self.trans_mem.append([row_start + num_x, row_start + num_x + len(regBupdate[1:]),
                                       self.transverse_tag, eletagcounter])
                eletagcounter += 1
            if num_z == len(self.noz) - 2:
                if self.skew < 0:  # if negative angle
                    self.trans_edge_1.append(
                        [reg_a_col + len(regA[:-1]), row_start + len(regBupdate[1:]), self.transverse_edge_1_tag,
                         eletagcounter])  # ele of node 1 to last node skew
                    eletagcounter += 1
                else:
                    self.trans_edge_1.append(
                        [1, row_start + len(regBupdate[1:]), self.transverse_edge_1_tag,
                         eletagcounter])  # ele of node 1 to last node skew
                    eletagcounter += 1
            elif num_z != len(
                    self.noz) - 1:  # num of nodes = num ele + 1, thus ignore last self.noz for implementing ele
                self.trans_edge_1.append(
                    [row_start + num_x + 1, row_start + num_x + len(regBupdate[1:]), self.transverse_edge_1_tag
                        , eletagcounter])  # support skew
                eletagcounter += 1
            # steps in transverse mesh, assign nodes of skew nodes

            row_start = row_start + len(regBupdate[1:])  # update next self.noz start node
            regBupdate = regBupdate[:-1]  # remove last element for next self.noz (skew boundary)

            if self.skew < 0:
                reg_a_col = reg_a_col + len(regA[:-1])  # update next self.noz node correspond with region A
            else:
                reg_a_col = reg_a_col - len(regA[:-1])  # update next self.noz node correspond with region A
        print('Elements automation complete for region B1 B2 and A')

    def compile_output(self, bridge_name):
        # function to output txt file containing model information:
        # Nodes and member elements.
        filename = "{}_properties.txt".format(bridge_name)
        with open(filename, 'w') as file_handle:
            # compile nodes
            file_handle.write("NODES\n")  # Header
            # file_handle.write(str(self.Nodedata))
            file_handle.writelines("%s\n" % nodes for nodes in self.Nodedata)  # Node data
            # compile connectivity
            file_handle.write("\nConnectivity\n")  # Header
            # write for each sections
            file_handle.write("long_mem \n")  # Sub_Header
            file_handle.writelines("%s\n" % ele for ele in self.long_mem)  #
            file_handle.write("long_edge_1\n")  # Sub_Header
            file_handle.writelines("%s\n" % ele for ele in self.long_edge_1)  #
            file_handle.write("long_edge_2\n")  # Sub_Header
            file_handle.writelines("%s\n" % ele for ele in self.long_edge_2)  #
            file_handle.write("trans_mem\n")  # Sub_Header
            file_handle.writelines("%s\n" % ele for ele in self.trans_mem)  #
            file_handle.write("trans_edge_1\n")  # Sub_Header
            file_handle.writelines("%s\n" % ele for ele in self.trans_edge_1)  #
            file_handle.write("trans_edge_2\n")  # Sub_Header
            file_handle.writelines("%s\n" % ele for ele in self.trans_edge_2)  #

    def set_material(self, material_obj):
        """
        Function to define material for Openseespy material model. For example, uniaxialMaterial, nDMaterial.

        :param mat_vec: list containing material properties following convention specified in Openseespy
        :param mat_type: str containing material type tag following available tags specified in Openseespy
        :return: Function populates object variables: (1) mat_matrix, and (2) mat_type_op.
        """
        self.global_mat_object = material_obj  # material matrix for

        self.op_uniaxial_material()

    # test output file
    def run_check(self):
        try:
            __import__(self.filename[:-3])  # run file
            print("File imported and run, OK")
        except:
            print("File error not executable")

    def run_gravity_analysis(self):
        # function to update output py file with commands for simple gravity analysis
        with open(self.filename, 'a') as file_handle:
            # write standard command lines for static analysis
            file_handle.write("#===========================\n# run simply load analysis\n#==========================\n")
            file_handle.write("ops.timeSeries('Linear', 1)\n")
            file_handle.write("ops.pattern('Plain', 1, 1)\n")
            file_handle.write("ops.load(20, 0.0, -1000, 0.0, 0, 0, 0)\n")

            file_handle.write("ops.integrator('LoadControl', 1/10)\n")  # Header
            file_handle.write("ops.numberer('Plain')\n")
            file_handle.write("ops.system('BandGeneral')\n")
            file_handle.write("ops.constraints('Plain')\n")
            file_handle.write("ops.test('NormDispIncr', 1e-8,6)\n")
            file_handle.write("ops.algorithm('Newton')\n")
            file_handle.write("ops.analysis('Static')\n")
            file_handle.write("ops.analyze(10)")

        # import and execute updated py file


# ----------------------------------------------------------------------------------------------------------------
# Member properties class
class Member:
    """
    Class for grillage members
    """

    def __init__(self, name, A, E, G, J, Iy, Iz, Ay, Az, op_ele_type="elasticBeamColumn"):
        self.name = name
        self.op_ele_type = op_ele_type
        self.Az = Az
        self.Ay = Ay
        self.Iz = Iz
        self.Iy = Iy
        self.J = J
        self.G = G
        self.E = E
        self.A = A

        # return argument list with convention following Openseespy - dependant on ele_type
        self.output_arguments()

    def output_arguments(self):
        """
        Function to output list argument according to element() command of variety of element tags
        in Opensees
        :return: list containing member properties in accordance with Openseespy input convention
        """
        section_input = None
        # assignment input based on ele type
        if self.op_ele_type == "ElasticTimoshenkoBeam":
            section_input = [self.E, self.G, self.A, self.J, self.Iy, self.Iz, self.Ay, self.Az]
            section_input = "[{:.3e}, {:.3e}, {:.3e}, {:.3e}, {:.3e}, {:.3e}, {:.3e}, {:.3e}]".format(self.E, self.G, self.A,
                                                                                               self.J,
                                                                                               self.Iy, self.Iz,
                                                                                               self.Ay, self.Az)
        elif self.op_ele_type == "elasticBeamColumn":  # eleColumn
            section_input = [self.E, self.G, self.A, self.J, self.Iy, self.Iz]
            section_input = "[{:.3e}, {:.3e}, {:.3e}, {:.3e}, {:.3e}, {:.3e}]".format(self.E, self.G, self.A,
                                                                                 self.J, self.Iy, self.Iz)
        return section_input

    def set_section(self):
        pass


# ----------------------------------------------------------------------------------------------------------------
class Material:
    """
    Class for material properties definition
    """

    def __init__(self, mat_type, mat_vec=[]):
        # super(UniAxialElasticMaterial, self).__init__(length, length)
        self.mat_type = mat_type
        self.mat_vec = mat_vec

        pass


class UniAxialElasticMaterial(Material):
    """
    Class for uniaxial material prop
    """

    def __init__(self, mat_type, mat_vec=[]):
        # super(UniAxialElasticMaterial, self).__init__(length, length)
        self.mat_type = mat_type
        self.mat_vec = mat_vec


class nDMaterial(Material):
    """
    Class for nD Material
    NOTE: Feature to be added after Uniaxial Material
    """

    def __init__(self, mat_type, mat_vec=[]):
        # super(UniAxialElasticMaterial, self).__init__(length, length)
        self.mat_type = mat_type
        self.mat_vec = mat_vec


# ----------------------------------------------------------------------------------------------------------------
class Section:
    def __init__(self, op_sec_tag, E, A, Iz, J, Ay, Az, Iy=None, G=None, alpha_y=None):
        self.op_sec_tag = op_sec_tag
        self.E = E
        self.A = A
        self.Iz = Iz
        self.Iy = Iy
        self.G = G
        self.Ay = Ay
        self.Az = Az
        self.J = J
        self.alpha_y = alpha_y
        # A, E, G, J, Iy, Iz, Ay, Az,
    # example
    # .section('Elastic', BeamSecTag,Ec,ABeam,IzBeam)


# ----------------------------------------------------------------------------------------------------------------
class GrillageMember:
    def __init__(self, section_obj, material_obj, name="Undefined"):
        self.name = name
        self.section_obj = section_obj
        self.material_obj = material_obj
