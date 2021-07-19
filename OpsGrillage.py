import math
from datetime import datetime
from itertools import combinations
import openseespy.postprocessing.Get_Rendering as opsplt
import matplotlib.pyplot as plt
import openseespy.postprocessing.ops_vis as opsv
import openseespy.opensees as ops

from Load import *
from Mesh import *
from Material import *
from member_sections import *
import xarray as xr


class OpsGrillage:
    """
    Main class of Openseespy grillage model wrapper. Outputs an executable py file which generates the prescribed
    Opensees grillage model based on user input.

    The class provides an interface for the user to specify the geometry of the grillage model. A keyword argument
    allows for users to select between skew/oblique or orthogonal mesh. Methods in this class allows users to input
    properties for various elements in the grillage model.

    """

    def __init__(self, bridge_name, long_dim, width, skew, num_long_grid,
                 num_trans_grid: float, edge_beam_dist, mesh_type="Ortho", model="3D", **kwargs):
        """
        :param bridge_name: Name of bridge model and output .py file
        :type bridge_name: str
        :param long_dim: Length of the model in the longitudinal direction (default: x axis)
        :type long_dim: int or float
        :param width: Width of the model in the transverse direction (default: z axis)
        :type width: int or float
        :param skew: Skew angle of the start and end edges of model
        :type skew: int or float
        :param num_long_grid: Number of grid lines in longitudinal direction
        :type num_long_grid: int
        :param num_trans_grid: Number of  grid lines in the transverse direction
        :type num_trans_grid: int
        :param edge_beam_dist: Distance of edge beam node lines to exterior main beam node lines
        :type edge_beam_dist: int or float
        :param mesh_type: Type of mesh either "Ortho" for orthogonal mesh or "Oblique" for oblique mesh
        :type mesh_type: string

        """

        self.global_load_str = []
        self.global_patch_int_dict = dict()
        self.mesh_type = mesh_type
        self.model_name = bridge_name
        self.long_dim = long_dim  # span , also c/c between support bearings
        self.width = width  # length of the bearing support - if skew  = 0 , this corresponds to width of bridge

        # parse edge skew angle, check if skew is a list containing 2 skew angles,
        # set start and end edge of span to have respective angles
        if isinstance(skew, list):
            self.skew_a = skew[0]
            if len(skew) >= 2:
                self.skew_b = skew[1]
        else:  # set skew_a and skew_b variables to equal
            self.skew_a = skew  # angle in degrees
            self.skew_b = skew  # angle in degrees
        if any([np.abs(self.skew_a)>90,np.abs(self.skew_b)>90]):
            raise ValueError("Skew angle either start or end edge exceeds 90 degrees. Allowable range is -90 to 90")
        # next check if arctan (L/w)

        self.num_long_gird = num_long_grid  # number of longitudinal beams
        self.num_trans_grid = num_trans_grid  # number of grids for transverse members
        self.edge_width = edge_beam_dist  # width of cantilever edge beam
        # instantiate matrices for geometric dependent properties
        self.trans_dim = None  # to be calculated automatically based on skew
        self.global_mat_object = []  # material matrix
        self.global_line_int_dict = []
        # list of components with tags
        self.element_command_list = []  # list of str for ops.element() commands
        self.section_command_list = []  # list of str for ops.section() commands
        self.material_command_list = []
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

        # dict for load cases and load types
        self.load_case_list = []  # list of dict, example [{'loadcase':LoadCase object, 'load_command': list of str}..]
        self.load_combination_dict = dict()  # example {0:[{'loadcase':LoadCase object, 'load_command': list of str},
        # {'loadcase':LoadCase object, 'load_command': list of str}....]}
        self.moving_load_case_dict = dict()  # example [ list of load_case_dict]\
        # counters to keep track of ops time series and ops pattern objects for loading
        self.global_time_series_counter = 1
        self.global_pattern_counter = 1

        # set pyfile name
        self.filename = "{}_op.py".format(self.model_name)
        # create namedtuples

        # calculate edge length of grillage
        self.trans_dim = self.width / math.cos(self.skew_a / 180 * math.pi)

        # Mesh objects and pyfile flag
        self.pyfile = None
        self.results = None

        # kwargs for rigid link modelling option
        self.rigid_type = kwargs.get("rigid_1",None)
        # TODO feature for rigid link + offset beam elements to added after release

        # create mesh object
        self.Mesh_obj = Mesh(self.long_dim, self.width, self.trans_dim, self.edge_width, self.num_trans_grid,
                             self.num_long_gird,
                             self.skew_a, skew_2=self.skew_b, orthogonal=self.ortho_mesh)

    def create_ops(self, pyfile=False):
        """
        Function to create model instance in Opensees model space. If pyfile input is True, function creates an
        executable pyfile for generating the grillage model in Opensees model space.
        :param pyfile: Boolean to flag py file generation or Opensees model instance.
        :type pyfile: bool

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
        # create element commands of grillage model
        for ele_dict in self.element_command_list:
            for ele_list in ele_dict.values():
                for ele_str in ele_list:
                    if self.pyfile:
                        with open(self.filename, 'a') as file_handle:
                            file_handle.write(ele_str)
                    else:
                        eval(ele_str)

        # create the result file for the Mesh object
        self.results = Results(self.Mesh_obj)

    # function to run mesh generation
    def __run_mesh_generation(self):

        # 2 generate command lines in output py file
        self.__write_op_node(self.Mesh_obj)  # write node() commands
        self.__write_op_fix(self.Mesh_obj)  # write fix() command for support nodes
        self.__write_geom_transf(self.Mesh_obj)  # x dir members
        # 3 identify boundary of mesh
        for mat_str in self.material_command_list:
            if self.pyfile:
                with open(self.filename, 'a') as file_handle:
                    file_handle.write("# Material definition \n")
                    file_handle.write(mat_str)
            else:
                eval(mat_str)
        for sec_str in self.section_command_list:
            if self.pyfile:
                with open(self.filename, 'a') as file_handle:
                    file_handle.write("# Create section: \n")
                    file_handle.write(
                        sec_str)
            else:
                eval(sec_str)


    def set_boundary_condition(self, edge_group_counter=[1], restraint_vector=[0, 1, 0, 0, 0, 0], group_to_exclude=[0]):
        """
        Function for user to modify boundary conditions of the grillage model. Edge nodes are automatically detected
        and recorded as having fixity in vertical y direction.

        .. note::
            Development yet to be completed - will progress once user input received
        """
        pass

    # abstracted procedures to write ops commands to output py file. All functions are private and named with "__write"
    def __write_geom_transf(self, mesh_obj, transform_type="Linear"):
        """
        Abstracted procedure to write ops.geomTransf() to output py file.
        :param transform_type: transformation type
        :type transform_type: str

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
        Sub-abstracted procedure handled by create_nodes() function. This function instantiates the Opensees model
        space. If pyfile flagged as True, this function writes the instantiating commands e.g. ops.model() to the
        output py file.

        .. note:
            For 3-D model, the default model dimension and node degree-of-freedoms are 3 and 6 respectively.
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
        Sub-abstracted procedure handled by create_nodes() function. This function execute the ops.node command to
        create model in Opensees model space. If pyfile is flagged true, writes the ops.nodes() command to py file
        instead.

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
            else:  # indices correspondance . 0 - x , 1 - y, 2 - z
                ops.node(nested_v['tag'], coordinate[0], coordinate[1], coordinate[2])

    def __write_op_fix(self, mesh_obj):
        """
        Abstracted procedure handed by create_nodes() function. This method writes the ops.fix() command for
        boundary condition definition in the grillage model. If pyfile is flagged true, writes
        the ops.fix() command to py file instead.

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

    def __write_uniaxial_material(self, member: GrillageMember = None,
                                  material: Union[UniAxialElasticMaterial, NDmaterial] = None):
        """
        Sub-abstracted procedure to write uniaxialMaterial command for the material properties of the grillage model.

        :return: Output py file with uniaxialMaterial() command
        """
        # function to generate uniaxialMaterial() command in output py file
        # ops.uniaxialMaterial(self.mat_type_op, 1, *self.mat_matrix)
        material_obj = None
        if member is None and material is None:
            raise Exception("Uniaxial material has no input GrillageMember or Material Object")
        if member is None:
            material_obj = material  # str of section type - Openseespy convention

        elif material is None:
            material_obj = member.material  # str of section type - Openseespy convention

        material_type, op_mat_arg = material_obj.get_uni_material_arg_str()

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
            mat_str = material_obj.get_uni_mat_ops_commands(material_tag=material_tag)
            self.material_command_list.append(mat_str)
            # if self.pyfile:
            #     with open(self.filename, 'a') as file_handle:
            #         file_handle.write("# Material definition \n")
            #         file_handle.write(mat_str)
            # else:
            #     eval(mat_str)
        else:
            print("Material {} with tag {} has been previously defined"
                  .format(material_type, material_tag))
            return material_tag

    def __write_section(self, grillage_member_obj: GrillageMember):
        """
        Abstracted procedure handled by set_member() function to write section() command for the elements. This method
        is ran only when GrillageMember object requires section() definition following convention of Openseespy.

        """
        # extract section variables from Section class
        section_obj = grillage_member_obj.section
        section_type, section_arg = section_obj.get_section_arg_str()
        # list of argument for section - Openseespy convention
        section_str = [section_type, section_arg]  # repr both variables as a list for keyword definition
        # if section is specified, get the sectiontagcounter for section assignment
        if not bool(self.section_dict):
            lastsectioncounter = 0  # if dict empty, start counter at 0
        else:  # dict not empty, get default value as latest defined tag
            lastsectioncounter = self.section_dict[list(self.section_dict)[-1]]
        # set section tag or get section tag if already been assigned
        previously_defined_section = list(self.section_dict.values())
        sectiontagcounter = self.section_dict.setdefault(repr(section_str), lastsectioncounter + 1)

        if sectiontagcounter not in previously_defined_section:
            sec_str = section_obj.get_section_command(section_tag=sectiontagcounter)
            self.section_command_list.append(sec_str)

            # print to terminal
            print("Section {}, of tag {} created".format(section_type, sectiontagcounter))
        else:
            print("Section {} with tag {} has been previously defined"
                  .format(section_type, sectiontagcounter))
        return sectiontagcounter

    # Function to set grillage elements
    def set_member(self, grillage_member_obj: GrillageMember, member=None):
        """
        Function to set grillage member class object to elements of grillage members.

        :param grillage_member_obj: Grillage_member class object
        :param member: str of member category - select from standard grillage elements

         ===================================   ===========================================================================
           1                                    edge_beam
           2                                    exterior_main_beam_1
           3                                    interior_main_beam
           4                                    exterior_main_beam_1
           5                                    edge_slab
           6                                    transverse_slab
         ===================================   ===========================================================================

        :return: sets member object to element of grillage in OpsGrillage instance
        :raises ValueError: If model instance is not created beforehand i.e. missing preceding create_ops() command.
        """
        #if self.Mesh_obj is None:
        #    raise ValueError("Model instance not created. Run ops.create_ops() function before setting members")
        # check and write member's section command
        section_tag = self.__write_section(grillage_member_obj)
        # check and write member's material command
        material_tag = self.__write_uniaxial_material(member=grillage_member_obj)
        # dictionary for key = common member tag, val is list of str for ops.element()
        ele_command_dict = dict()
        ele_command_list = []
        # if option for pyfile is True, write the header for element group commands
        if self.pyfile:
            with open(self.filename, 'a') as file_handle:
                file_handle.write("# Element generation for member: {}\n".format(member))
        z_flag = False
        x_flag = False
        edge_flag = False
        common_member_tag = []
        # get common element member tags based on input string
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
        elif member == "transverse_slab":  # For now, set None as to assign as slab
            common_member_tag = "slab"
        else:
            raise ValueError("Member str not a standard grillage element - refer to documentation/Module Description"
                             "for valid member and input string")

        ele_width = 1
        # if member properties is based on unit width (e.g. slab elements), get width of element and assign properties
        if grillage_member_obj.section.unit_width and common_member_tag =="slab":
            for ele in self.Mesh_obj.trans_ele:
                n1 = ele[1]  # node i
                n2 = ele[2]  # node j
                node_tag_list = [n1, n2]
                # get node width of node_i and node_j
                lis_1 = self.Mesh_obj.node_width_x_dict[n1]
                lis_2 = self.Mesh_obj.node_width_x_dict[n2]
                ele_width = 1
                ele_width_record = []
                # for the two list of vicinity nodes, find their distance and store in ele_width_record
                for lis in [lis_1, lis_2]:
                    if len(lis) == 1:
                        ele_width_record.append(np.sqrt(lis[0][0] ** 2 + lis[0][1] ** 2 + lis[0][2] ** 2) / 2)
                    elif len(lis) == 2:
                        ele_width_record.append((np.sqrt(lis[0][0] ** 2 + lis[0][1] ** 2 + lis[0][2] ** 2) +
                                                 np.sqrt(lis[1][0] ** 2 + lis[1][1] ** 2 + lis[1][2] ** 2)) / 2)
                    else:
                        #
                        break
                ele_width = np.mean(
                    ele_width_record)  # if member lies between a triangular and quadrilateral grid, get mean between
                # both width
                # here take the average width in x directions

                ele_str = grillage_member_obj.get_element_command_str(ele_tag=ele[0], node_tag_list=node_tag_list,
                                                                      transf_tag=ele[4], ele_width=ele_width,
                                                                      materialtag=material_tag, sectiontag=section_tag)
                ele_command_list.append(ele_str)
                # if self.pyfile:
                #     with open(self.filename, 'a') as file_handle:
                #         file_handle.write(ele_str)
                # else:
                #     eval(ele_str)
        else:
            # loop each element z group assigned under common_member_tag
            if z_flag:
                for z_groups in self.Mesh_obj.common_z_group_element[common_member_tag]:
                    # assign properties to elements in z group
                    for ele in self.Mesh_obj.z_group_to_ele[z_groups]:
                        node_tag_list = [ele[1], ele[2]]
                        ele_str = grillage_member_obj.get_element_command_str(ele_tag=ele[0],
                                                                              node_tag_list=node_tag_list,
                                                                              transf_tag=ele[4], ele_width=ele_width,
                                                                              materialtag=material_tag,
                                                                              sectiontag=section_tag)

                        ele_command_list.append(ele_str)

                        # if self.pyfile:
                        #     with open(self.filename, 'a') as file_handle:
                        #         file_handle.write(ele_str)
                        # else:
                        #     eval(ele_str)
                    self.ele_group_assigned_list.append(z_groups)
            elif edge_flag:
                for ele in self.Mesh_obj.edge_span_ele:
                    if ele[3] == common_member_tag:
                        # ele_str = grillage_member_obj.section.get_element_command_str(
                        #     ele_tag=ele[0], n1=ele[1], n2=ele[2], transf_tag=ele[4], ele_width=ele_width)
                        node_tag_list = [ele[1], ele[2]]
                        ele_str = grillage_member_obj.get_element_command_str(ele_tag=ele[0],
                                                                              node_tag_list=node_tag_list,
                                                                              transf_tag=ele[4], ele_width=ele_width,
                                                                              materialtag=material_tag,
                                                                              sectiontag=section_tag)
                        ele_command_list.append(ele_str)
                        # if self.pyfile:
                        #     with open(self.filename, 'a') as file_handle:
                        #         file_handle.write(ele_str)
                        # else:
                        #     eval(ele_str)
                    self.ele_group_assigned_list.append("edge: {}".format(common_member_tag))
            # here set the element command list to the common member tag, if previously defined (key exist),
            # overwrite the element command list for that key
        ele_command_dict[common_member_tag] = ele_command_list
        self.element_command_list.append(ele_command_dict)

    # function to set shell members
    def set_shell_members(self, grillage_member_obj: GrillageMember, quad=True, tri=False):
        """
        Function to set shell/quad members across entire mesh grid.

        :param quad:
        :param tri:
        :param grillage_member_obj: GrillageMember object
        :type grillage_member_obj: GrillageMember
        :raises ValueError: If GrillageMember object was not specified for quad or shell element. Also raises this error
                            if components of GrillageMember object (e.g. section or material) was not properly defined
                            for the specific shell element in accordance with Opensees conventions.

        .. note::
            To distinguish triangular elements with Quad elements

        """
        # this function creates shell elements out of the node grids of Mesh object
        shell_counter = 1
        if self.Mesh_obj is None:
            raise ValueError("Model instance not created. Run ops.create_ops() function before setting members")
        # check and write member's section command if any
        section_tag = self.__write_section(grillage_member_obj)
        # check and write member's material command if any
        material_tag = self.__write_uniaxial_material(member=grillage_member_obj)
        # instantiate shell element list
        shell_element_list = []
        shell_element_dict = dict()

        for grid_nodes_list in self.Mesh_obj.grid_number_dict.values():
            ele_str = grillage_member_obj.get_element_command_str(ele_tag=shell_counter, node_tag_list=grid_nodes_list,
                                                                  materialtag=material_tag, sectiontag=section_tag)
            shell_element_list.append(ele_str)
            if self.pyfile:
                with open(self.filename, 'a') as file_handle:
                    file_handle.write(ele_str)
            else:
                eval(ele_str)

    # function to set material obj of grillage model.
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
    # Functions to find nodes or grids correspond to a point or line + distributing
    # loads to grillage nodes. These are low level functions not accessible from API.

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
        # from starting point of line load
        # initiate variables
        start_grid = []
        next_grid = []
        x = 0
        z = 0
        x_start = []
        z_start = []
        colinear_list = []  # list storing coordinates *sublist of element coinciding points
        intersect_spec = dict()  # a sub dict for characterizing the line segment's intersecting points within grid
        # sub_dict has the following keys:
        # {bound: , long_intersect: , trans_intersect, edge_intersect, ends:}
        # find grids where start point of line load lies in
        start_nd, start_grid = self.get_point_load_nodes(line_load_obj.load_point_1)
        last_nd, last_grid = self.get_point_load_nodes(line_load_obj.line_end_point)

        line_grid_intersect = dict()
        # loop each grid check if line segment lies in grid
        for grid_tag, grid_nodes in self.Mesh_obj.grid_number_dict.items():
            point_list = []
            # loop all nodes in grid to get coordinates
            for node_tag in grid_nodes:
                coord = self.Mesh_obj.node_spec[node_tag]['coordinate']
                coord_point = Point(coord[0], coord[1], coord[2])
                point_list.append(coord_point)
            # get long, trans and edge elements in the grids. This is for searching intersection later on
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

                    # find intersecting points within grid- R annotates for intersection, z,x,edge stands for
                    # respective element type (long, trans, edge)
                    Rz, Rx, Redge, R_z_col, R_x_col, R_edge_col = self.__get_intersecting_elements(grid_tag, start_grid,
                                                                                                   last_grid,
                                                                                                   line_load_obj,
                                                                                                   long_ele_index,
                                                                                                   trans_ele_index,
                                                                                                   edge_ele_index)
                    if R_z_col or R_x_col or R_edge_col:
                        colinear_list += R_z_col if R_z_col else []
                        colinear_list += R_x_col if R_x_col else []
                        colinear_list += R_edge_col if R_edge_col else []

                    grid_inter_points += Rz + Rx + Redge
                    # check if point is not double assigned
                    if grid_tag not in line_grid_intersect.keys():
                        intersect_spec.setdefault("long_intersect", Rz)
                        intersect_spec.setdefault("trans_intersect", Rx)
                        #
                        intersect_spec.setdefault("edge_intersect", Redge)
                        line_grid_intersect.setdefault(grid_tag, intersect_spec)
                    intersect_spec = dict()  # reset intersect spec for next grid

        # update line_grid_intersect by removing grids if line coincide with elements and multiple grids of vicinity
        # grids are returned with same values
        removed_key = []
        edited_dict = line_grid_intersect.copy()

        # update line_grid_intersect adding start and end points of line segment to the dict within grid key
        for grid_key, int_list in edited_dict.items():
            if not any([n >= 2 for n in [len(val) for val in int_list.values()]]):
                if grid_key == start_grid or start_grid in self.Mesh_obj.grid_vicinity_dict[grid_key].values():
                    int_list.setdefault("ends", [[line_load_obj.load_point_1.x, line_load_obj.load_point_1.y,
                                                  line_load_obj.load_point_1.z]])
                    # edited_dict[grid_key] += [
                    #     [line_load_obj.load_point_1.x, line_load_obj.load_point_1.y,
                    #      line_load_obj.load_point_1.z]]
                elif grid_key == last_grid or last_grid in self.Mesh_obj.grid_vicinity_dict[grid_key].values():
                    int_list.setdefault("ends", [[line_load_obj.line_end_point.x, line_load_obj.line_end_point.y,
                                                  line_load_obj.line_end_point.z]])
                    # edited_dict[grid_key] += [
                    #     [line_load_obj.line_end_point.x, line_load_obj.line_end_point.y,
                    #      line_load_obj.line_end_point.z]]
                else:
                    int_list.setdefault("ends", [])
            else:
                int_list.setdefault("ends", [])
        # last check to remove duplicate grids due to having colinear conditions
        # i.e. where two vicinity grids with same intersection points are stored in edited_dict
        for grid_key, int_list in line_grid_intersect.items():
            if grid_key not in removed_key:
                check_dup_list = [int_list == val for val in line_grid_intersect.values()]
                # if there are duplicates check_dup_list will be greater than 1,
                # another case to remove if
                if sum(check_dup_list) > 1:
                    # check if grid key is a vicinity grid of current grid_key
                    for dup_key in [key for (count, key) in enumerate(line_grid_intersect.keys()) if
                                    check_dup_list[count] and key is not grid_key]:
                        if dup_key in [start_grid, last_grid]:
                            continue
                        elif dup_key in self.Mesh_obj.grid_vicinity_dict[grid_key].values():
                            removed_key.append(dup_key)
                            del edited_dict[dup_key]

        return edited_dict

    # private function to find intersection points of line/patch edge within grid
    def __get_intersecting_elements(self, current_grid, line_start_grid, line_end_grid, line_load_obj, long_ele_index,
                                    trans_ele_index, edge_ele_index):
        R_z = []  # temporary
        Rz = []
        R_x = []  # temporary
        Rx = []
        R_edge = []  # temporary placeholder for Redge
        Redge = []
        R_x_col = []
        R_z_col = []
        R_edge_col = []
        for long_ele in [self.Mesh_obj.long_ele[i] for i in long_ele_index]:
            pz1 = self.Mesh_obj.node_spec[long_ele[1]]['coordinate']  # point z 1
            pz2 = self.Mesh_obj.node_spec[long_ele[2]]['coordinate']  # point z 2
            pz1 = Point(pz1[0], pz1[1], pz1[2])  # convert to point namedtuple
            pz2 = Point(pz2[0], pz2[1], pz2[2])  # convert to point namedtuple
            # get the line segment within the grid. Line segment defined by two points assume model plane = 0 [x_1, z_1
            # ], and [x_2, z_2]
            x_1, x_2, z_1, z_2 = self.__check_line_ends_in_grid(pz1, pz2, current_grid, line_start_grid, line_end_grid,
                                                                line_load_obj)
            p_1 = Point(x_1, pz1.y, z_1)  # Assume same plane
            p_2 = Point(x_2, pz2.y, z_2)  # Assume same plane
            # check if special case - (1) one either is none, line segment does not exist
            if any([x_1 is None, x_2 is None, z_1 is None, z_2 is None]):
                continue
            if p_1 == p_2:  # (2) if both points of line are identical, point equates to an intersection point on long
                # member
                Rz.append([p_1.x, p_1.y, p_1.z])
                continue
            # if neither special case, check intersection
            intersect_z, colinear_z = check_intersect(pz1, pz2, p_1, p_2)
            if colinear_z:
                if p_1 == p_2:
                    R_z_col.append([p_1.x, p_1.y, p_1.z])
                else:  #
                    R_z_col.append([p_1.x, p_1.y, p_1.z])
                    R_z_col.append([p_2.x, p_2.y, p_2.z])
                # line is colinear to long ele, start and end points are
                # if pz1.x < p_1.x:
                #     subdict_long = [[p_1.x, p_1.z], [pz2.x, pz2.z]]
                # else:
                #     subdict_long = [[p_1.x, p_1.z], [pz1.x, pz1.z]]
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
                #
                Rx.append([p_1.x, p_1.y, p_1.z])
                continue
            # check potential for intersection or co linear condition
            intersect_x, colinear_x = check_intersect(px1, px2, p_1, p_2)
            if colinear_x:
                # line is trans ele, now check if both points are equal - colinear and equal means they coincide a node
                # of the element
                if p_1 == p_2:
                    R_x_col.append([p_1.x, p_1.y, p_1.z])
                else:  #
                    R_x_col.append([p_1.x, p_1.y, p_1.z])
                    R_x_col.append([p_2.x, p_2.y, p_2.z])

                # if p_1.z == p_2.z:  # colinear and two points are identical points
                #     subdict_trans = [[px1.x, px1.z], [px2.x, px2.z]]
                # elif px1.x < p_1.x:
                #     subdict_trans = [[p_1.x, p_1.z], [px2.x, px2.z]]
                # else:  # px1.x > p_1.x
                #     subdict_trans = [[p_1.x, p_1.z], [px1.x, px1.z]]
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
            p_1 = Point(x_1, p_edge_1.y, z_1)  # Assume same model plane y = 0
            p_2 = Point(x_2, p_edge_2.y, z_2)  # Assume same model plane y = 0
            # if any x or z value is null, line segment does not exist for the range, continue to next trans ele
            if any([x_1 is None, x_2 is None, z_1 is None, z_2 is None]):
                continue
            if p_1 == p_2:  # (2) if both points of line are the exact point, point equates to an intersection point
                Redge.append([p_1.x, p_1.y, p_1.z])  # Redge variable to be returned - as list
                continue
            intersect_x, colinear_edge = check_intersect(p_edge_1, p_edge_2, p_1, p_2)
            if colinear_edge:
                # line is colinear to long ele, start and end points are
                if p_1 == p_2:
                    R_edge_col.append([p_1.x, p_1.y, p_1.z])
                else:  #
                    R_edge_col.append([p_1.x, p_1.y, p_1.z])
                    R_edge_col.append([p_2.x, p_2.y, p_2.z])
                # if p_1.z == p_2.z:  # colinear and two points are identical points
                #     subdict_trans = [[p_edge_1.x, p_edge_1.z], [p_edge_2.x, p_edge_2.z]]
                # elif p_edge_1.x < p_1.x:
                #     subdict_trans = [[p_1.x, p_1.z], [p_edge_2.x, p_edge_2.z]]
                # else:  # px1.x > p_1.x
                #     subdict_trans = [[p_1.x, p_1.z], [p_edge_1.x, p_edge_1.z]]
            elif intersect_x:
                L1 = line([p_edge_1.x, p_edge_1.z], [p_edge_2.x, p_edge_2.z])
                L2 = line([x_1, z_1], [x_2, z_2])
                R_edge = intersection(L1, L2)  # temporary R_edge variable
                Redge.append([R_edge[0], p_edge_1.y, R_edge[1]])  # Redge variable to be returned - as list
        return Rz, Rx, Redge, R_z_col, R_x_col, R_edge_col

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
        # function to return nodes bounded by patch load
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

        # Function to assign line load to mesh. Procedure to assign line load is as follows:
        # . get properties of line on the grid
        # . convert line load to equivalent point load
        # . Find position of equivalent point load
        # . Runs assignment for point loads function (assign_point_to_four_node) using equivalent point load

        # loop each grid
        load_str_line = []
        for grid, points in line_grid_intersect.items():
            if "ends" not in points.keys():  # hard code fix to solve colinear problems - see API notes
                continue  # continue to next load assignment
            # extract two point of intersections within the grid
            # depending on the type of line intersections
            if len(points["long_intersect"]) >= 2:  # long, long
                p1 = points["long_intersect"][0]
                p2 = points["long_intersect"][1]
            elif len(points["trans_intersect"]) >= 2:  # trans trans
                p1 = points["trans_intersect"][0]
                p2 = points["trans_intersect"][1]
            elif points["long_intersect"] and points["trans_intersect"]:  # long, trans
                p1 = points["long_intersect"][0]
                p2 = points["trans_intersect"][0]
            elif points["long_intersect"] and points["edge_intersect"]:  # long, edge
                p1 = points["long_intersect"][0]
                p2 = points["edge_intersect"][0]
            elif points["trans_intersect"] and points["edge_intersect"]:  # trans, edge
                p1 = points["trans_intersect"][0]
                p2 = points["edge_intersect"][0]
            elif points["long_intersect"] and points["ends"]:  # long, ends
                p1 = points["long_intersect"][0]
                p2 = points["ends"][0]
            elif points["trans_intersect"] and points["ends"]:  # trans, ends
                p1 = points["trans_intersect"][0]
                p2 = points["ends"][0]
            elif points["edge_intersect"] and points["ends"]:  # edge, ends
                p1 = points["edge_intersect"][0]
                p2 = points["ends"][0]
            else:
                p1 = [0, 0, 0]
                p2 = p1

            # get length of line
            L = np.sqrt((p1[0] - p2[0]) ** 2 + (p1[2] - p2[2]) ** 2)

            # get magnitudes at point 1 and point 2
            w1 = line_load_obj.interpolate_udl_magnitude([p1[0], 0, p1[1]])
            w2 = line_load_obj.interpolate_udl_magnitude([p2[0], 0, p2[1]])
            W = (w1 + w2) * L / 2
            # get mid point of line
            x_bar = ((2 * w1 + w2) / (w1 + w2)) * L / 3  # from p2
            load_point = line_load_obj.get_point_given_distance(xbar=x_bar,
                                                                point_coordinate=[p2[0], self.y_elevation, p2[2]])

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
        # merging process of the intersect grid dicts
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
            # loop each int points - add extract coordinates, get patch magnitude using interpolation ,
            # convert coordinate to namedtuple Loadpoint and append to point list p_list
            for int_list in int_point_list.values():
                for int_point in int_list:  # [x y z]
                    p = patch_load_obj.patch_mag_interpolate(int_point[0], int_point[
                        2]) if int_point != [] else []  # object function returns array like
                    # p is array object, extract
                    p_list.append(LoadPoint(int_point[0], int_point[1], int_point[2], p[0]) if int_point != [] else [])
            # loop each node in grid points
            for items in node_in_grid:
                coord = self.Mesh_obj.node_spec[items]['coordinate']
                p = patch_load_obj.patch_mag_interpolate(coord[0], coord[2])[0]  # object function returns array like
                p_list.append(LoadPoint(coord[0], coord[1], coord[2], p))
            # Loop each p_list object to find duplicates if any, remove duplicate
            for count, point in enumerate(p_list):
                dupe = [point == val for val in p_list]
                # if duplicate, remove value
                if sum(dupe) > 1:
                    p_list.pop(count)
            # sort points in counterclockwise
            p_list = sort_vertices(p_list)  # sort takes namedtuple
            # get centroid of patch on grid
            xc, yc, zc = get_patch_centroid(p_list)
            inside_point = Point(xc, yc, zc)
            # volume = area of base x average height
            # _, A = calculate_area_given_four_points(inside_point, p_list[0], p_list[1], p_list[2], p_list[3])
            A = self.get_node_area(inside_point=inside_point, p_list=p_list)
            mag = A * sum([point.p for point in p_list]) / len(p_list)
            # assign point and mag to 4 nodes of grid
            load_str = self.assign_point_to_four_node(point=[xc, yc, zc], mag=mag)
            self.global_load_str += load_str
        return self.global_load_str

    @staticmethod
    def get_node_area(inside_point, p_list) -> float:
        A = calculate_area_given_vertices(p_list)
        return A

    # ----------------------------------------------------------------------------------------------------------
    #  functions to add load case and load combination
    def distribute_load_types_to_model(self, load_case_obj: Union[LoadCase, CompoundLoad]) -> list:

        global load_groups
        load_str = []
        # check the input parameter type, set load_groups parameter according to its type
        if isinstance(load_case_obj, LoadCase):
            load_groups = load_case_obj.load_groups
        elif isinstance(load_case_obj.load_groups[0]['load'], CompoundLoad):
            load_groups = load_case_obj.load_groups[0]['load'].compound_load_obj_list
        # loop through each load object
        load_str = []
        for load_dict in load_groups:
            load_obj = load_dict['load']
            if isinstance(load_obj, CompoundLoad):
                # load_obj is a Compound load class, start a nested loop through each load class within compound load
                # nested loop through each load in compound load, assign and get
                for nested_list_of_load in load_obj.compound_load_obj_list:
                    if isinstance(nested_list_of_load, NodalLoad):
                        load_str += nested_list_of_load.get_nodal_load_str()
                    elif isinstance(nested_list_of_load, PointLoad):
                        load_str += self.assign_point_to_four_node(point=list(nested_list_of_load.load_point_1)[:-1],
                                                                   mag=nested_list_of_load.load_point_1.p)
                    elif isinstance(nested_list_of_load, LineLoading):
                        line_grid_intersect = self.get_line_load_nodes(
                            nested_list_of_load)  # returns self.line_grid_intersect
                        self.global_line_int_dict.append(line_grid_intersect)
                        load_str += self.assign_line_to_four_node(nested_list_of_load, line_grid_intersect)
                    elif isinstance(nested_list_of_load, PatchLoading):
                        load_str += self.assign_patch_load(nested_list_of_load)
            else:
                # run single assignment of load type (load_obj is a load class)
                if isinstance(load_obj, NodalLoad):
                    load_str += [load_obj.get_nodal_load_str()]  # here return load_str as list with single element
                elif isinstance(load_obj, PointLoad):
                    load_str += self.assign_point_to_four_node(point=list(load_obj.load_point_1)[:-1],
                                                               mag=load_obj.load_point_1.p)
                elif isinstance(load_obj, LineLoading):
                    line_grid_intersect = self.get_line_load_nodes(load_obj)  # returns self.line_grid_intersect
                    self.global_line_int_dict.append(line_grid_intersect)
                    load_str += self.assign_line_to_four_node(load_obj, line_grid_intersect)
                elif isinstance(load_obj, PatchLoading):
                    load_str += self.assign_patch_load(load_obj)

        return load_str

    def add_load_case(self, load_case_obj: LoadCase, load_factor=1):
        """
        Function to add individual load cases to OpsGrillage instance.

        :param load_factor: Optional load factor for the prescribed load case
        :param load_case_obj: A load case object of the load condition
        :type load_case_obj: LoadCase

        """
        # update the load command list of load case object
        load_str = self.distribute_load_types_to_model(load_case_obj=load_case_obj)
        # store load case + load command in dict and add to load_case_list
        load_case_dict = {'name': load_case_obj.name, 'loadcase': load_case_obj, 'load_command': load_str,
                          'load_factor': load_factor}  # FORMATTING HERE

        self.load_case_list.append(load_case_dict)
        print("Load Case {} added".format(load_case_obj.name))

    def analyse_load_case(self):
        """
        Function to analyse all basic load cases defined previously using add_load_case() function

        :except:

        """
        # analyse all load case defined in self.load_case_dict for OpsGrillage instance
        # loop each load case dict
        for load_case_dict in self.load_case_list:
            # create analysis object, run and get results
            load_case_obj = load_case_dict['loadcase']
            load_command = load_case_dict['load_command']
            load_factor = load_case_dict['load_factor']
            load_case_analysis = Analysis(analysis_name=load_case_obj.name, ops_grillage_name=self.model_name,
                                          pyfile=self.pyfile,
                                          time_series_counter=self.global_time_series_counter,
                                          pattern_counter=self.global_pattern_counter,
                                          node_counter=self.Mesh_obj.node_counter,
                                          ele_counter=self.Mesh_obj.element_counter)
            load_case_analysis.add_load_command(load_command, load_factor=load_factor)
            # run the Analysis object, collect results, and store Analysis object in the list for Analysis load case
            self.global_time_series_counter, self.global_pattern_counter, node_disp, ele_force \
                = load_case_analysis.evaluate_analysis()
            # store result in Recorder object
            self.results.insert_analysis_results(analysis_obj=load_case_analysis)

    def add_load_combination(self, load_combination_name: str, load_case_name_dict: dict):
        """
        To be deprecated

        """
        load_case_dict_list = []  # list of dict: structure of dict See line
        # create dict with key (combination name) and val (list of dict of load cases)
        for load_case_name, load_factor in load_case_name_dict.items():
            # lookup the defined load cases for load_case_name
            a = [index for (index, val) in enumerate(self.load_case_list) if val['name'] == load_case_name]
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

        self.load_combination_dict.setdefault(load_combination_name, load_case_dict_list)
        print("Load Combination: {} created".format(load_combination_name))

    def add_moving_load_case(self, moving_load_obj: MovingLoad, load_factor=1):
        """
        Function to add Moving load case to OpsGrillage instance.

        :param moving_load_obj: Moving load class object instance
        :type moving_load_obj: MovingLoad
        :param load_factor: optional load factor to be set for all incremental load case. Default is 1.
        :type load_factor: Int or Float

        """
        # get the list of individual load cases
        list_of_incr_load_case_dict = []
        # for each load case, find the load commands of load distribution
        for moving_load_case_list in moving_load_obj.moving_load_case:
            for increment_load_case in moving_load_case_list:
                load_str = self.distribute_load_types_to_model(load_case_obj=increment_load_case)
                increment_load_case_dict = {'name': increment_load_case.name, 'loadcase': increment_load_case,
                                            'load_command': load_str,
                                            'load_factor': load_factor}
                list_of_incr_load_case_dict.append(increment_load_case_dict)
            self.moving_load_case_dict[moving_load_obj.name] = list_of_incr_load_case_dict

        print("Moving load case: {} created".format(moving_load_obj.name))

    def analyse_moving_load_case(self, moving_load_case_name: str = None):
        """
        Function to analyze all defined moving load cases.

        :param moving_load_case_name: Name of specific load case to be ran (Optional)
        :type moving_load_case_name: str

        """
        # function to analyse individual moving load case
        # create analysis object for each load case correspond to increment of moving paths
        # loop through all moving load objects
        if self.pyfile:
            print("Analysis of OpsGrillage in file writing mode - pyfile flag = True")
        list_of_inc_analysis = []
        for moving_load_obj, load_case_dict_list in self.moving_load_case_dict.items():
            for load_case_dict in load_case_dict_list:
                load_case_obj = load_case_dict['loadcase']  # maybe unused
                load_command = load_case_dict['load_command']
                load_factor = load_case_dict['load_factor']
                incremental_analysis = Analysis(analysis_name=load_case_obj.name,
                                                ops_grillage_name=self.model_name,
                                                pyfile=self.pyfile,
                                                time_series_counter=self.global_time_series_counter,
                                                pattern_counter=self.global_pattern_counter,
                                                node_counter=self.Mesh_obj.node_counter,
                                                ele_counter=self.Mesh_obj.element_counter)
                incremental_analysis.add_load_command(load_command, load_factor=load_factor)
                self.global_time_series_counter, self.global_pattern_counter, node_disp, ele_force \
                    = incremental_analysis.evaluate_analysis()
                list_of_inc_analysis.append(incremental_analysis)
                # store result in Recorder object
            self.results.insert_analysis_results(list_of_inc_analysis=list_of_inc_analysis)

    def get_results(self):
        """
        Function to get results from all load cases.

        :return: A data array for basic all load case, and a list of data arrays for each moving load cases if any
        :returns basic_da: Data Array for all basic load case. For details of components see :doc:`Result` Page
        :returns list_moving_da: A list of Data array each element correspond to a Data array for a single moving load
        :type list_moving_da: list
        """
        basic_da, list_moving_da = self.results.compile_data_array()
        return basic_da, list_moving_da


# ---------------------------------------------------------------------------------------------------------------------
class Analysis:
    """
    Main class to handle the run/execution of load case + load combination + moving load analysis. Analysis class is
    created and used within OpsGrillage class after "adding load case", "adding load combination" and "adding moving
    load" procedures.

    The following are the roles of Analysis object:

    * store information of ops commands for performing static (default) analysis of single/multiple load case(s).
    * execute the required ops commands to perform analysis using the OpsGrillage model instance.
    * if flagged, writes an executable py file instead which performs the exact analysis as it would for an OpsGrillage instance instead.
    * manages multiple load case's ops.load() commands, applying the specified load factors to the load cases for load combinations

    """
    remove_pattern_command: str

    def __init__(self, analysis_name: str, ops_grillage_name: str, pyfile: bool, node_counter, ele_counter,
                 analysis_type='Static',
                 time_series_counter=1, pattern_counter=1):
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
        self.time_series_counter = time_series_counter
        self.plain_counter = pattern_counter
        # Variables recording results of analysis
        self.node_disp = dict()  # key node tag, val list of dof
        self.ele_force = dict()  # key ele tag, val list of forces on nodes of ele[ order according to ele tag]
        # preset ops analysis commands
        self.wipe_command = "ops.wipeAnalysis()\n"
        self.numberer_command = "ops.numberer('Plain')\n"  # default plain
        self.system_command = "ops.system('BandGeneral')\n"  # default band general
        self.constraint_command = "ops.constraints('Plain')\n"  # default plain
        self.algorithm_command = "ops.algorithm('Linear')\n"  # default linear
        self.analyze_command = "ops.analyze(1)\n"  # default 1 step
        self.analysis_command = "ops.analysis(\"{}\")\n".format(analysis_type)
        self.intergrator_command = "ops.integrator('LoadControl', 1)\n"
        self.mesh_node_counter = node_counter
        self.mesh_ele_counter = ele_counter
        self.remove_pattern_command = "ops.remove('loadPattern',{})\n".format(self.plain_counter - 1)
        # if true for pyfile, create pyfile for analysis command
        if self.pyfile:
            with open(self.analysis_file_name, 'w') as file_handle:
                # create py file or overwrite existing
                # writing headers and description at top of file
                file_handle.write(
                    "# Executable py file for Analysis of \n# Model name: {}\n".format(self.ops_grillage_name))
                file_handle.write("# Load case: {}\n".format(self.analysis_name))
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
        time_series = self.time_series_command(load_factor)  # get time series command - LF default 1
        pattern_command = self.pattern_command()  # get pattern command
        time_series_dict = {'time_series': time_series, 'pattern': pattern_command, 'load_command': load_str}
        self.load_cases_dict_list.append(time_series_dict)  # add dict to list

    def evaluate_analysis(self):
        # write/execute ops.load commands for load groups
        if self.pyfile:
            with open(self.analysis_file_name, 'a') as file_handle:
                file_handle.write(self.wipe_command)
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
            eval(self.wipe_command)
            if self.plain_counter - 1 != 1:  # plain counter increments by 1 upon self.pattern_command function, so -1 here
                eval(self.remove_pattern_command)  # remove previous load pattern if any
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
        # extract results
        node_disp, ele_force = self.extract_grillage_responses()
        # return time series and plain counter to update global time series and plain counter by by OpsGrillage
        return self.time_series_counter, self.plain_counter, node_disp, ele_force

    def extract_grillage_responses(self):
        if not self.pyfile:
            # first loop extract node displacements
            for node_tag in range(1, self.mesh_node_counter):
                disp_list = ops.nodeDisp(node_tag)
                self.node_disp.setdefault(node_tag, disp_list)

            for ele_tag in range(1, self.mesh_ele_counter):
                ele_force = ops.eleResponse(ele_tag, 'localForces')
                self.ele_force.setdefault(ele_tag, ele_force)

        print("Extract completed")
        return self.node_disp, self.ele_force


class Results:
    """
    Main class to store results of an Analysis class object, process into data array output for post processing/plotting.
    Class object is accessed within OpsGrillage class object.
    """

    def __init__(self, mesh_obj: Mesh):
        # static single analysis load cases
        self.basic_load_case_record = dict()
        self.moving_load_case_record = []
        self.moving_load_counter = 0
        # dynamic moving load (incremental) load cases
        self.mesh_obj = mesh_obj

    def insert_analysis_results(self, analysis_obj: Analysis = None, list_of_inc_analysis: list = None):
        # Create/parse data based on incoming analysis object or list of analysis obj (moving load)
        if analysis_obj:
            # compile ele forces for each node
            node_disp = analysis_obj.node_disp
            node_force = dict.fromkeys(analysis_obj.node_disp.keys(), [0, 0, 0, 0, 0, 0])  # copy the dict keys
            # extract element forces and sort them to according to nodes - summing in the process
            for ele_num, ele_forces in analysis_obj.ele_force.items():
                # get ele nodes
                ele_nodes = ops.eleNodes(ele_num)
                # for node i
                force_i = ele_forces[:6]  # list 6:
                # for node j
                force_j = ele_forces[6:]  # list 6:
                # update first node
                sum_force_i = [a + b for (a, b) in zip(force_i, node_force[ele_nodes[0]])]
                node_force.update({ele_nodes[0]: sum_force_i})
                # update second node
                sum_force_j = [a + b for (a, b) in zip(force_j, node_force[ele_nodes[1]])]
                node_force.update({ele_nodes[1]: sum_force_j})
            self.basic_load_case_record.setdefault(analysis_obj.analysis_name, [node_disp, node_force])
        # if
        elif list_of_inc_analysis:
            inc_load_case_record = dict()
            for inc_analysis_obj in list_of_inc_analysis:
                # compile ele forces for each node
                node_disp = inc_analysis_obj.node_disp
                node_force = dict.fromkeys(inc_analysis_obj.node_disp.keys(), [0, 0, 0, 0, 0, 0])  # copy the dict keys
                # extract element forces and sort them to according to nodes - summing in the process
                for ele_num, ele_forces in inc_analysis_obj.ele_force.items():
                    # get ele nodes
                    ele_nodes = ops.eleNodes(ele_num)
                    # for node i
                    force_i = ele_forces[:6]  # list 6:
                    # for node j
                    force_j = ele_forces[6:]  # list 6:
                    # update first node
                    sum_force_i = [a + b for (a, b) in zip(force_i, node_force[ele_nodes[0]])]
                    node_force.update({ele_nodes[0]: sum_force_i})
                    # update second node
                    sum_force_j = [a + b for (a, b) in zip(force_j, node_force[ele_nodes[1]])]
                    node_force.update({ele_nodes[1]: sum_force_j})
                inc_load_case_record.setdefault(inc_analysis_obj.analysis_name, [node_disp, node_force])

            self.moving_load_case_record.append(inc_load_case_record)

    def compile_data_array(self):
        # Final function called to compile all inserted analyses into xarray dataArray format
        # Dimension names
        dim = ["Loadcase", "Node", "Component"]
        # Coordinates of dimension
        node = list(self.mesh_obj.node_spec.keys())  # for Node
        # for Component
        component = ["dx", "dy", "dz", "theta_x", "theta_y", "theta_z", "Vx", "Vy", "Vz", "Mx", "My", "Mz"]

        # Sort data for dataArrays
        # for basic load case  {loadcasename:[{1:,2:...},{1:,2:...}], ... , loadcasename:[{1:,2:...},{1:,2:...} }
        basic_array_list = []
        basic_load_case_coord = []
        for load_case_name, resp_list_of_2_dict in self.basic_load_case_record.items():
            basic_array_list.append([a + b for (a, b) in zip(list(resp_list_of_2_dict[0].values()),
                                                             list(resp_list_of_2_dict[1].values()))])

            # Coordinate of Load Case dimension
            basic_load_case_coord.append(load_case_name)
            # combine disp and force with respect to Component axis : size 12
        basic_array = np.array(basic_array_list)
        # create data array for each basic load case if any
        basic_da = None
        if basic_array.size:
            basic_da = xr.DataArray(data=basic_array, dims=dim,
                                    coords={dim[0]: basic_load_case_coord, dim[1]: node, dim[2]: component})

        # for moving load cases
        # [ {}, {} ,..., {} ]  where each {} is a moving load {increloadcasename:[{1:,2:...},{1:,2:...}]..... }
        moving_daarray_list = []

        for moving_load_case_inc_dict in self.moving_load_case_record:  # for each moving load, loop thru increment LC
            inc_moving_load_case_coord = []
            inc_moving_array_list = []
            # for each load case increment in ML
            for increment_load_case_name, inc_resp_list_of_2_dict in moving_load_case_inc_dict.items():
                inc_moving_array_list.append([a + b for (a, b) in zip(list(inc_resp_list_of_2_dict[0].values()),
                                                                      list(inc_resp_list_of_2_dict[1].values()))])
                # Coordinate of Load Case dimension
                inc_moving_load_case_coord.append(increment_load_case_name)

            moving_array = np.array(inc_moving_array_list)
            ind_moving_da = xr.DataArray(data=moving_array, dims=dim,
                                         coords={dim[0]: inc_moving_load_case_coord, dim[1]: node, dim[2]: component})
            moving_daarray_list.append(ind_moving_da)

        return basic_da, moving_daarray_list
