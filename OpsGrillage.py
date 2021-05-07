import numpy as np
import math
import openseespy.opensees as ops
from datetime import datetime


class OpsGrillage:
    """
    Main class of Openseespy grillage model wrapper. Outputs an executable py file which generates the prescribed
    Opensees grillage model based on user input.

    The class provides an interface for the user to specify the geometry of the grillage model. A keyword argument
    allows for users to select between skew/oblique or orthogonal mesh. Methods in this class allows users to input
    properties for various elements in the grillage model.
    """

    def __init__(self, bridge_name, long_dim, width, skew, num_long_grid,
                 num_trans_grid, edge_beam_dist, mesh_type="Ortho"):
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
        # Section placeholders
        self.section_arg = None
        self.section_tag = None
        self.section_type = None
        self.section_group_noz = []  # list of tag representing ele groups of long mem
        self.section_group_nox = []  # list of tag representing ele groups of trans mem
        self.spacing_diff_noz = []
        self.spacing_diff_nox = []
        # dict
        self.group_ele_dict = None  # dictionary of ele groups e.g. [ "name of group": tag ]
        self.global_element_list = None  # list of all elements in grillage
        self.ele_group_assigned_list = []  # list recording assigned ele groups in grillage model
        self.section_dict = {}  # dictionary of section tags
        # mesh object
        self.mesh_group = None

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
        self.edge_width = edge_beam_dist  # width of cantilever edge beam
        self.regA = []
        self.regB = []
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
        self.global_mat_object = []  # material matrix
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
        """
        Abstracted procedure to create nodes of grillage model. This procedure also handles sub-abstracted procedures
        involved in writing Opensees command: model(), node(), and fix() commands to output py file.
        :return: Output py file with model(), node() and fix() commands
        """
        # calculate edge length of grillage
        self.trans_dim = self.width / math.cos(self.skew / 180 * math.pi)
        # check for orthogonal mesh requirement
        self.check_skew()

        # 1 create Opensees model space
        self.op_model_space()
        # check mesh type and run procedure accordingly
        if self.ortho_mesh:
            # perform orthogonal meshing
            self.mesh_group = self.orthogonal_mesh()
        else:  # perform skew mesh
            self.mesh_group = self.skew_mesh()
        v = self.get_vector_xz()

        if self.ortho_mesh:
            # generate command lines for 3 ele transformation in orthogonal mesh
            self.op_ele_transform_input(1, [0, 0, 1])  # x dir members
            self.op_ele_transform_input(2, [v[0], 0, v[1]])  # z dir members (skew)
            self.op_ele_transform_input(3, [1, 0, 0])  # z dir members orthogonal
        else:
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
        User function to define support boundary conditions in addition to the model edges automatically detected
        by create_nodes() procedure.

        :param restraint_nodes: list of node tags to be restrained
        :type restraint_nodes: list
        :param restraint_vector: list representing node restraint for Nx Ny Nz, Mx My Mz respectively.
                                    represented by 1 (fixed), and 0 (free)
        :type restraint_vector: list
        :return: Append node fixity to the support_nodes class variable
        """
        for nodes in restraint_nodes:
            self.support_nodes.append([nodes, restraint_vector])

    # abstraction to write ops commands to output py file
    def op_ele_transform_input(self, trans_tag, vector_xz, transform_type="Linear"):
        """
        Abstracted procedure to write ops.geomTransf() to output py file.
        :param trans_tag: tag of transformation - set according to default 1, 2 and 3
        :param vector_xz: vector parallel to plane xz of the element. Automatically calculated by get_vector_xz()
        :param transform_type: transformation type
        :return: writes ops.geomTransf() line to output py file
        """
        # TODO assign transform_type
        # write geoTransf() command
        ops.geomTransf(transform_type, trans_tag, *vector_xz)
        with open(self.filename, 'a') as file_handle:
            file_handle.write("# create transformation {}\n".format(trans_tag))
            file_handle.write("ops.geomTransf(\"{type}\", {tag}, *{vxz})\n".format(
                type=transform_type, tag=trans_tag, vxz=vector_xz))

    def op_model_space(self):
        """
        Sub-abstracted procedure handled by create_nodes() function. This method creates the model() command
        in the output py file.
        :return: Output py file with wipe() and model() commands

        Note: For 3-D model, the default model dimension and node degree-of-freedoms are 3 and 6 respectively.
        This method automatically sets the aforementioned parameters to 2 and 4 respectively, for a 2-D problem.
        """
        # write model() command
        ops.model('basic', '-ndm', self.ndm, '-ndf', self.ndf)
        with open(self.filename, 'a') as file_handle:
            file_handle.write("ops.wipe()\n")
            file_handle.write("ops.model('basic', '-ndm', {ndm}, '-ndf', {ndf})\n".format(ndm=self.ndm, ndf=self.ndf))

    def op_create_nodes(self):
        """
        Sub-abstracted procedure handled by create_nodes() function. This method create node() command for each node
        point generated during meshing procedures.
        :return: Output py file populated with node() commands to generated the prescribed grillage model.
        """
        # write node() command
        with open(self.filename, 'a') as file_handle:
            file_handle.write("# Node generation procedure\n")
        for node_point in self.Nodedata:
            ops.node(node_point[0], node_point[1], node_point[2], node_point[3])
            with open(self.filename, 'a') as file_handle:
                file_handle.write("ops.node({tag}, {x:.4f}, {y:.4f}, {z:.4f})\n".format(tag=node_point[0],
                                                                                        x=node_point[1],
                                                                                        y=node_point[2],
                                                                                        z=node_point[3]))

    def op_fix(self):
        """
        Sub-abstracted procedure handed by create_nodes() function. This method writes the fix() command for
        boundary condition defintion in the grillage model.
        :return: Output py file populated with fix() command for boundary condition definition.
        """
        with open(self.filename, 'a') as file_handle:
            file_handle.write("# Boundary condition implementation\n")
        for boundary in self.support_nodes:
            # ops.fix(boundary[0], *boundary[1])
            with open(self.filename, 'a') as file_handle:
                file_handle.write("ops.fix({}, *{})\n".format(boundary[0], boundary[1]))

    def op_uniaxial_material(self):
        """

        :return:
        """
        # function to generate uniaxialMaterial() command in output py file
        # ops.uniaxialMaterial(self.mat_type_op, 1, *self.mat_matrix)
        with open(self.filename, 'a') as file_handle:
            file_handle.write("# Material definition \n")
            file_handle.write("ops.uniaxialMaterial(\"{}\", 1, *{})\n".format(self.global_mat_object.mat_type,
                                                                              self.global_mat_object.mat_vec))

    # Encapsulated functions pertaining to identifying element groups
    def identify_member_groups(self):
        """
        Abstracted method to identify member groups based on node spacings in orthogonal directions.
        :return:
        """
        # identify element groups in grillage based on line mesh vectors self.nox and self.noz

        # get the groups of elements
        self.section_group_noz, self.spacing_diff_noz, self.spacing_val_noz = self.characterize_node_diff(self.noz,
                                                                                                          self.deci_tol)
        self.section_group_nox, self.spacing_diff_nox, self.spacing_val_nox = self.characterize_node_diff(self.nox,
                                                                                                          self.deci_tol)
        # update self.section_group_nox counter to continue after self.section_group_noz
        self.section_group_nox = [x + max(self.section_group_noz) for x in self.section_group_nox]

        if self.ortho_mesh:
            # update self.section_group_nox first element to reflect element group of Region B
            self.section_group_nox[0] = self.section_group_nox[len(self.regA) - 1]
        else:  # else skew mesh do nothing
            pass
        # set groups dictionary
        if self.ortho_mesh:  # if ortho mesh
            if max(self.section_group_noz) <= 4:  # if true , standard sections set for longitudinal members
                self.group_ele_dict = {"edge_beam": 1, "exterior_main_beam_1": 2, "interior_main_beam": 3,
                                       "exterior_main_beam_2": 4, "edge_slab": 5, "transverse_slab": 6}
            else:  # groups
                self.group_ele_dict = {"edge_beam": 1, "exterior_main_beam_1": 2, "interior_main_beam": 3,
                                       "exterior_main_beam_2": 4, "edge_slab": 5, "transverse_slab": 6}
            # TODO : additional rules for orthogonal mesh group for custom line nodes
        else:  # skew mesh, run generate respective group dictionary
            if max(self.section_group_noz) <= 4:
                # dictionary applies to longitudinal members only
                self.group_ele_dict = {"edge_beam": 1, "exterior_main_beam_1": 2, "interior_main_beam": 3,
                                       "exterior_main_beam_2": 4, "edge_slab": 5, "transverse_slab": 6}
            else:  # section grouping greater than 6
                # TODO : rules for skew mesh if custom line nodes feature implemented
                # set variable up to 4 group (longitudinal)
                self.group_ele_dict = {"edge_beam": 1, "exterior_main_beam_1": 2, "interior_main_beam": 3,
                                       "exterior_main_beam_2": 4}
                # for transverse (group 5 and above) assign based on custom number
                # print to terminal assignment
                print()

            # orthogonal mesh rules
        # print groups to terminal
        print("Total groups of elements in longitudinal : {}".format(max(self.section_group_noz)))
        print("Total groups of elements in transverse : {}".format(max(self.section_group_nox)))

    @staticmethod
    def characterize_node_diff(node_list, tol):
        """
        Abstracted method to characterize the groups of elements based on spacings of node points in the node point list
        :param tol: float of tolerance for checking spacings in np.diff() function
        :param node_list: list containing node points along orthogonal axes (x and z)
        :return ele_group: list containing integers representing the groups of elements
        The function loops each element and characterize the element into groups based on the unique spacings between
        the element.
        """
        ele_group = [1]  # initiate element group list, first default is group 1 edge beam
        spacing_diff_set = {}  # initiate set recording the diff in spacings
        spacing_val_set = {}  # initiate set recoding spacing value
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
                spacing_val_set[counter + 1] = sum(spacing_diff)
                # set tag
                ele_group.append(spacing_diff_set[repr(spacing_diff)])
                counter += 1
        ele_group.append(1)  # add last element of list (edge beam group 1)
        return ele_group, spacing_diff_set, spacing_val_set

    def set_section(self, op_section_obj):
        """
        Abstracted procedure handled by set_member() function to write section() command for the elements

        """
        # extract section variables from Section class
        section_type = op_section_obj.op_section_type  # str of section type - Openseespy convention
        section_arg = op_section_obj.output_arguments_unit_width()  # list of argument for section
        # - Openseespy convention
        section_str = [section_type, section_arg]  # repr both variables as a list for keyword definition
        # check if section
        if not bool(self.section_dict):
            sectiontagcounter = 0  # if dict empty, start counter at 1
        else:
            sectiontagcounter = self.section_dict[list(self.section_dict)[-1]]

        if repr(section_str) in self.section_dict:
            # similar section in dict, means section was defined and section() command has previously been written
            pass  # do nothing
            # print to terminal
            print("Attempted definition of {} with tag {} has been previously defined"
                  .format(section_type, sectiontagcounter))
        else:  # dict not empty and section not found in section_dict, proceeed to create new keyword in dict
            # get last inserted element, set tag as sectiontagcounter
            # record section in dictionary
            self.section_dict[repr(section_str)] = sectiontagcounter + 1
            # run and generate code line for section
            with open(self.filename, 'a') as file_handle:
                file_handle.write("# Create section: \n")
                file_handle.write(
                    "ops.section(\"{}\", {}, *{})\n".format(section_type, sectiontagcounter + 1, section_arg))
            # print to terminal
            print("Section {}, of tag {} created".format(section_type, sectiontagcounter))

    def set_member(self, op_member_class, member=None):
        """
        Function to assign GrillageMember obj to element groups. Function then create ops.element() command for the
         prescribed element.
        :param op_member_class: Member object
        :param member: str of grillage element group to be assigned
        :return:
        assign member properties to all grillage element within specified group.

        Note: assignment of elements differs between skew and orthogonal mesh type.
        """
        # check input GrillageMember class
        if isinstance(op_member_class, GrillageMember):
            pass  # proceed with setting members
        else:  # raise exception
            Exception("Input member {} not a GrillageMember class".format(op_member_class))

        with open(self.filename, 'a') as file_handle:
            file_handle.write("# Element generation for section: {}\n".format(member))
        #         element  tag   *[ndI ndJ]  A  E  G  Jx  Iy   Iz  transform obj
        # get output string - sorted according to convention of Openseespy
        if op_member_class.section.unit_width:  # check if unit width
            # if yes, convert properties to match width of element
            # get element width based on member tag
            # node_width float
            node_width = self.spacing_val_nox[self.group_ele_dict[member] - max(self.section_group_noz)]
            #
            prop = op_member_class.section.output_arguments_unit_width(node_width / 2)
        else:  # get properties based on non-unit width
            prop = op_member_class.section.output_arguments_unit_width()
        # check if ele group has been assigned.
        if member in self.ele_group_assigned_list:
            raise Exception('Element Group {} has already been assigned'.format(member))
        if member is None:
            raise Exception('No member str variable specified')
        # check for section()
        if op_member_class.section.section_command_flag:
            # if true, write section() command prior to element definition
            self.set_section(op_member_class.section)  # set the section of the element member.
        # get beam type variable
        beam_ele_type = op_member_class.section.op_ele_type

        # begin assign and write element() command
        # ----------------------------------------

        # Check if assignment of all transverse members based on per m width properties
        if op_member_class.section.unit_width:
            # loop through the unique members based on spacings of nodes, assign all members (key-tag) in the transverse
            # direction
            for key, node_width in self.spacing_val_nox.items():

                # loop each element- find matching
                for ele in self.global_element_list:
                    if ele[2] == key + max(
                            self.section_group_noz):  # if element match key for transverse memeber loop
                        with open(self.filename, 'a') as file_handle:
                            file_handle.write(
                                "ops.element(\"{type}\", {tag}, *[{i}, {j}], *{memberprop}, {transtag})\n"
                                    .format(type=beam_ele_type, tag=ele[3], i=ele[0], j=ele[1],
                                            memberprop=prop, transtag=ele[4]))
                # add ele group to assigned list
                self.ele_group_assigned_list.append(key + max(self.section_group_noz))
        else:
            # direct assignment of members applies for longitudinal members
            for ele in self.global_element_list:
                # ops.element(beam_ele_type, ele[3],
                #            *[ele[0], ele[1]], *op_member_prop_class, trans_tag)  ###
                if ele[2] == self.group_ele_dict[member]:
                    with open(self.filename, 'a') as file_handle:
                        file_handle.write("ops.element(\"{type}\", {tag}, *[{i}, {j}], *{memberprop}, {transtag})\n"
                                          .format(type=beam_ele_type, tag=ele[3], i=ele[0], j=ele[1],
                                                  memberprop=prop, transtag=ele[4]))

            # add ele group to assigned list
            self.ele_group_assigned_list.append(self.group_ele_dict[member])
        # TODO element() command for ele type that takes section tag and material tag

        # print to terminal
        print("Members assigned {}".format(repr(self.ele_group_assigned_list)))
        if len(self.ele_group_assigned_list) != max(self.section_group_nox):
            print("Remaining members: {}".format(
                self.Diff(range(1, max(self.section_group_nox) + 1), self.ele_group_assigned_list)))
        else:
            print("All members assigned")

    # Encapsulated functions related to mesh generation
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
        assign_list = []  # list recording assigned elements to check against double assignment
        for (count, ele) in enumerate(self.trans_mem):
            if self.ortho_mesh:  # if orthogonal mesh
                if ele[2] == 5:  # if its a support node (tag = 5 default for skew)
                    if not ele[0] in assign_list:  # check if ele is not in the assign list
                        assign_list.append(ele[0])
                        self.support_nodes.append([ele[0], self.fix_val_pin])

                    # if true, assign ele as support
                    if not ele[1] in assign_list:  # check if ele is not in the assign list
                        assign_list.append(ele[1])
                        self.support_nodes.append([ele[1], self.fix_val_pin])
            else:  # skew mesh
                if ele[2] == 5:  # if its a support node (tag = 5 default for skew)
                    if not ele[0] in assign_list:  # check if ele is not in the assign list
                        assign_list.append(ele[0])
                        self.support_nodes.append([ele[0], self.fix_val_pin])

                    # if true, assign ele as support
                    if not ele[1] in assign_list:  # check if ele is not in the assign list
                        assign_list.append(ele[1])
                        self.support_nodes.append([ele[1], self.fix_val_pin])

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
        """
        Function to set boolean to true if orthogonal mesh option. This function is automatically called during __init__
        Function also checks if skew angle lies in allowable threshold
        - between 10-30 degree (var self.skew_threshold) both types of mesh (skew and orthogonal) are allowed.
        outside this bound, skew rules are strictly: (1) skew for angles less than 10 deg, and
        (2) orthogonal for angles greater than 30 deg.
        """
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

    @staticmethod
    def Diff(li1, li2):
        return list(list(set(li1) - set(li2)) + list(set(li2) - set(li1)))

    # encapsulated meshing procedure for skew and orthogonal meshing
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
                next_row_z = (node_row_z + 1) * len(self.nox)  # get next row's (z axis) nodetagcounter
                # link nodes along current row (z axis), in the x direction
                self.long_mem.append([current_row_z + node_col_x, current_row_z + node_col_x + 1,
                                      self.section_group_noz[node_row_z], eletagcounter, 1])
                eletagcounter += 1
                # link nodes in the z direction (e.g. transverse members)
                if next_row_z == nodetagcounter - 1:  # if looping last row of line mesh z
                    pass  # do nothing (exceeded the z axis edge of the grillage)
                else:  # assigning elements in transverse direction (z)
                    self.trans_mem.append([current_row_z + node_col_x, next_row_z + node_col_x,
                                           self.section_group_nox[node_col_x - 1], eletagcounter, 2])
                    # section_group_nox counts from 1 to 12, therefore -1 to start counter 0 to 11
                    eletagcounter += 1
            if next_row_z >= len(self.nox) * len(self.noz):  # check if current z coord is last row
                pass  # last column (x = self.nox[-1]) achieved, no more assignment
            else:  # assign last transverse member at last column (x = self.nox[-1])
                self.trans_mem.append([current_row_z + node_col_x + 1, next_row_z + node_col_x + 1,
                                       self.section_group_nox[node_col_x], eletagcounter, 2])
                # after counting section_group_nox 0 to 11, this line adds the counter of 12
                eletagcounter += 1
        # combine long and trans member elements to global list
        self.global_element_list = self.long_mem + self.trans_mem
        print("Element generation completed. Number of elements created = {}".format(eletagcounter - 1))
        # save elements and nodes to mesh object
        mesh_group = Mesh(self.global_element_list, self.Nodedata)
        return mesh_group

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
        self.regA = np.linspace(0, self.long_dim - self.breadth, self.num_trans_grid)
        # RegA consist of overlapping last element
        # RegB first element overlap with RegA last element
        self.regB = self.get_region_b(self.regA[-1],
                                      self.noz)  # nodes @ region B startswith last entry of region A up to
        self.nox = np.hstack(
            (self.regA[:-1], self.regB))  # combined to form nox, with last node of regA removed for repeated val
        # identify member groups based on nox and noz
        self.identify_member_groups()  # returns section_group_nox and section_group_noz
        # mesh region A quadrilateral area
        nodetagcounter = 1  # counter for nodetag, updates after creating each nodes
        eletagcounter = 1  # counter for element, updates after creating each elements
        for pointz in self.noz:  # loop for each mesh point in z dir
            for pointx in self.regA[:-1]:  # loop for each mesh point in x dir (nox)
                # populate nodedata array - inputs [nodetag,x,y,z]
                self.Nodedata.append([nodetagcounter, pointx, self.y_elevation, pointz])
                nodetagcounter += 1
        print('Number of elements in Region A: {}'.format(nodetagcounter - 1))

        # create elements of region A
        for node_row_z in range(0, len(self.noz)):
            for node_col_x in range(1, len(self.regA[:-1])):
                current_row_z = node_row_z * len(self.regA[:-1])  # current row's start node tag
                next_row_z = (node_row_z + 1) * len(  # next row's start node tag
                    self.regA[:-1])  # increment nodes after next self.noz (node grid along transverse)
                # link nodes along current row z
                self.long_mem.append([current_row_z + node_col_x, current_row_z + node_col_x + 1,
                                      self.section_group_noz[node_row_z], eletagcounter, 1])
                eletagcounter += 1
                # link nodes along current row in x dir (transverse)
                if next_row_z == nodetagcounter - 1:  # check if current z coord is last row
                    pass  # last column (x = self.nox[-1]) achieved, no more assigning transverse member

                else:
                    self.trans_mem.append([current_row_z + node_col_x, next_row_z + node_col_x,
                                           self.section_group_nox[node_col_x - 1], eletagcounter, 3])
                    eletagcounter += 1
                # last
            if next_row_z >= len(self.noz) * len(self.regA[:-1]):
                pass
            else:
                self.trans_mem.append([current_row_z + node_col_x + 1, next_row_z + node_col_x + 1,
                                       self.section_group_nox[node_col_x], eletagcounter, 3])
                # e.g. after counting section_group_nox 0 to 10, this line adds the counter of 11
                eletagcounter += 1
        print('Elements automation complete for region A: Number of elements = {}'.format(eletagcounter - 1))

        # node generation for region B
        # node generate B1 @ right support
        b1_node_tag_start = nodetagcounter - 1  # last node tag of region A
        regBupdate = self.regB  # initiate list for line mesh of region B1 - updated each loop by removing last element
        # record the section gruop counter
        reg_section_counter = node_col_x
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
        regBupdate = self.regB  # reset placeholder
        row_start = b1_node_tag_start  # last nodetag of region A
        if self.skew < 0:
            reg_a_col = row_start  # nodetag of last node in last row of region A (last nodetag of region A)
        else:  # nodetag of last node in first row of region A
            reg_a_col = len(
                self.regA[:-1])  # the last node of a single row + ignore last element of reg A (overlap regB)
        for num_z in range(0, len(self.noz)):
            # element that link nodes with those from region A
            if self.skew < 0:  # if negative skew, loop starts from the last row (@ row = width)
                self.long_mem.append([reg_a_col, row_start + 1,
                                      self.section_group_noz[(-1 - num_z)], eletagcounter, 1])
                eletagcounter += 1
            else:  # skew is positive,
                self.long_mem.append([reg_a_col, row_start + 1,
                                      self.section_group_noz[num_z], eletagcounter, 1])
                eletagcounter += 1
            # loop for each column node in x dir
            # create elements for each nodes in current row (z axis) in the x direction (list regBupdate)
            for num_x in range(1, len(regBupdate)):
                if self.skew < 0:
                    self.long_mem.append([row_start + num_x, row_start + num_x + 1,
                                          self.section_group_noz[(-1 - num_z)], eletagcounter, 1])
                    eletagcounter += 1
                else:
                    self.long_mem.append([row_start + num_x, row_start + num_x + 1,
                                          self.section_group_noz[num_z], eletagcounter, 1])
                    eletagcounter += 1
                # transverse member
                self.trans_mem.append([row_start + num_x, row_start + num_x + len(regBupdate),
                                       self.section_group_nox[num_x + reg_section_counter], eletagcounter, 3])
                eletagcounter += 1
            if num_z != len(self.noz) - 1:  # check if current row (z) is the last row of the iteration;
                # if yes,  last node of skew is single node, no element, break the loop for self.noz
                # if no, run line below, to assign the skew edges
                self.trans_mem.append([row_start + num_x + 1, row_start + num_x + len(regBupdate),
                                       self.section_group_nox[-1], eletagcounter, 2])
                eletagcounter += 1

            row_start = row_start + len(regBupdate)  # update next self.noz start node of region B
            regBupdate = regBupdate[:-1]  # remove last element for next self.noz (skew boundary)
            # check for skew angle varients of region B1 loop (positive or negative)
            if self.skew < 0:
                reg_a_col = reg_a_col - len(
                    self.regA[:-1])  # update row node number correspond with region A (decreasing)
            else:
                reg_a_col = reg_a_col + len(
                    self.regA[:-1])  # update row node number correspond with region A (increasing)
        print('Elements automation complete for region B1 and A')

        # B2 left support
        regBupdate = -self.regB + self.regA[-1]  # left side of quadrilateral area, regB can lie in negative x axis
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
            reg_a_col = 1 + (len(self.noz) - 1) * len(self.regA[:-1])  # links to first node last row of region A
        regBupdate = -self.regB + self.regA[-1]  # reset placeholder
        for num_z in range(0, len(self.noz)):
            # link nodes from region A
            if num_z == len(self.noz) - 1:  # for z = 6
                # at last row of z nodes, there exist only a single point node (typically node 1)
                # therefore, no connection of nodes to form element - end loop
                break  #
            if self.skew < 0:
                self.long_mem.append([row_start + 1, reg_a_col, self.section_group_noz[num_z], eletagcounter, 1])
                eletagcounter += 1
            else:
                self.long_mem.append([row_start + 1, reg_a_col, self.section_group_noz[(-1 - num_z)], eletagcounter, 1])
                eletagcounter += 1
            # loop for each column node in x dir
            for num_x in range(1, len(regBupdate[1:])):
                if self.skew < 0:  # negative angle
                    #
                    self.long_mem.append(
                        [row_start + num_x + 1, row_start + num_x, self.section_group_noz[num_z], eletagcounter, 1])
                    eletagcounter += 1
                else:  # positive angle
                    self.long_mem.append(
                        [row_start + num_x + 1, row_start + num_x, self.section_group_noz[(-1 - num_z)], eletagcounter,
                         1])
                    eletagcounter += 1
                # assign transverse member (orthogonal)
                self.trans_mem.append([row_start + num_x, row_start + num_x + len(regBupdate[1:]),
                                       self.section_group_nox[num_x + reg_section_counter + 1], eletagcounter, 3])
                eletagcounter += 1
                # section_group +1 due to not counting the first column (x = 0) , also by default, the size of
                # regB in B2 region is N - 1 of the size of regB in B1.
                # Therefore assignment starts from 1, not 0 (hence+1 )

            # code to assign the skew edge (edge_slab)
            if num_z == len(self.noz) - 1:  # for z = 6
                # at last row of z nodes, there exist only a single point node (typically node 1)
                # therefore, no connection of nodes to form element - end loop
                break  #
            elif num_z == len(self.noz) - 2:  # if at the second last step z = 5
                # at this step, connect last element to node of region A to form skew edge
                if self.skew < 0:  # if negative angle
                    self.trans_mem.append(
                        [reg_a_col + len(self.regA[:-1]), row_start + len(regBupdate[1:]),
                         self.section_group_nox[-1], eletagcounter, 2])  # ele of node 1 to last node skew
                    eletagcounter += 1
                else:  # else positive skew
                    self.trans_mem.append(
                        [1, row_start + len(regBupdate[1:]), self.section_group_nox[-1],
                         eletagcounter, 2])  # ele of node 1 to last node skew
                    eletagcounter += 1
            elif num_z != len(self.noz) - 1:  # check if its not the last step
                # assign trasnverse members of region B2
                self.trans_mem.append(
                    [row_start + num_x + 1, row_start + num_x + len(regBupdate[1:]), self.section_group_nox[-1]
                        , eletagcounter, 2])  # support skew
                eletagcounter += 1
            # steps in transverse mesh, assign nodes of skew nodes

            row_start = row_start + len(regBupdate[1:])  # update next self.noz start node
            regBupdate = regBupdate[:-1]  # remove last element for next self.noz (skew boundary)

            if self.skew < 0:
                reg_a_col = reg_a_col + len(self.regA[:-1])  # update next self.noz node correspond with region A
            else:
                reg_a_col = reg_a_col - len(self.regA[:-1])  # update next self.noz node correspond with region A
        print('Elements automation complete for region B1 B2 and A')
        self.global_element_list = self.long_mem + self.trans_mem
        # save elements and nodes to mesh object
        mesh_group = Mesh(self.global_element_list,self.Nodedata)
        return mesh_group

    def set_material(self, material_obj):
        """
        Function to define material for Openseespy material model. For example, uniaxialMaterial, nDMaterial.


        :return: Function populates object variables: (1) mat_matrix, and (2) mat_type_op.
        """
        self.global_mat_object = material_obj  # material matrix for

        # write Opensees material() command
        self.op_uniaxial_material()

    # test output file
    def run_check(self):
        """
        Unit test for code, invoke the output py file to check execution
        :return:
        """
        try:
            __import__(self.filename[:-3])  # run file
            print("File imported and run, OK")
        except:
            print("File error not executable")

    def add_nodal_load_analysis(self, point, load_value, direction="y"):
        """
        Function to add point load analysis to output file.
        :return: at the end of output file, add lines to create timeSeries, pattern, load, integrator
        """
        if point > len(self.Nodedata):
            Exception("Loading point for load analysis is not valid - out of bounds of node numbers")
        with open(self.filename, 'a') as file_handle:
            # write header
            file_handle.write("#===========================\n# run simply load analysis\n#==========================\n")
            # write generation of time series and pattern, set default as 1
            file_handle.write("ops.timeSeries('Linear', 1)\n")
            file_handle.write("ops.pattern('Plain', 1, 1)\n")
            # add load() command
            if direction == "y":
                file_handle.write("ops.load({pt}, 0.0, {val}, 0.0, 0, 0, 0)\n"
                                  .format(pt=point if point is float or int else 20, val=load_value))
            elif direction == "x":
                file_handle.write("ops.load({pt}, {val}, 0.0, 0.0, 0, 0, 0)\n"
                                  .format(pt=point if point is float or int else 20, val=load_value))
            elif direction == "z":
                file_handle.write("ops.load({pt}, 0.0, 0.0, {val}, 0, 0, 0)\n"
                                  .format(pt=point if point is float or int else 20, val=load_value))
            else:  # For moments
                file_handle.write("ops.load({pt}, 0.0, 0.0, 0.0, 0, 0, 0)\n"
                                  .format(pt=point if point is float or int else 20, val=load_value))

            # Add command for analaysis
            file_handle.write("ops.integrator('LoadControl', 1)\n")  # Header
            file_handle.write("ops.numberer('Plain')\n")
            file_handle.write("ops.system('BandGeneral')\n")
            file_handle.write("ops.constraints('Plain')\n")
            file_handle.write("ops.algorithm('Linear')\n")
            file_handle.write("ops.analysis('Static')\n")
            file_handle.write("ops.analyze(1)")


# ----------------------------------------------------------------------------------------------------------------
# Classes for components of opGrillage object
# ----------------------------------------------------------------------------------------------------------------
class Material:
    """
    Class for material properties definition
    """

    def __init__(self, mat_type, mat_vec):
        # super(UniAxialElasticMaterial, self).__init__(length, length)
        self.mat_type = mat_type
        self.mat_vec = mat_vec

        pass


class UniAxialElasticMaterial(Material):
    """
    Class for uniaxial material prop
    """

    def __init__(self, mat_type, mat_vec):
        # super(UniAxialElasticMaterial, self).__init__(length, length)
        super().__init__(mat_type, mat_vec)
        self.mat_type = mat_type
        self.mat_vec = mat_vec


class Mesh:
    """
    Class for mesh groups. The class holds information pertaining the mesh group such as element connectivity and nodes
    of the mesh object.


    """
    def __init__(self, ele_group, node_list):
        self.ele_group = ele_group
        self.node_list = node_list


# ----------------------------------------------------------------------------------------------------------------
class Section:
    def __init__(self, E, A, Iz, J, Ay, Az, Iy=None, G=None, alpha_y=None, op_ele_type=None,
                 unit_width=False, op_section_type=None):
        """

        :param E: Elastic modulus
        :type E: float or int
        :param A: Cross sectional area
        :type A: float or int
        :param Iz: Moment of inertia about z axis
        :type Iz: float or int
        :param J: Torsional inertia
        :param Ay:
        :param Az:
        :param Iy:Moment of inertia about z axis
        :type Iy: float or int
        :param G: Shear modulus
        :param alpha_y:
        :param op_ele_type:
        :param unit_width:

        # example
        # .section('Elastic', BeamSecTag,Ec,ABeam,IzBeam)
        """
        # sections
        self.op_section_type = op_section_type  # section tag based on Openseespy
        self.section_command_flag = False  # default False
        # section geometry properties variables
        self.E = E
        self.A = A
        self.Iz = Iz
        self.Iy = Iy
        self.G = G
        self.Ay = Ay
        self.Az = Az
        self.J = J
        self.alpha_y = alpha_y
        # types for element definition and unit width properties
        self.op_ele_type = op_ele_type
        self.unit_width = unit_width

        # check if section command is needed for the section object
        if self.op_section_type is not None:
            self.section_command_flag = True  # section_command_flag set to True.

    def output_arguments_unit_width(self, width=1):
        """
        Function to output list argument according to element() command of variety of element tags
        in Opensees - for unit width properties assignment
        :return: list containing member properties in accordance with Openseespy input convention
        """
        section_input = None
        # assignment input based on ele type
        if self.op_ele_type == "ElasticTimoshenkoBeam":
            section_input = [self.E, self.G, self.A, self.J, self.Iy, self.Iz, self.Ay, self.Az]
            section_input = "[{:.3e}, {:.3e}, {:.3e}, {:.3e}, {:.3e}, {:.3e}, {:.3e}, {:.3e}]".format(self.E,
                                                                                                      self.G,
                                                                                                      self.A,
                                                                                                      self.J,
                                                                                                      self.Iy * width,
                                                                                                      self.Iz * width,
                                                                                                      self.Ay * width,
                                                                                                      self.Az * width)
        elif self.op_ele_type == "elasticBeamColumn":  # eleColumn
            section_input = [self.E, self.G, self.A, self.J, self.Iy, self.Iz]
            section_input = "[{:.3e}, {:.3e}, {:.3e}, {:.3e}, {:.3e}, {:.3e}]".format(self.E, self.G, self.A * width,
                                                                                      self.J, self.Iy * width,
                                                                                      self.Iz * width)

        # procedure to check if element() command requires preceding section() command
        if self.op_section_type == "Elastic":
            # check if section is Elastic, return argument list correspond to section Elastic
            pass
        elif self.op_section_type == "RC Section":
            # if section is RC section, return argument list correspond to section RC section
            pass

        return section_input


# ----------------------------------------------------------------------------------------------------------------
class GrillageMember:
    """
    Class of grillage member. A GrillageMember object has a section, material object.
    """

    def __init__(self, section, material, name="Undefined"):
        """

        :param section: Section class object assigned to GrillageMember
        :param material: Material class object assigned to GrillageMember
        :param name: Name of the grillage member (Optional)
        """
        self.name = name
        self.section = section
        self.material = material


# ----------------------------------------------------------------------------------------------------------------
# Loading classes and load cases
# ---------------------------------------------------------------------------------------------------------------
class Loading:
    def __init__(self, load_type, load_value, direction="y"):
        pass


class LineLoading(Loading):
    def __init__(self):
        super().__init__()


class PatchLoading(Loading):
    def __init__(self):
        super().__init__()


class LoadCase:
    def __init__(self, Load):
        pass
