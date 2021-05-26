import numpy as np
import math
import openseespy.opensees as ops
from datetime import datetime
from collections import defaultdict
from static import *
from Load import *
from Material import *
from member_sections import *
from Mesh import *


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
        self.skew = skew  # angle in degrees

        # Variables for grillage grillage
        self.num_long_gird = num_long_grid  # number of longitudinal beams
        self.num_trans_grid = num_trans_grid  # number of grids for transverse members
        self.edge_width = edge_beam_dist  # width of cantilever edge beam
        self.regA = []
        self.regB = []
        self.edge_beam_nodes = []
        # instantiate matrices for geometric dependent properties
        self.trans_dim = None  # to be calculated automatically based on skew
        self.breadth = None  # to be calculated automatically based on skew
        self.spclonggirder = None  # to be automated
        self.spctransslab = None  # to be automated

        # initialize lists
        self.node_map = []  # array like to be populated
        self.nox = []  # line mesh in x direction
        self.noz = []  # line mesh in z direction
        # initiate list of various elements of grillage model, each entry of list is a sublist [node_i, node_j, eletag]
        self.long_mem = []  # longitudinal members
        self.trans_mem = []  # transverse members
        self.support_nodes = []  # list of nodes at support regions
        self.vxz_skew = []  # vector xz of skew elements - for section transformation
        self.global_mat_object = []  # material matrix
        self.noz_trib_width = []
        self.nox_trib_width = []
        # initialize tags of grillage elements - default tags are for standard elements of grillage
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
        self.nox_special = None  # array specifying custom coordinate of longitudinal nodes
        self.noz_special = None  # array specifying custom coordinate of transverse nodes
        self.skew_threshold = [10, 30]  # threshold for grillage to allow option of mesh choices
        self.deci_tol = 4  # tol of decimal places

        # dict for load cases and load types
        self.load_case_dict = defaultdict(lambda: 1)
        self.nodal_load_dict = defaultdict(lambda: 1)
        self.ele_load_dict = defaultdict(lambda: 1)

        # counters to keep track of objects
        self.load_case_counter = 1
        self.load_combination_counter = 1

        # Initiate py file output
        self.filename = "{}_op.py".format(self.model_name)

        # calculate edge length of grillage
        self.trans_dim = self.width / math.cos(self.skew / 180 * math.pi)
        # 1 create Opensees model space

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

        else:
            pass
        self.__write_op_model()
        self.__run_mesh_generation()

    def __run_mesh_generation(self):
        # function to run mesh generation
        self.Mesh_obj = Mesh(self.long_dim, self.width, self.trans_dim, self.edge_width, self.num_trans_grid,
                             self.num_long_gird,
                             self.skew, skew_2=self.skew, orthogonal=self.ortho_mesh)

        # 2 generate command lines in output py file
        self.__write_op_node(self.Mesh_obj)  # write node() commands
        self.__write_op_fix(self.Mesh_obj)  # write fix() command for support nodes
        self.__write_geom_transf(self.Mesh_obj)  # x dir members
        # 3 identify boundary of mesh
        # TODO hereafter modify to read properties from Mesh.obj

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
        :param trans_tag: tag of transformation - set according to default 1, 2 and 3
        :param vector_xz: vector parallel to plane xz of the element. Automatically calculated by get_vector_xz()
        :param transform_type: transformation type
        :type transform_type: str

        :return: Writes ops.geomTransf() line to output py file
        """

        # write geoTransf() command
        # ops.geomTransf(transform_type, trans_tag, *vector_xz)
        # with open(self.filename, 'a') as file_handle:
        #     file_handle.write("# create transformation {}\n".format(trans_tag))
        #     file_handle.write("ops.geomTransf(\"{type}\", {tag}, *{vxz})\n".format(
        #         type=transform_type, tag=trans_tag, vxz=vector_xz))

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
            else:
                ops.node(nested_v['tag'], coordinate[0], coordinate[1], coordinate[2])

    def __write_op_fix(self, mesh_obj):
        """
        Abstracted procedure handed by create_nodes() function. This method writes the fix() command for
        boundary condition defintion in the grillage model.

        :return: Output py file populated with fix() command for boundary condition definition.
        """
        if self.pyfile:
            with open(self.filename, 'a') as file_handle:
                file_handle.write("# Boundary condition implementation\n")
            # TODO generalize for user input of boundary condition
        for k, v, in mesh_obj.edge_node_recorder.items():
            # if edge beam - common group z ==0 - do not assign
            if mesh_obj.node_spec[k]["z_group"] in mesh_obj.common_z_group_element[0]:
                pass
            elif v == 0:
                if self.pyfile:
                    with open(self.filename, 'a') as file_handle:
                        file_handle.write("ops.fix({}, *{})\n".format(k, self.fix_val_pin))
                else:
                    ops.fix(k, *self.fix_val_pin)
            elif v == 1:
                if self.pyfile:
                    with open(self.filename, 'a') as file_handle:
                        file_handle.write("ops.fix({}, *{})\n".format(k, self.fix_val_roller_x))
                else:
                    ops.fix(k, *self.fix_val_roller_x)

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

    # def __identify_member_groups(self):
    #     """
    #     Abstracted method handled by either orthogonal_mesh() or skew_mesh() function
    #     to identify member groups based on node spacings in orthogonal directions.
    #
    #     :return: Set variable `group_ele_dict` according to
    #     """
    #     # identify element groups in grillage based on line mesh vectors self.nox and self.noz
    #
    #     # get the grouping properties of nox
    #     # grouping number, dictionary of unique groups, dict of spacing values for given group as key, list of trib
    #     # area of nodes
    #     self.section_group_noz, self.spacing_diff_noz, self.spacing_val_noz, self.noz_trib_width \
    #         = characterize_node_diff(self.noz, self.deci_tol)
    #     self.section_group_nox, self.spacing_diff_nox, self.spacing_val_nox, self.nox_trib_width \
    #         = characterize_node_diff(self.nox, self.deci_tol)
    #     # update self.section_group_nox counter to continue after self.section_group_noz
    #     self.section_group_nox = [x + max(self.section_group_noz) for x in self.section_group_nox]
    #
    #     if self.ortho_mesh:
    #         # update self.section_group_nox first element to match counting for element group of Region B
    #         self.section_group_nox[0] = self.section_group_nox[len(self.regA) - 1]
    #     else:  # else skew mesh do nothing
    #         pass
    #     # set groups dictionary
    #     if self.ortho_mesh:  # if ortho mesh
    #         if max(self.section_group_noz) <= 4:  # if true , standard sections set for longitudinal members
    #             self.group_ele_dict = {"edge_beam": 1, "exterior_main_beam_1": 2, "interior_main_beam": 3,
    #                                    "exterior_main_beam_2": 4, "edge_slab": 5, "transverse_slab": 6}
    #         else:  # groups
    #             self.group_ele_dict = {"edge_beam": 1, "exterior_main_beam_1": 2, "interior_main_beam": 3,
    #                                    "exterior_main_beam_2": 4, "edge_slab": 5, "transverse_slab": 6}
    #     else:  # skew mesh, run generate respective group dictionary
    #         if max(self.section_group_noz) <= 4:
    #             # dictionary applies to longitudinal members only
    #             self.group_ele_dict = {"edge_beam": 1, "exterior_main_beam_1": 2, "interior_main_beam": 3,
    #                                    "exterior_main_beam_2": 4, "edge_slab": 5, "transverse_slab": 6}
    #         else:  # section grouping greater than 6
    #
    #             # set variable up to 4 group (longitudinal)
    #             self.group_ele_dict = {"edge_beam": 1, "exterior_main_beam_1": 2, "interior_main_beam": 3,
    #                                    "exterior_main_beam_2": 4}
    #             # for transverse (group 5 and above) assign based on custom number
    #
    #         # orthogonal mesh rules
    #     # print groups to terminal
    #     print("Total groups of elements in longitudinal : {}".format(max(self.section_group_noz)))
    #     print("Total groups of elements in transverse : {}".format(max(self.section_group_nox)))

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

    def __get_vector_xz(self):
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
        x = self.width
        y = -(-self.breadth)
        # normalize vector
        length = math.sqrt(x ** 2 + y ** 2)
        vec = [x / length, y / length]
        return vec

    def __get_region_b(self, reg_a_end, noz):
        """
        Abstracted procedure to define the varying spacing nodes in orthogonal mesh (near support edges). This
        method is called within orthogonal_mesh() or skew_mesh.

        :return: list of nodes within the skew edge regions

        """
        # Function to calculate the node coordinate for skew region B
        # -> triangular breadth along the longitudinal direction
        # :param step: list containing transverse nodes (along z dir)
        # :param reg_a_end: last node from regA (quadrilateral region)
        # :return: node coordinate for skew triangular area (region B1 or B2)

        regB = [reg_a_end]  # initiate array regB
        for node in range(2, len(noz)):  # minus 2 to ignore first and last element of step
            regB.append(self.long_dim - noz[-node] * np.abs(np.tan(self.skew / 180 * math.pi)))
        # after append, add last element - self.long_dim
        regB.append(self.long_dim)
        regB = np.array(regB)
        return regB

    def __check_skew(self):
        """
        Function to set boolean to true if orthogonal mesh option. This function is automatically called during __init__
        Function also checks if skew angle lies in allowable threshold
        - between 10-30 degree (var self.skew_threshold) both types of mesh (skew and orthogonal) are allowed.
        outside this bound, skew rules are strictly: (1) skew for angles less than 10 deg, and
        (2) orthogonal for angles greater than 30 deg.
        """

        # if mesh type is beyond default allowance threshold of 11 degree and 30 degree, return exception
        if np.abs(self.skew) <= self.skew_threshold[0] and self.ortho_mesh:
            # print
            raise Exception('Orthogonal mesh not allowed for angle less than {}'.format(self.skew_threshold[0]))
        elif np.abs(self.skew) >= self.skew_threshold[1] and not self.ortho_mesh:
            raise Exception('Oblique mesh not allowed for angle greater than {}'.format(self.skew_threshold[1]))

    def set_member(self, grillage_member_obj, member=None):
        # if write flag, write header of element assignment
        if self.pyfile:
            with open(self.filename, 'a') as file_handle:
                file_handle.write("# Element generation for section: {}\n".format(member))

        common_member_tag = []
        if member == "interior_main_beam":
            common_member_tag = 2
        elif member == "exterior_main_beam_1":
            common_member_tag = 1
        elif member == "exterior_main_beam_2":
            common_member_tag = 3
        elif member == "edge_beam":
            common_member_tag = 0
        else:
            common_member_tag = None

        ele_width = 1
        # if member is transverse, assign slab elements
        if grillage_member_obj.section.unit_width and common_member_tag is None:
            for ele in self.Mesh_obj.trans_ele:
                tag = ele[0]
                # get node_i and node_j spacing
                lis = self.Mesh_obj.node_width_x_dict[tag]
                ele_width = 1
                if len(lis) == 1:
                    ele_width = np.sqrt(lis[0][0] ** 2 + lis[0][1] ** 2 + lis[0][2] ** 2) / 2
                elif len(lis) == 2:
                    ele_width = (np.sqrt(lis[0][0] ** 2 + lis[0][1] ** 2 + lis[0][2] ** 2) +
                                 np.sqrt(lis[1][0] ** 2 + lis[1][1] ** 2 + lis[1][2] ** 2)) / 2

                ele_str = grillage_member_obj.section.get_element_command_str(
                    ele_tag=ele[0], n1=ele[1], n2=ele[2], transf_tag=ele[4], ele_width=ele_width)
                if self.pyfile:
                    with open(self.filename, 'a') as file_handle:
                        file_handle.write(ele_str)
                else:
                    eval(ele_str)
        else:
            # loop each element z group assigned under common_member_tag
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

    def add_load_case(self, name, *load_obj, analysis_type='Static'):
        """
        Functions to add loads or load cases
        :param name:
        :param load_obj:
        :param analysis_type:
        :return:
        """

        with open(self.filename, 'a') as file_handle:
            # if no load cases have been defined previously, create time series object for the first time
            if not bool(self.load_case_dict):
                time_series = "ops.timeSeries('Constant', 1)\n"
                file_handle.write(time_series)
                eval(time_series)
                load_case_counter = 0  # if dict empty, start counter at 1
            else:  # set load_case_counter variable as the latest
                load_case_counter = self.load_case_dict[list(self.load_case_dict)[-1]]
                wipe_command = "ops.wipeAnalysis()\n"
                file_handle.write(wipe_command)  # write wipeAnalysis for current load case
                eval(wipe_command)

            # set load case to load_case_dict
            load_case_tag = self.load_case_dict.setdefault(name, load_case_counter + 1)
            # write header
            file_handle.write("#===========================\n# create load case {}\n#==========================\n"
                              .format(name))
            # create pattern obj for load case
            pattern_command = "ops.pattern('Plain', {}, 1)\n".format(load_case_tag)
            file_handle.write(pattern_command)
            eval(pattern_command)
            # print to terminal
            print("Load Case {} created".format(name))
            # loop through each load object
            for loads in load_obj:
                if isinstance(loads, NodalLoad):
                    load_str = loads.get_nodal_load_str()
                    for lines in load_str:
                        file_handle.write(lines)
                    # print to terminal
                    print("Nodal load - {loadname} - added to load case: {loadcase}".format(loadname=loads.name,
                                                                                            loadcase=name))
                elif isinstance(loads, PointLoad):
                    nod = self.__return_four_node_position(position=loads.position)
                    print(nod)

                elif isinstance(loads, LineLoading):
                    load_str = self.__assign_line_load(line_position_x=2, udl_value=2)
                    for lines in load_str:
                        file_handle.write(lines)
                    print("Line load - {loadname} - added to load case: {name}".format(loadname=loads.name, name=name))

                elif isinstance(loads, PatchLoading):
                    if loads.patch_define_option == "two-lines":
                        load_str = self.__assign_patch_load_bound_option(bound_lines=loads.northing_lines,
                                                                         area_load=loads.qy)
                    elif loads.patch_define_option == "four-points":
                        # TODO
                        pass

                    for lines in load_str:
                        file_handle.write(lines)
                    print("Patch load - {loadname} - added to load case: {name}".format(loadname=loads.name, name=name))
                else:
                    print("No loads assigned for {}".format(loads))

            # Create instance and write command to output py file
            file_handle.write("ops.integrator('LoadControl', 1)\n")  # Header
            file_handle.write("ops.numberer('Plain')\n")
            file_handle.write("ops.system('BandGeneral')\n")
            file_handle.write("ops.constraints('Plain')\n")
            file_handle.write("ops.algorithm('Linear')\n")
            file_handle.write("ops.analysis(\"{}\")\n".format(analysis_type))
            file_handle.write("ops.analyze(1)\n")

    # ---------------------------------------------------------------
    # assignment procedure
    def get_nodes_given_point(self, point):
        x = point[0]
        y = point[1]
        z = point[2]
        node_distance = []
        # find node closest to point
        for tag, subdict in self.Mesh_obj.node_spec.items():
            node = subdict['coordinate']
            dis = np.sqrt((node[0] - x) ** 2 + 0 + (node[2] - z) ** 2)
            node_distance.append([tag, dis])
        node_distance.sort(key=lambda x: x[1])
        closest = node_distance[0]
        if closest[0] < x and closest[2] < z:
            pass

        pass

    # TO be retired
    def __return_four_node_position(self, position):
        # function to identify the position of point load/axle
        # position [x,z]
        # find grid lines that bound position in x direction
        grid_a_z, grid_b_z = search_grid_lines(self.noz, position=position[1])
        # return nodes in the bounded grid lines grid_a_z and grid_b_z
        grid_b_z_nodes = [x for x in self.node_map if x[4] == grid_a_z]
        grid_a_z_nodes = [x for x in self.node_map if x[4] == grid_b_z]
        # loop each grid nodes to find the two closest nodes in the x direction (vector distance)
        node_distance = []
        for node in grid_b_z_nodes:
            dis = np.sqrt((node[1] - position[0]) ** 2 + 0 + (node[3] - position[1]) ** 2)
            node_distance.append([node[0], dis])
        for node in grid_a_z_nodes:
            dis = np.sqrt((node[1] - position[0]) ** 2 + 0 + (node[3] - position[1]) ** 2)
            node_distance.append([node[0], dis])
        node_distance.sort(key=lambda x: x[1])
        n1 = node_distance[0]
        n2 = node_distance[1]
        n3 = node_distance[2]
        n4 = node_distance[3]
        return [x[0] for x in [n1, n2, n3, n4]]

    # TO be retired
    def __assign_line_load(self, line_position_x, udl_value):
        line = search_grid_lines(self.noz, position=line_position_x)
        load_str = []
        for ele in self.long_mem:
            if ele[5] == line[1][0]:
                eleLoad_line = "ops.eleLoad('-ele', {eleTag}, '-type', '-beamUniform', {Wy}, {Wz}, {Wx})\n" \
                    .format(eleTag=ele[3], Wy=0, Wx=0, Wz=0)
            elif ele[5] == line[0][0]:
                eleLoad_line = "ops.eleLoad('-ele', {eleTag}, '-type', '-beamUniform', {Wy}, {Wz}, {Wx})\n" \
                    .format(eleTag=ele[3], Wy=0, Wx=0, Wz=0)
            else:
                eleLoad_line = ''
            load_str.append(eleLoad_line)
        return load_str

    # TO be retired
    def __assign_patch_load_bound_option(self, bound_lines, area_load):
        if bound_lines[0] > bound_lines[1]:
            ub_nd_line = search_grid_lines(self.noz, position=bound_lines[0], position_bound="ub")
            lb_nd_line = search_grid_lines(self.noz, position=bound_lines[1], position_bound="lb")
        else:
            lb_nd_line = search_grid_lines(self.noz, position=bound_lines[0], position_bound="lb")
            ub_nd_line = search_grid_lines(self.noz, position=bound_lines[1], position_bound="ub")
        load_str = []
        # if lower bound = upper bound, no in between lines, only assign to the single line identified by
        # lower_bound_nd_line/upper_bound_nd_line
        # if ub_nd_line and lb_nd_line are identical, patch load area too small for definition of patch load
        if lb_nd_line[0][0] == ub_nd_line[0][0] and lb_nd_line[1][0] == ub_nd_line[1][0]:
            # print warning to Terminal
            print('Northing bounds too small for definition of patch loads - consider line load instead ')

        # if bounded line is common, set load to
        elif lb_nd_line[0] == ub_nd_line[1]:
            in_between_nd_line = [lb_nd_line[0][0]]
            lb_nd_line[0] = [[], 0]
            ub_nd_line[1] = [[], 0]
        elif lb_nd_line[0][0] + 1 == ub_nd_line[1][0]:
            in_between_nd_line = []
        else:
            in_between_nd_line = [lb_nd_line[0][0] + 1]
            while not in_between_nd_line[-1] + 1 > ub_nd_line[1][0]:
                in_between_nd_line.append(in_between_nd_line[-1] + 1)

        # loop all between node lines, assign udl using full width of node tributary area
        for nd_line in in_between_nd_line:
            nd_wid = self.noz_trib_width[nd_line]
            udl_line = area_load * nd_wid
            for ele in self.long_mem:
                # if element is part of the grid line, assign UDl using eleLoad command
                if ele[5] == nd_line:
                    eleLoad_line = "ops.eleLoad('-ele', {eleTag}, '-type', '-beamUniform', {Wy}, {Wz}, {Wx})\n" \
                        .format(eleTag=ele[3], Wy=udl_line, Wx=0, Wz=0)
                    load_str.append(eleLoad_line)
        # assign ub and lb udl
        for ele in self.long_mem:
            if ele[5] == lb_nd_line[1][0]:
                eleLoad_line = "ops.eleLoad('-ele', {eleTag}, '-type', '-beamUniform', {Wy}, {Wz}, {Wx})\n" \
                    .format(eleTag=ele[3], Wy=area_load * lb_nd_line[1][1], Wx=0, Wz=0)
            elif ele[5] == lb_nd_line[0][0]:
                eleLoad_line = "ops.eleLoad('-ele', {eleTag}, '-type', '-beamUniform', {Wy}, {Wz}, {Wx})\n" \
                    .format(eleTag=ele[3], Wy=area_load * lb_nd_line[0][1], Wx=0, Wz=0)
            elif ele[5] == ub_nd_line[1][0]:
                eleLoad_line = "ops.eleLoad('-ele', {eleTag}, '-type', '-beamUniform', {Wy}, {Wz}, {Wx})\n" \
                    .format(eleTag=ele[3], Wy=area_load * ub_nd_line[1][1], Wx=0, Wz=0)
            elif ele[5] == ub_nd_line[0][0]:
                eleLoad_line = "ops.eleLoad('-ele', {eleTag}, '-type', '-beamUniform', {Wy}, {Wz}, {Wx})\n" \
                    .format(eleTag=ele[3], Wy=area_load * ub_nd_line[0][1], Wx=0, Wz=0)
            else:
                eleLoad_line = ""
            load_str.append(eleLoad_line)

        return load_str
