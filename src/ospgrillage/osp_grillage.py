# -*- coding: utf-8 -*-
"""
This module contain the parent class OspGrillage which handles input information and outputs the grillage model instance
or executable py file. This is done by wrapping `OpenSeesPy` commands for creating models (nodes/elements).
This module also handles all load case assignment, analysis, and results by wrapping `OpenSeesPy` command for analysis
"""

from datetime import datetime
from itertools import combinations

import openseespy.opensees as ops

from ospgrillage.load import *
from ospgrillage.mesh import *
from ospgrillage.material import *
from ospgrillage.members import *
from ospgrillage.postprocessing import *
import xarray as xr


def create_grillage(**kwargs):
    """
    User interface to create :class:`~ospgrillage.osp_grillage.OspGrillage` object.

    The constructor takes the following arguments:

    :param model_type: Name string of model type - default is "beam"
    :type model_type: str
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
    :param mesh_type: Type of mesh either "Ortho" or "Oblique" - default "Ortho"
    :type mesh_type: string
    :param kwargs: See below

    :keyword:

    * ext_to_int_dist: (Int or Float, or a List of Int or Float) distance between internal beams and
    exterior main beams. If list is provided (usually size 2), apply each distinct distance to left and right
         side respectively.


    Depending on the ``model_type`` argument, this function returns the relevant concrete class of
    :class:`~ospgrillage.osp_grillage.OspGrillage`.

    :returns: :class:`~ospgrillage.osp_grillage.OspGrillageBeam` or :class:`~ospgrillage.osp_grillage.OspGrillageShell`
    """
    model_type = kwargs.get("model_type", "beam_only")
    if model_type == "shell_beam":  # if shell, create shell grillage type
        return OspGrillageShell(**kwargs)
    else:  # creates default model type - beam elements
        return OspGrillageBeam(**kwargs)


class GrillageElement:
    """
    Class to store grillage element data pertaining to generating ops.element() command. This class is handled by
    OspGrillage class to transfer information between GrillageMember, Mesh, and OspGrillage classes.
    """

    def __init__(self):
        # instantiate variables of elements
        self.ele_node_list = []
        # TODO trial with set_member() function


class OspGrillage:
    """
    Base class of grillage model. Stores information about mesh and grillage elements. Also provides methods to
    add load cases to grillage model for analysis.

    The class constructor provides an interface for the user to specify the geometric properties of the grillage model
    and its mesh.

    """

    def __init__(
        self,
        bridge_name,
        long_dim,
        width,
        skew: Union[list, float, int],
        num_long_grid: int,
        num_trans_grid: int,
        edge_beam_dist: Union[list, float, int],
        mesh_type="Ortho",
        model="3D",
        **kwargs,
    ):
        """
        Init the OspGrillage class

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
        :param num_trans_grid: Number of  grid lines in the transverse direction -
        :type num_trans_grid: int
        :param edge_beam_dist: Distance of edge beam node lines to exterior main beam node lines
        :type edge_beam_dist: int or float
        :param mesh_type: Type of mesh either "Ortho" for orthogonal mesh or "Oblique" for oblique mesh
        :type mesh_type: string
        :param kwargs: See below

        :keyword:
        * beam_z_spacing: (list of int or float) Custom distance of longitudinal members (global z - direction). Note
          this parameter supercedes num_long_grid.
        * beam_x_spacing: (list of int or float) Custom distance of transverse members (global x - direction). Note
          this parameter supercedes num_trans_grid.
        * ext_to_int_dist: (Int or Float, or a List of Int or Float) distance between internal beams
          and exterior main beams. If list is provided (usually size 2), apply each distinct distance to left and right
          side respectively.
        * multi_span_dist_list: (List of Int/Float) List of distance (x dir) correspond to span length of each multi span
        * multi_span_num_points: (List of Int) Num of transverse member correspond to spans of each element in multi_span_dist_list
          If not specified, takes int var for num_trans_beam and assigns to all spans of multi_span_dist_list
        * continuous: (Bool) To set continuity of spans. Default True. If False, separate spans by non_cont_spacing_x
        * stitch_slab_elements: (Bool) To set stictch elements between spans. Elements are set using `set_member()` with
          member= "stich_elements"
        * non_cont_spacing_x: (float) sets spacing or length of stitch elements.

        :raises ValueError: If skew angle is greater than 90. If number of transverse grid line is less than 2.


        """
        # store geometry input
        self.mesh_type = mesh_type  # mesh type either orthogonal or oblique
        self.model_name = bridge_name  # name string
        self.long_dim = long_dim  # span , defined c/c between support bearings
        self.width = width  # length of the bearing support - if skew  = 0 , this corresponds to width of bridge
        self.num_long_gird = num_long_grid  # number of longitudinal beams
        self.num_trans_grid = num_trans_grid  # number of grids for transverse members
        self.edge_width = edge_beam_dist  # width of cantilever edge beam

        # if skew is a list containing 2 skew angles, then set angles to the start and end edge of span
        if isinstance(skew, list):
            self.skew_a = skew[0]
            if len(skew) >= 2:
                self.skew_b = skew[1]
        else:  # both start and end edge span edges have same angle
            self.skew_a = skew  # angle in degrees
            self.skew_b = skew  # angle in degrees
        # check if angle is greater than 90
        if any([np.abs(self.skew_a) > 90, np.abs(self.skew_b) > 90]):
            raise ValueError(
                "Skew angle either start or end edge exceeds 90 degrees. Allowable range is -90 to 90"
            )
        # next check if arctan (L/w)

        # check if edge beam dist is provided as a list of size 2, set to edge_beam a and edge_beam b respectively
        if isinstance(edge_beam_dist, list):
            self.edge_width_a = edge_beam_dist[0]
            if len(edge_beam_dist) >= 2:
                self.edge_width_b = edge_beam_dist[1]
            else:
                self.edge_width_b = edge_beam_dist[0]
        else:  # same edge distance, set to both a and b
            self.edge_width_a = edge_beam_dist
            self.edge_width_b = edge_beam_dist

        # instantiate variables
        self.global_mat_object = []  # material matrix
        self.global_line_int_dict = []
        # list of components tags
        self.element_command_list = dict()  # list of str of ops.element() commands
        self.section_command_list = []  # list of str of ops.section() commands
        self.material_command_list = []  # list of str of ops.material() commands
        # list of common grillage elements - base class variable
        self.common_grillage_element_keys = [
            "edge_beam",
            "exterior_main_beam_1",
            "interior_main_beam",
            "exterior_main_beam_2",
            "start_edge",
            "end_edge",
            "stitch_elements",
            "transverse_slab",
        ]
        # prefix index of members after longitudinal members
        self.long_member_index = 4  # 0,1,2,3 correspond to edge, ext_a, interior_beam,
        # dict storing information
        self.common_grillage_element_z_group = dict()  # of common grillage
        self.section_dict = {}  # of section tags
        self.material_dict = {}  # of material tags
        # variables related to analysis - which can be unique to element/material/ types
        self.constraint_type = "Plain"  # base class - plain
        # collect mesh groups
        self.mesh_group = []  # for future release
        if self.mesh_type == "Ortho":
            self.ortho_mesh = True
        else:
            self.ortho_mesh = False

        self.y_elevation = 0  # default model plane is orthogonal plane of y = 0
        self.min_grid_ortho = 3  # for orthogonal mesh (skew>skew_threshold) region of orthogonal area default 3
        # set model space and degree's of freedom according to user input for model space
        if model == "2D":
            self.__ndm = 2  # OpenSess dimension 2
            self.__ndf = 3  # Degrees' of Freedom per node 3
        else:
            self.__ndm = 3  # OpenSees dimension 3
            self.__ndf = 6  # Degrees' of Freedom per node 6

        # default vector for standard (for 2D grillage in x - z plane) - 1 represent fix for [Vx,Vy,Vz, Mx, My, Mz]
        self.fix_val_pin = [1, 1, 1, 0, 0, 0]  # pinned
        self.fix_val_roller_x = [0, 1, 1, 0, 0, 0]  # roller
        self.fix_val_fixed = [1, 1, 1, 1, 1, 1]  # rigid /fixed support
        # default dict for support conditions
        self.fixity_vector = {
            "pin": [1, 1, 1, 0, 0, 0],
            "roller": [0, 1, 1, 0, 0, 0],
            "fixed": [1, 1, 1, 1, 1, 1],
        }
        # special rules for grillage - alternative to Properties of grillage definition - use for special dimensions
        self.skew_threshold = [
            10,
            30,
        ]  # threshold for grillage to allow option of mesh choices
        self.deci_tol = 4  # tol of decimal places

        # dict for load cases and load types
        self.global_load_str = []  # store load() commands
        self.global_patch_int_dict = dict()  # store patch intersection grid information
        self.load_case_list = (
            []
        )  # list of dict, example [{'loadcase':LoadCase object, 'load_command': list of str}..]
        self.load_combination_dict = (
            dict()
        )  # example {0:[{'loadcase':LoadCase object, 'load_command': list of str},
        # {'loadcase':LoadCase object, 'load_command': list of str}....]}
        self.moving_load_case_dict = dict()  # example [ list of load_case_dict]\
        # counters to keep track of ops time series and ops pattern objects for loading
        self.global_time_series_counter = 1
        self.global_pattern_counter = 1

        # file name for output py file
        self.filename = "{}_op.py".format(self.model_name)

        # calculate edge length of grillage accounting for skew
        self.trans_dim = self.width / math.cos(self.skew_a / 180 * math.pi)

        # Mesh objects, pyfile flag, and verbose flag
        self.pyfile = None
        self.results = None
        self.diagnostics = kwargs.get(
            "diagnostics", False
        )  # flag for diagnostics printed to terminal

        # kwargs for rigid link modelling option
        self.model_type = kwargs.get(
            "model_type", "beam_only"
        )  # accepts int type 1 or 2

        # for curve mesh
        self.mesh_radius = kwargs.get("mesh_radius", None)
        # check inputs
        if self.mesh_radius:
            if self.mesh_radius < self.long_dim:
                raise Exception("mesh_radius must be greater than long_dim of grillage")

        # ===========================================================================================================
        # Begin parsing mesh inputs and mesh procedures
        # ===========================================================================================================

        # create mesh object of grillage
        self.Mesh_obj = self._create_mesh(
            long_dim=self.long_dim,
            width=self.width,
            trans_dim=self.trans_dim,
            num_trans_beam=self.num_trans_grid,
            num_long_beam=self.num_long_gird,
            skew_1=self.skew_a,
            edge_dist_a=self.edge_width_a,
            edge_dist_b=self.edge_width_b,
            skew_2=self.skew_b,
            orthogonal=self.ortho_mesh,
            **kwargs,
        )

        # create dict of standard elements from the generated Mesh obj
        self._create_standard_element_list()  # base class method, concrete classes may overwrite this

        # flag for OpenSees model instance
        self.model_instance = False  # default false before creating

        # list storing all commands and str
        self.variable_command_list = []
        self.model_command_list = []  # to be populated
        self.analysis_command = None
        self.global_ele_counter = self.Mesh_obj.element_counter

        # vars for spring
        self.spring_edges = []
        self.spring_node_pairs = (
            {}
        )  # dict with keys being master node (support) and value being slave node (non-support)
        self.equal_dof_command_str_list = []  # list to store ops command

        # edge support type
        self.edge_support_type_dict = {
            edge_num: self.fixity_vector["roller"]
            for i, edge_num in enumerate(
                list(set(self.Mesh_obj.edge_node_recorder.values()))
            )
        }
        self.edge_support_type_dict.update({0: self.fixity_vector["pin"]})

    def _create_mesh(self, **kwargs):
        """
        Private function to create mesh. Creates the concrete Mesh class based on mesh type specified
        """
        if self.model_type == "beam_link":
            mesh_obj = BeamLinkMesh(**kwargs)
        elif self.model_type == "shell_beam":
            mesh_obj = ShellLinkMesh(**kwargs)
        elif self.model_type == "beam_only":
            mesh_obj = BeamMesh(**kwargs)
        else:
            mesh_obj = None
        if self.diagnostics:
            print("Meshing complete")
        return mesh_obj

    # interface function
    def create_osp_model(self, pyfile=False):
        """
        Function to create model instance in OpenSees model space. If pyfile input is True, function creates an
        executable pyfile for generating the grillage model in OpenSees model space.

        :param pyfile: if True returns an executable py file instead of creating OpenSees instance of model.
        :type pyfile: bool

        """
        self.pyfile = pyfile
        # if output mode, create the py file
        if self.pyfile:
            with open(self.filename, "w") as file_handle:
                # create py file or overwrite existing
                # writing headers and description at top of file
                file_handle.write(
                    "# Grillage generator wizard\n# Model name: {}\n".format(
                        self.model_name
                    )
                )
                # time
                now = datetime.now()
                dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
                file_handle.write("# Constructed on:{}\n".format(dt_string))
                # necessary imports
                file_handle.write(
                    "import numpy as np\nimport math\nimport openseespy.opensees as ops"
                    "\nimport openseespy.postprocessing.Get_Rendering as opsplt\n"
                )

        self._write_op_model()
        # run model generation in OpenSees or write generation command to py file
        self._run_mesh_generation()

        # create the result object for the grillage model
        self.results = Results(self.Mesh_obj)
        self._write_rigid_link()

    # function to run mesh generation
    def _run_mesh_generation(self):
        """
        Private function to write / execute commands. This function handles relevant OpenSeesPy commands
        """
        # write / execute model commands
        self._write_op_node(self.Mesh_obj)  # write node() commands
        self._write_op_fix(self.Mesh_obj)  # write fix() command for support nodes
        self._write_geom_transf(self.Mesh_obj)  # x dir members

        # write / execute variable definition command

        # write / execute material and sections
        for mat_str in self.material_command_list:
            if self.pyfile:
                with open(self.filename, "a") as file_handle:
                    file_handle.write("# Material definition \n")
                    file_handle.write(mat_str)
            else:
                eval(mat_str)
                self.model_command_list.append(mat_str)

        for sec_str in self.section_command_list:
            if self.pyfile:
                with open(self.filename, "a") as file_handle:
                    file_handle.write("# Create section: \n")
                    file_handle.write(sec_str)
            else:
                eval(sec_str)
                self.model_command_list.append(sec_str)

        # write /execute element commands

        for ele_tag, ele_str in self.element_command_list.items():
            if self.pyfile:
                with open(self.filename, "a") as file_handle:
                    file_handle.write(ele_str)
            else:
                eval(ele_str)
                self.model_command_list.append(ele_str)

        # write equalDOF commands
        self._write_equal_dof(node_tag_list=self.spring_node_pairs.items())

        # if created OpenSees instance, set instance flag
        if not self.pyfile:
            self.model_instance = True

    # interface function
    def set_boundary_condition(
        self,
        edge_group_counter: int = None,
        new_restraint_vector: list = None,
    ):
        """
        Function to set or modify customized support conditions.

        .. note::
            This feature to be available for future release.
        """
        if not isinstance(edge_group_counter, int):
            raise Exception("Int required for edge_group_counter= argument")

        if not self.model_instance:
            # reset the var
            self.edge_support_type_dict[edge_group_counter] = new_restraint_vector
        else:
            raise Exception(
                "Model instance have been created - append boundary conditions won't be applied: Hint - "
                "first set_boundary_condition() before create_osp_model()"
            )
        if new_restraint_vector:
            self.fix_val_pin = [1, 1, 1, 0, 0, 0]  # pinned
            self.fix_val_roller_x = [0, 1, 1, 0, 0, 0]  # roller
            self.fix_val_fixed = [1, 1, 1, 1, 1, 1]

    # private functions to write ops commands to output py file.
    def _write_geom_transf(self, mesh_obj, transform_type="Linear"):
        """
        Private function to write ops.geomTransf() to output py file.
        :param transform_type: transformation type
        :type transform_type: str

        """
        # loop all transform dict items,
        for k, v in mesh_obj.transform_dict.items():
            vxz = k.split("|")[0]  # first substring is vector xz
            offset = k.split("|")[
                1
            ]  # second substring is global offset of node i and j of element
            if eval(offset):
                offset_list = eval(
                    offset
                )  # list of global offset of node i entry 0 and node j entry 1
                geom_tranfs_str = 'ops.geomTransf("{type}", {tag}, *{vxz}, {offset_i}, {offset_j})\n'.format(
                    type=transform_type,
                    tag=v,
                    vxz=eval(vxz),
                    offset_i=offset_list[0],
                    offset_j=offset_list[1],
                )

                if self.pyfile:
                    with open(self.filename, "a") as file_handle:
                        file_handle.write(geom_tranfs_str)
                else:
                    eval(geom_tranfs_str)

            else:
                geom_tranfs_str = 'ops.geomTransf("{type}", {tag}, *{vxz})\n'.format(
                    type=transform_type, tag=v, vxz=eval(vxz)
                )
                if self.pyfile:
                    with open(self.filename, "a") as file_handle:
                        file_handle.write("# create transformation {}\n".format(v))
                        file_handle.write(geom_tranfs_str)

                else:
                    eval(geom_tranfs_str)

            # store to global list
            self.model_command_list.append(geom_tranfs_str)

    def _write_op_model(self):
        """
        Private function to instantiate the OpenSees model
        space. If pyfile flagged as True, this function writes the instantiating commands e.g. ops.model() to the
        output py file.

        .. note:
            For 3-D model, the default model dimension and node degree-of-freedoms are 3 and 6 respectively.
            This method automatically sets the aforementioned parameters to 2 and 4 respectively, for a 2-D problem.
        """
        wipe_str = "ops.wipe()\n"
        model_str = "ops.model('basic', '-ndm', {ndm}, '-ndf', {ndf})\n".format(
            ndm=self.__ndm, ndf=self.__ndf
        )
        # check if write or eval command
        if self.pyfile:
            with open(self.filename, "a") as file_handle:
                file_handle.write(wipe_str)
                file_handle.write(model_str)
        else:
            eval(wipe_str)
            eval(model_str)
            self.model_command_list.append(wipe_str)
            self.model_command_list.append(model_str)
            # ops.wipe()
            # ops.model("basic", "-ndm", self.__ndm, "-ndf", self.__ndf)

    def _write_op_node(self, mesh_obj):
        """
        Private function to write or execute the ops.node command to
        create nodes in OpenSees model space. If pyfile is flagged true, writes the ops.nodes() command to py file
        instead.

        """
        # check if write mode, write header for node commands
        if self.pyfile:
            with open(self.filename, "a") as file_handle:
                file_handle.write("# Model nodes\n")

        # loop all node in dict, write or eval node command
        for (
            k,
            nested_v,
        ) in mesh_obj.node_spec.items():
            coordinate = nested_v["coordinate"]
            node_str = "ops.node({tag}, {x:.4f}, {y:.4f}, {z:.4f})\n".format(
                tag=nested_v["tag"],
                x=coordinate[0],
                y=coordinate[1],
                z=coordinate[2],
            )
            if self.pyfile:
                with open(self.filename, "a") as file_handle:
                    file_handle.write(node_str)
            else:  # indices correspondence . 0 - x , 1 - y, 2 - z
                eval(node_str)
                self.model_command_list.append(node_str)

    def _write_op_fix(self, mesh_obj):
        """
        Private function to write the ops.fix() command for
        boundary condition definition in the grillage model. If pyfile is flagged true, writes
        the ops.fix() command to py file instead.

        """
        if self.pyfile:
            with open(self.filename, "a") as file_handle:
                file_handle.write("# Boundary condition implementation\n")
            # TODO generalize for user input of boundary condition
        for node_tag, edge_group_num in mesh_obj.edge_node_recorder.items():
            # if node is an edge beam - is part of common group z ==0 ,do not assign any fixity
            if (
                mesh_obj.node_spec[node_tag]["z_group"]
                in mesh_obj.common_z_group_element[0]
            ):  # here [0] is first group
                pass  # move to next node in edge recorder
            else:
                fix_str = "ops.fix({}, *{})\n".format(
                    node_tag, self.edge_support_type_dict[edge_group_num]
                )
                if self.pyfile:  # if writing py file
                    with open(self.filename, "a") as file_handle:
                        file_handle.write(fix_str)
                else:  # run instance
                    eval(fix_str)
                    self.model_command_list.append(fix_str)

    def _write_equal_dof(self, node_tag_list, dof: list = None):
        """
        Function to write equalDOF command
        """
        if dof is None:
            dof = [1, 2, 3, 4, 5]  # default

        # key is supported node , slave is non supported node
        for master_node, slave_node in node_tag_list:
            equaldof_str = "ops.equalDOF({rNodetag},{cNodetag},*{dofs})\n".format(
                rNodetag=master_node, cNodetag=slave_node, dofs=dof
            )

            if self.pyfile:
                with open(self.filename, "a") as file_handle:
                    file_handle.write(equaldof_str)
            else:
                eval(equaldof_str)
                self.model_command_list.append(equaldof_str)

    def _write_material(
        self, member: GrillageMember = None, material: Material = None
    ) -> int:
        """
        Private function to write Material command of the model class.
        """

        material_obj = None
        # check if material input is valid,
        if member is None and material is None:
            raise Exception(
                "Uniaxial material has no input GrillageMember or Material Object"
            )
        elif member is None:
            # This is for the option of updating preivously defined material commands
            material_obj = material
        elif material is None:
            material_obj = member.material
            if not member.material_command_flag:
                return 1  # placeholder num, no material command is written/executed
        # access member class object's material - get the material arguments and command
        (
            material_type,
            op_mat_arg,
        ) = member.material.get_material_args()  # get the material arguments

        # - write unique material tag and input argument to store as key for dict
        material_str = [
            material_type,
            op_mat_arg,
        ]  # repr both variables as a list for keyword definition
        # if section is specified, get the materialtagcounter for material() assignment
        # if not bool(self.material_dict):
        #     lastmaterialtag = 0  # if dict empty, start counter at 1
        # else:  # set materialtagcounter as the latest defined element - i.e. max of section_dict
        #     lastmaterialtag = self.material_dict[list(self.material_dict)[-1]]
        lastmaterialtag = self._get_material_tag()

        material_tag = self.material_dict.setdefault(
            repr(material_str), lastmaterialtag + 1
        )  # set key for material
        # check if the material_tag is a previously assigned key, if not, append to materal_command_list variable
        if material_tag != lastmaterialtag:
            mat_str = member.material.get_ops_material_command(
                material_tag=material_tag
            )
            self.material_command_list.append(mat_str)
        else:  # material tag defined, skip, print to terminal
            if self.diagnostics:
                print(
                    "Material {} with tag {} has been previously defined".format(
                        material_type, material_tag
                    )
                )
        return material_tag

    def _get_material_tag(self):
        if not bool(self.material_dict):
            lastmaterialtag = 0  # if dict empty, start counter at 1
        else:  # set materialtagcounter as the latest defined element - i.e. max of section_dict
            lastmaterialtag = self.material_dict[list(self.material_dict)[-1]]
        return lastmaterialtag

    def _write_section(self, grillage_member_obj: GrillageMember) -> int:
        """
        Private function to write section() command for the elements.

        """
        # checks if grillage member's element type requires the generation of ops.section()
        if not grillage_member_obj.section_command_flag:
            return 1  # return a placeholder num, no section is written
        # extract section variables from Section class
        section_type = grillage_member_obj.section  # get section type
        section_arg = grillage_member_obj.get_section_arguments()  # get arguments
        section_str = [
            section_type,
            section_arg,
        ]  # repr both variables as a list for keyword definition
        # if section is specified, get the sectiontagcounter for section assignment
        if not bool(self.section_dict):
            lastsectioncounter = 0  # if dict empty, start counter at 0
        else:  # dict not empty, get default value as latest defined tag
            lastsectioncounter = self.section_dict[list(self.section_dict)[-1]]
        # set section tag or get section tag if already been assigned
        previously_defined_section = list(self.section_dict.values())
        sectiontagcounter = self.section_dict.setdefault(
            repr(section_str), lastsectioncounter + 1
        )

        if sectiontagcounter not in previously_defined_section:
            sec_str = grillage_member_obj.get_ops_section_command(
                section_tag=sectiontagcounter
            )
            self.section_command_list.append(sec_str)

            # print to terminal
            if self.diagnostics:
                print(
                    "Section {}, of tag {} created".format(
                        section_type, sectiontagcounter
                    )
                )
        else:
            if self.diagnostics:
                print(
                    "Section {} with tag {} has been previously defined".format(
                        section_type, sectiontagcounter
                    )
                )
        return sectiontagcounter

    def _create_standard_element_list(self):
        """
        Private method to populate common_grillage_element dict. This is the base class variant -concrete classes of
        grillage may have different elements

        Base class variant is beam grillage model.

        """

        # loop through base dict for grillage elements, sort members based on four groups (edge,ext_a,int,ext_b).
        for key, val in zip(
            self.common_grillage_element_keys[0 : self.long_member_index],
            sort_list_into_four_groups(self.Mesh_obj.model_plane_z_groups).values(),
        ):
            self.common_grillage_element_z_group.update({key: val})
        # populate start edge and end edge entries
        self.common_grillage_element_z_group[self.common_grillage_element_keys[4]] = [0]
        self.common_grillage_element_z_group[
            self.common_grillage_element_keys[5]
        ] = list(range(1, self.Mesh_obj.global_edge_count))
        self.common_grillage_element_z_group[self.common_grillage_element_keys[6]] = [
            0
        ]  # proxy 0 for set_member() loop
        self.common_grillage_element_z_group[
            self.common_grillage_element_keys[0] + "_1"
        ] = [
            self.common_grillage_element_z_group[self.common_grillage_element_keys[0]][
                0
            ]
        ]
        self.common_grillage_element_z_group[
            self.common_grillage_element_keys[0] + "_2"
        ] = [
            self.common_grillage_element_z_group[self.common_grillage_element_keys[0]][
                1
            ]
        ]

    def _write_rigid_link(self):
        """
        Private procedure to write or execute OpenSeesPy rigidLink() command. Reads rigid link data from link_str_list
        variable

        """
        # loop all rigidLink command, write or eval rigid link command. note link_str is already formatted
        for link_str in self.Mesh_obj.link_str_list:
            if self.pyfile:
                with open(self.filename, "a") as file_handle:
                    file_handle.write(link_str)
            else:
                eval(link_str)

    # interface function
    def set_member(
        self,
        grillage_member_obj: GrillageMember,
        member=None,
        specific_group=None,
        specific_span=None,
    ):
        """
        Function to set grillage member class object to elements of grillage members.

        :param grillage_member_obj: `GrillageMember` class object
        :type grillage_member_obj: GrillageMember
        :param member: str of member category - see below table for the available name strings
        :type member: str


         =====================================    ======================================
         Standard grillage elements name str      Description
         =====================================    ======================================
          edge_beam                               Elements along x axis at top and bottom edges of mesh (z = 0, z = width)
          exterior_main_beam_1                    Elements along first grid line after bottom edge (z = 0)
          interior_main_beam                      For all elements in x direction between grid lines of exterior_main_beam_1 and exterior_main_beam_2
          exterior_main_beam_1                    Elements along first grid line after top edge (z = width)
          start_edge                     	      Elements along z axis where longitudinal grid line x = 0
          end_edge                                Elements along z axis where longitudinal grid line x = Length
          transverse_slab                         For all elements in transverse direction between start_edge and end_edge
         =====================================    ======================================


        :raises: ValueError If missing argument for member=
        """
        if self.diagnostics:
            print("Setting member: {} of model".format(member))
        if member is None:
            raise ValueError(
                "Missing target elements of grillage model to be assigned. Hint, member="
            )
        specific_group_list = []
        if not isinstance(specific_group, list):
            specific_group_list = [specific_group]
        # check and write member's section command
        section_tag = self._write_section(grillage_member_obj)
        # check and write member's material command
        material_tag = self._write_material(member=grillage_member_obj)
        # dictionary for key = common member tag, val is list of str for ops.element()
        ele_command_dict = dict()
        ele_group_to_command_dict = dict()
        ele_tag_to_command_dict = dict()
        ele_command_list = []
        # if option for pyfile is True, write the header for element group commands
        if self.pyfile:
            with open(self.filename, "a") as file_handle:
                file_handle.write(
                    "# Element generation for member: {}\n".format(member)
                )
        # lookup member grouping
        # z_flag, x_flag, edge_flag, common_member_tag = self._create_standard_element_list(namestring=member)

        ele_width = 1  # set default ele width 1
        # if member properties is based on unit width (e.g. slab elements), get width of element and assign properties
        if grillage_member_obj.section.unit_width:
            if member == self.common_grillage_element_keys[-1]:
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
                            ele_width_record.append(
                                np.sqrt(
                                    lis[0][0] ** 2 + lis[0][1] ** 2 + lis[0][2] ** 2
                                )
                                / 2
                            )
                        elif len(lis) >= 2:
                            ele_width_record.append(
                                (
                                    np.sqrt(
                                        lis[0][0] ** 2 + lis[0][1] ** 2 + lis[0][2] ** 2
                                    )
                                    + np.sqrt(
                                        lis[1][0] ** 2 + lis[1][1] ** 2 + lis[1][2] ** 2
                                    )
                                )
                                / 2
                            )
                        else:
                            #
                            break  # has assigned element, continue to next check
                    ele_width = np.mean(
                        ele_width_record
                    )  # if node lies between a triangular and quadrilateral grid, get mean between
                    # both width
                    # here take the average width in x directions
                    ele_str = grillage_member_obj.get_element_command_str(
                        ele_tag=ele[0],
                        node_tag_list=node_tag_list,
                        transf_tag=ele[4],
                        ele_width=ele_width,
                        materialtag=material_tag,
                        sectiontag=section_tag,
                    )
                    ele_command_list.append(ele_str)
                    ele_tag_to_command_dict[ele[0]] = ele_str

            elif member == "start_edge" or member == "end_edge":
                for edge_group in self.common_grillage_element_z_group[member]:
                    for edge_ele in self.Mesh_obj.edge_group_to_ele[edge_group]:
                        edge_ele_width = 0.5  # nominal half -m width
                        node_tag_list = [edge_ele[1], edge_ele[2]]
                        ele_str = grillage_member_obj.get_element_command_str(
                            ele_tag=edge_ele[0],
                            node_tag_list=node_tag_list,
                            transf_tag=edge_ele[4],
                            ele_width=edge_ele_width,
                            materialtag=material_tag,
                            sectiontag=section_tag,
                        )
                        ele_command_list.append(ele_str)
                        ele_tag_to_command_dict[edge_ele[0]] = ele_str

            ele_group_to_command_dict[0] = ele_command_list
        else:  # non-unit width member assignment
            if member == self.common_grillage_element_keys[-1]:
                ele_list = self.Mesh_obj.trans_ele

                if specific_span:  # filter for specific span elements only
                    ele_list = [
                        ele
                        for ele in ele_list
                        if ele[0] in self.Mesh_obj.span_group_to_ele_tag[specific_span]
                    ]

                ele_command_list += self._get_element_command_list(
                    grillage_member_obj=grillage_member_obj,
                    list_of_ele=ele_list,
                    material_tag=material_tag,
                    section_tag=section_tag,
                )
                ele_group_to_command_dict[0] = ele_command_list

                for nth, ele in enumerate(ele_list):
                    ele_tag_to_command_dict[ele[0]] = ele_command_list[nth]
                ele_command_list = []
            else:
                for z_group in self.common_grillage_element_z_group[member]:
                    # if specific group is specified, assign grillage member to specific groups only
                    if specific_group and z_group in specific_group_list:
                        continue  # go to next group

                    elif member == "start_edge" or member == "end_edge":
                        ele_list = self.Mesh_obj.edge_group_to_ele[
                            z_group
                        ]  # here z group represents the edge group instead

                    elif member == self.common_grillage_element_keys[-2]:
                        ele_list = self.Mesh_obj.connect_ele

                    else:
                        ele_list = self.Mesh_obj.z_group_to_ele[z_group]

                    if isinstance(
                        specific_span, int
                    ):  # filter for specific span elements only
                        ele_list = [
                            ele
                            for ele in ele_list
                            if ele[0]
                            in self.Mesh_obj.span_group_to_ele_tag[specific_span]
                        ]

                    ele_command_list += self._get_element_command_list(
                        grillage_member_obj=grillage_member_obj,
                        list_of_ele=ele_list,
                        material_tag=material_tag,
                        section_tag=section_tag,
                    )

                    ele_group_to_command_dict[z_group] = ele_command_list

                    for nth, ele in enumerate(ele_list):
                        ele_tag_to_command_dict[ele[0]] = ele_command_list[nth]

                    ele_command_list = []

        self.element_command_list.update(ele_tag_to_command_dict)

    def set_spring_support(
        self, rotational_spring_stiffness, edge_num=0, spring_direction=6
    ):
        """
        Sets a spring support value of rotational_spring_stiffness to all nodes of edge number.
        """
        if edge_num in self.spring_edges:
            raise Exception(
                "Spring support already defined for edge number {}".format(edge_num)
            )
        else:
            self.spring_edges.append(edge_num)

        e_tangent = rotational_spring_stiffness
        # create spring material obj in workspace and store to global material list
        spring_material = create_material(ops_mat_type="Elastic", E=e_tangent)
        spring_name = "spring"  # spring correspond to rotational

        # create section and GrillageMember object for spring (zerolength) element
        spring_section = create_section(op_ele_type="zeroLength")
        spring_member = create_member(section=spring_section, material=spring_material)

        # write material obj in workspace to class
        material_tag = self._write_material(member=spring_member)

        # Find all the nodes /node number for the current edge num
        node_tag_list = [
            key
            for key, val in self.Mesh_obj.edge_node_recorder.items()
            if val == edge_num
        ]
        new_node_list = []
        ele_command_dict = {}
        ele_command_dict[spring_name] = []  # init empty list
        ele_command_list = ele_command_dict[spring_name]
        edge_node_dict = {}
        ele_tag_to_command_dict = dict()
        for node_tag in node_tag_list:
            # get node coordinate
            node_coord = self.Mesh_obj.node_spec[node_tag]["coordinate"]
            x_group = self.Mesh_obj.node_spec[node_tag]["x_group"]
            z_group = self.Mesh_obj.node_spec[node_tag]["z_group"]
            # create new node tag after last node tag in node_spec +=1
            node_counter = list(self.Mesh_obj.node_spec.keys())[-1] + 1
            # create a second node with the same coordinate x y z - new label # add to node spec
            self.Mesh_obj.node_spec.setdefault(
                node_counter,
                {
                    "tag": node_counter,
                    "coordinate": node_coord,
                    "x_group": x_group,
                    "z_group": z_group,
                },
            )
            # store new node information
            new_node_list.append(node_counter)
            edge_node_dict[node_counter] = edge_num
            # create element between the node and newly defined node
            ele_count = self.global_ele_counter
            nodes = [node_counter, node_tag]
            ele_command_list.append(
                spring_member.get_element_command_str(
                    ele_tag=ele_count,
                    node_tag_list=nodes,
                    materialtag=material_tag,
                )
            )

            ele_tag_to_command_dict[ele_count] = spring_member.get_element_command_str(
                ele_tag=ele_count,
                node_tag_list=nodes,
                materialtag=material_tag,
            )
            self.global_ele_counter += 1
            # removes boundary condition on nodes of node_list
            del self.Mesh_obj.edge_node_recorder[node_tag]
            # create master/slave link between both node_tag (non support), to node_counter (supported)
            self.spring_node_pairs[node_counter] = node_tag

        # replace constrain onto constrains of node in node_list to new node
        self.Mesh_obj.edge_node_recorder.update(edge_node_dict)

        self.element_command_list.update(ele_tag_to_command_dict)

    # sub-functions of set_member function
    @staticmethod
    def _get_element_command_list(
        grillage_member_obj, list_of_ele, material_tag, section_tag
    ):
        """
        Private unction to get list of element command string
        :param grillage_member_obj:
        :param list_of_ele:
        :param material_tag:
        :param section_tag:
        :return: list of string consisting element() commands for creating elements
        """
        ele_command_list = []
        for ele in list_of_ele:
            n1 = ele[1]  # node i
            n2 = ele[2]  # node j
            node_tag_list = [n1, n2]
            ele_width = 1
            ele_str = grillage_member_obj.get_element_command_str(
                ele_tag=ele[0],
                node_tag_list=node_tag_list,
                transf_tag=ele[4],
                ele_width=ele_width,
                materialtag=material_tag,
                sectiontag=section_tag,
            )
            ele_command_list.append(ele_str)
        return ele_command_list

    # interface function
    def set_material(self, material_obj):
        """
        Function to define a global material model. This function proceeds to write write the material() command to
        output file. By default, function is only called and handled within set_member function. When called by user,
        function creates a material object instance to be set for the OpenSees instance.

        .. note::
            Currently, function does not have overwriting feature yet.
        """
        # set material to global material object
        self.global_mat_object = material_obj  # material matrix for

        # write uniaxialMaterial() command to output file
        self._write_material(material=material_obj)

    # ---------------------------------------------------------------
    # Functions to query nodes or grids correspond to a point or line + distributing
    # loads to grillage nodes. These are not accessible part of API

    # private procedure to find elements within a grid
    def _get_elements(self, node_tag_combo):
        # abstracted procedure to find and return the long and trans elements within a grid of 4 or 3 nodes
        record_long = []
        record_trans = []
        record_edge = []
        for combi in node_tag_combo:
            long_mem_index = [
                i
                for i, x in enumerate(
                    [
                        combi[0] in n[1:3] and combi[1] in n[1:3]
                        for n in self.Mesh_obj.long_ele
                    ]
                )
                if x
            ]
            trans_mem_index = [
                i
                for i, x in enumerate(
                    [
                        combi[0] in n[1:3] and combi[1] in n[1:3]
                        for n in self.Mesh_obj.trans_ele
                    ]
                )
                if x
            ]
            edge_mem_index = [
                i
                for i, x in enumerate(
                    [
                        combi[0] in n[1:3] and combi[1] in n[1:3]
                        for n in self.Mesh_obj.edge_span_ele
                    ]
                )
                if x
            ]
            record_long = record_long + long_mem_index  # record
            record_trans = record_trans + trans_mem_index  # record
            record_edge = record_edge + edge_mem_index
        return record_long, record_trans, record_edge

    # Getter for Points Loads nodes
    def _get_point_load_nodes(self, point):
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
                coord = self.Mesh_obj.node_spec[node_tag]["coordinate"]
                coord_point = Point(coord[0], coord[1], coord[2])
                point_list.append(coord_point)
            if check_point_in_grid(loading_point, point_list):
                node_list = point_list
                grid = grid_tag

        node_list = self.Mesh_obj.grid_number_dict.get(grid, None)
        return node_list, grid  # grid = grid number

    # Getter for Line loads nodes
    def _get_line_load_nodes(self, line_load_obj=None, list_of_load_vertices=None):
        # from starting point of line load
        # initiate variables
        next_grid = []
        x = 0
        z = 0
        x_start = []
        z_start = []
        colinear_spec = (
            []
        )  # list storing coordinates *sublist of element coinciding points
        # colinear_spec has the following properties: key (ele number), [point1, point2]
        intersect_spec = (
            dict()
        )  # a sub dict for characterizing the line segment's intersecting points within grid
        grid_inter_points = []
        # process inputs
        if line_load_obj is None and list_of_load_vertices is not None:
            start_load_vertex = list_of_load_vertices[0]  # first point is start point
            end_load_vertex = list_of_load_vertices[1]  # second point is end point
        elif line_load_obj is not None and list_of_load_vertices is None:
            start_load_vertex = line_load_obj.load_point_1
            end_load_vertex = line_load_obj.line_end_point
        else:
            raise Exception(
                "Error is defining points of line/patch on grillage: hint check load points vertices of "
                "load obj"
            )
        # sub_dict has the following keys:
        # {bound: , long_intersect: , trans_intersect, edge_intersect, ends:}
        # find grids where start point of line load lies in
        start_nd, start_grid = self._get_point_load_nodes(start_load_vertex)
        last_nd, last_grid = self._get_point_load_nodes(end_load_vertex)

        line_grid_intersect = dict()
        # loop each grid check if line segment lies in grid
        for grid_tag, grid_nodes in self.Mesh_obj.grid_number_dict.items():
            point_list = []
            # get coordinates of all nodes in grid
            for node_tag in grid_nodes:
                coord = self.Mesh_obj.node_spec[node_tag]["coordinate"]
                coord_point = Point(coord[0], coord[1], coord[2])
                point_list.append(coord_point)
            # get long, trans and edge elements in the grids. This is for searching intersection later on
            element_combi = combinations(grid_nodes, 2)
            long_ele_index, trans_ele_index, edge_ele_index = self._get_elements(
                element_combi
            )

            (
                Rz,
                Rx,
                Redge,
                R_z_col,
                R_x_col,
                R_edge_col,
            ) = self._get_intersecting_elements(
                grid_tag,
                start_grid,
                last_grid,
                start_load_vertex,
                end_load_vertex,
                long_ele_index,
                trans_ele_index,
                edge_ele_index,
            )
            # if colinear, assign to colinear_spec
            if any([R_z_col, R_x_col, R_edge_col]):
                if R_z_col:
                    colinear_spec += R_z_col
                if R_x_col:
                    colinear_spec += R_x_col
                if R_edge_col:
                    colinear_spec += R_edge_col
            # if no intersection, continue to next grid
            elif Rz == [] and Rx == [] and Redge == []:
                continue

            else:  # intersection point exist, record to intersect_spec and set to dict
                intersect_spec.setdefault("long_intersect", Rz)
                intersect_spec.setdefault("trans_intersect", Rx)
                #
                intersect_spec.setdefault("edge_intersect", Redge)
                grid_inter_points += Rz + Rx + Redge
                # check if point is not double assigned

                line_grid_intersect.setdefault(grid_tag, intersect_spec)
                intersect_spec = dict()

        # update line_grid_intersect by removing grids if line coincide with elements and multiple grids of vicinity
        # grids are returned with same values
        removed_key = []
        edited_dict = line_grid_intersect.copy()
        # if line does not intersect any grid, overwrite edited_dict
        if not edited_dict:
            for key in self.Mesh_obj.grid_number_dict.keys():
                edited_dict.setdefault(
                    key,
                    {"long_intersect": [], "trans_intersect": [], "edge_intersect": []},
                )

        # update line_grid_intersect adding start and end points of line segment to the dict within grid key
        for grid_key, int_list in edited_dict.items():
            point_tuple_list = []
            int_list.setdefault("ends", [])  # set the key pair to empty list
            for node_tag in self.Mesh_obj.grid_number_dict[grid_key]:
                coord = self.Mesh_obj.node_spec[node_tag]["coordinate"]
                coord_point = Point(coord[0], coord[1], coord[2])
                point_tuple_list.append(coord_point)

            if check_point_in_grid(start_load_vertex, point_tuple_list):
                # int_list.setdefault("ends", [[line_load_obj.load_point_1.x, line_load_obj.load_point_1.y,
                #       line_load_obj.load_point_1.z]])
                int_list["ends"].append(
                    [start_load_vertex.x, start_load_vertex.y, start_load_vertex.z]
                )

            if check_point_in_grid(end_load_vertex, point_tuple_list):
                # int_list.setdefault("ends", [[line_load_obj.line_end_point.x, line_load_obj.line_end_point.y,
                #                  line_load_obj.line_end_point.z]])
                int_list["ends"].append(
                    [end_load_vertex.x, end_load_vertex.y, end_load_vertex.z]
                )
            else:
                int_list.setdefault("ends", [])
        # loop to remove empty entries
        for grid_key, int_list in list(edited_dict.items()):
            if all([val == [] for val in int_list.values()]):
                del edited_dict[grid_key]

        # last check to remove duplicate grids due to having colinear conditions
        # i.e. where two vicinity grids with same intersection points are stored in edited_dict

        for grid_key, int_list in line_grid_intersect.items():
            if grid_key not in removed_key:
                check_dup_list = [
                    int_list == val for val in line_grid_intersect.values()
                ]
                # if there are duplicates check_dup_list will be greater than 1,
                # another case to remove if
                if sum(check_dup_list) > 1:
                    # check if grid key is a vicinity grid of current grid_key
                    for dup_key in [
                        key
                        for (count, key) in enumerate(line_grid_intersect.keys())
                        if check_dup_list[count] and key is not grid_key
                    ]:
                        if dup_key in [start_grid, last_grid]:
                            continue
                        elif (
                            dup_key
                            in self.Mesh_obj.grid_vicinity_dict[grid_key].values()
                        ):
                            removed_key.append(dup_key)
                            del edited_dict[dup_key]

        return edited_dict, colinear_spec

    # private function to find intersection points of line/patch edge within grid
    def _get_intersecting_elements(
        self,
        current_grid,
        line_start_grid,
        line_end_grid,
        start_point,
        end_point,
        long_ele_index,
        trans_ele_index,
        edge_ele_index,
    ):
        # instantiate variables
        R_z = (
            []
        )  # variables with _ are elements of the main variable without _ i.e. R_z is an element of Rz
        Rz = []
        R_x = []
        Rx = []
        R_edge = []
        Redge = []
        R_x_col = []
        R_z_col = []
        R_edge_col = []
        # get line segment - p_1 and p_2 correspond to start and end point of line
        p_1 = start_point  # start point of line
        p_2 = end_point
        # get line equation for checking intersections
        L2 = line([p_1.x, p_1.z], [p_2.x, p_2.z])
        # loop through long elements in grid, find intersection points
        for long_ele in [self.Mesh_obj.long_ele[i] for i in long_ele_index]:
            pz1 = self.Mesh_obj.node_spec[long_ele[1]]["coordinate"]  # point z 1
            pz2 = self.Mesh_obj.node_spec[long_ele[2]]["coordinate"]  # point z 2
            pz1 = Point(pz1[0], pz1[1], pz1[2])  # convert to point namedtuple
            pz2 = Point(pz2[0], pz2[1], pz2[2])  # convert to point namedtuple
            # get the line segment within the grid. Line segment defined by two points assume model plane = 0 [x_1, z_1
            # ], and [x_2, z_2]

            # if neither special case, check intersection
            intersect_z, colinear_z = check_intersect(pz1, pz2, p_1, p_2)
            if colinear_z and intersect_z:
                # if colinear, find the colinear points
                first = is_between(p_1, pz1, p_2)
                second = is_between(p_1, pz2, p_2)
                if first and second:
                    R_z_col.append([long_ele[0], pz1, pz2])
                elif first:  # second point not in between
                    if is_between(pz1, p_2, pz2):
                        R_z_col.append([long_ele[0], pz1, p_2])
                    else:
                        R_z_col.append([long_ele[0], pz1, p_1])
                elif second:  # second only
                    if is_between(pz1, p_1, pz2):
                        R_z_col.append([long_ele[0], p_1, pz2])
                    else:
                        R_z_col.append([long_ele[0], p_2, pz2])

            elif intersect_z:
                L1 = line([pz1.x, pz1.z], [pz2.x, pz2.z])
                R_z = intersection(L1, L2)
                Rz.append([R_z[0], pz1.y, R_z[1]])
        # loop through trans elements in grid, find intersection points
        for trans_ele in [self.Mesh_obj.trans_ele[i] for i in trans_ele_index]:
            px1 = self.Mesh_obj.node_spec[trans_ele[1]]["coordinate"]  # point z 1
            px2 = self.Mesh_obj.node_spec[trans_ele[2]]["coordinate"]  # point z 2
            px1 = Point(px1[0], px1[1], px1[2])  # convert to point namedtuple
            px2 = Point(px2[0], px2[1], px2[2])  # convert to point namedtuple

            # check potential for intersection or co linear condition
            intersect_x, colinear_x = check_intersect(px1, px2, p_1, p_2)
            if colinear_x and intersect_x:
                first = is_between(p_1, px1, p_2)
                second = is_between(p_1, px2, p_2)
                if first and second:
                    R_z_col.append([trans_ele[0], px1, px2])
                elif first:  # second point not in between
                    if is_between(px1, p_2, px2):
                        R_z_col.append([trans_ele[0], px1, p_2])
                    else:
                        R_z_col.append([trans_ele[0], px1, p_1])
                elif second:  # second only
                    if is_between(px1, p_1, px2):
                        R_z_col.append([trans_ele[0], p_1, px2])
                    else:
                        R_z_col.append([trans_ele[0], p_2, px2])

            elif intersect_x:
                L1 = line([px1.x, px1.z], [px2.x, px2.z])
                R_x = intersection(L1, L2)
                Rx.append([R_x[0], px1.y, R_x[1]])

        # loop through edge elements in grid, find intersection points
        for edge_ele in [self.Mesh_obj.edge_span_ele[i] for i in edge_ele_index]:
            p_edge_1 = self.Mesh_obj.node_spec[edge_ele[1]]["coordinate"]  # point z 1
            p_edge_2 = self.Mesh_obj.node_spec[edge_ele[2]]["coordinate"]  # point z 2
            p_edge_1 = Point(
                p_edge_1[0], p_edge_1[1], p_edge_1[2]
            )  # convert to point namedtuple
            p_edge_2 = Point(
                p_edge_2[0], p_edge_2[1], p_edge_2[2]
            )  # convert to point namedtuple

            intersect_edge, colinear_edge = check_intersect(
                p_edge_1, p_edge_2, p_1, p_2
            )
            if colinear_edge and intersect_edge:
                first = is_between(p_1, p_edge_1, p_2)
                second = is_between(p_1, p_edge_2, p_2)
                if first and second:
                    R_z_col.append([edge_ele[0], p_edge_1, p_edge_2])
                elif first:  # second point not in between
                    if is_between(p_edge_1, p_2, p_edge_2):
                        R_z_col.append([edge_ele[0], p_edge_1, p_2])
                    else:
                        R_z_col.append([edge_ele[0], p_edge_1, p_1])
                elif second:  # second only
                    if is_between(p_edge_1, p_1, p_edge_2):
                        R_z_col.append([edge_ele[0], p_1, p_edge_2])
                    else:
                        R_z_col.append([edge_ele[0], p_2, p_edge_2])

            elif intersect_edge:
                L1 = line([p_edge_1.x, p_edge_1.z], [p_edge_2.x, p_edge_2.z])
                R_edge = intersection(L1, L2)  # temporary R_edge variable
                Redge.append(
                    [R_edge[0], p_edge_1.y, R_edge[1]]
                )  # Redge variable to be returned - as list
        return Rz, Rx, Redge, R_z_col, R_x_col, R_edge_col

    # Getter for Patch loads
    def _get_bounded_nodes(self, patch_load_obj):
        # function to return nodes bounded by patch load
        point_list = [
            patch_load_obj.load_point_1,
            patch_load_obj.load_point_2,
            patch_load_obj.load_point_3,
            patch_load_obj.load_point_4,
        ]
        bounded_node = []
        bounded_grids = []
        for node_tag, node_spec in self.Mesh_obj.node_spec.items():
            coordinate = node_spec["coordinate"]
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
    def _assign_point_to_four_node(self, point, mag, shape_func="linear"):
        node_mx = []
        node_mz = []
        # search grid where the point lies in
        grid_nodes, _ = self._get_point_load_nodes(point=point)
        if grid_nodes is None:
            load_str = []
            return load_str
        # if corner or edge grid with 3 nodes, run specific assignment for triangular grids
        # extract coordinates
        p1 = self.Mesh_obj.node_spec[grid_nodes[0]]["coordinate"]
        p2 = self.Mesh_obj.node_spec[grid_nodes[1]]["coordinate"]
        p3 = self.Mesh_obj.node_spec[grid_nodes[2]]["coordinate"]

        point_list = [
            Point(p1[0], p1[1], p1[2]),
            Point(p2[0], p2[1], p2[2]),
            Point(p3[0], p3[1], p3[2]),
        ]
        if len(grid_nodes) == 3:
            sorted_list, sorted_node_tag = sort_vertices(point_list, grid_nodes)
            Nv = ShapeFunction.linear_triangular(
                x=point[0],
                z=point[2],
                x1=sorted_list[0].x,
                z1=sorted_list[0].z,
                x2=sorted_list[1].x,
                z2=sorted_list[1].z,
                x3=sorted_list[2].x,
                z3=sorted_list[2].z,
            )
            node_load = [mag * n for n in Nv]
            node_mx = np.zeros(len(node_load))
            node_mz = np.zeros(len(node_load))
        else:  # else run assignment for quadrilateral grids
            # extract coordinates of fourth point
            p4 = self.Mesh_obj.node_spec[grid_nodes[3]]["coordinate"]
            point_list.append(Point(p4[0], p4[1], p4[2]))
            sorted_list, sorted_node_tag = sort_vertices(point_list, grid_nodes)
            # mapping coordinates to natural coordinate, then finds eta (x) and zeta (z) of the point xp,zp
            eta, zeta = solve_zeta_eta(
                xp=point[0],
                zp=point[2],
                x1=sorted_list[0].x,
                z1=sorted_list[0].z,
                x2=sorted_list[1].x,
                z2=sorted_list[1].z,
                x3=sorted_list[2].x,
                z3=sorted_list[2].z,
                x4=sorted_list[3].x,
                z4=sorted_list[3].z,
            )

            # access shape function of line load
            if shape_func == "hermite":
                Nv, Nmx, Nmz = ShapeFunction.hermite_shape_function_2d(eta, zeta)
                node_mx = [mag * n for n in Nmx]
                # Mz
                node_mz = [mag * n for n in Nmz]
            else:  # linear shaep function
                Nv = ShapeFunction.linear_shape_function(eta, zeta)
            # Nv, Nmx, Nmz = ShapeFunction.hermite_shape_function_2d(eta, zeta)
            # Fy
            node_load = [mag * n for n in Nv]

        load_str = []
        if shape_func == "hermite":
            for count, node in enumerate(sorted_node_tag):
                load_str.append(
                    "ops.load({pt}, *{val})\n".format(
                        pt=node,
                        val=[0, node_load[count], 0, node_mx[count], 0, node_mz[count]],
                    )
                )
        else:
            for count, node in enumerate(sorted_node_tag):
                load_str.append(
                    "ops.load({pt}, *{val})\n".format(
                        pt=node, val=[0, node_load[count], 0, 0, 0, 0]
                    )
                )
        return load_str

    # Setter for Line loads and above
    def _assign_line_to_four_node(
        self, line_load_obj, line_grid_intersect, line_ele_colinear
    ) -> list:
        # Function to assign line load to mesh. Procedure to assign line load is as follows:
        # . get properties of line on the grid
        # . convert line load to equivalent point load
        # . Find position of equivalent point load
        # . Runs assignment for point loads function (assign_point_to_four_node) using equivalent point load

        # loop each grid
        load_str_line = []
        for grid, points in line_grid_intersect.items():
            if (
                "ends" not in points.keys()
            ):  # hard code fix to solve colinear problems - see API notes
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
                continue

            # get length of line
            L = np.sqrt((p1[0] - p2[0]) ** 2 + (p1[2] - p2[2]) ** 2)

            # get magnitudes at point 1 and point 2
            w1 = line_load_obj.interpolate_udl_magnitude([p1[0], 0, p1[1]])
            w2 = line_load_obj.interpolate_udl_magnitude([p2[0], 0, p2[1]])

            W = (w1 + w2) / 2
            # get mid point of line
            x_bar = ((2 * w1 + w2) / (w1 + w2)) * L / 3  # from p2
            load_point = line_load_obj.get_point_given_distance(
                xbar=x_bar, point_coordinate=[p2[0], self.y_elevation, p2[2]]
            )

            # uses point load assignment function to assign load point and mag to four nodes in grid
            load_str = self._assign_point_to_four_node(
                point=load_point, mag=W, shape_func=line_load_obj.shape_function
            )
            load_str_line += load_str  # append to major list for line load

        # loop through all colinear elements
        # for each colinear element, assign line load to two nodes of element

        assigned_ele = []
        for ele in line_ele_colinear:
            if ele[0] not in assigned_ele:
                p1 = ele[1]
                p2 = ele[2]
                # get magnitudes at point 1 and point 2
                L = get_distance(p1, p2)
                w1 = line_load_obj.interpolate_udl_magnitude([p1.x, p1.y, p1.z])
                w2 = line_load_obj.interpolate_udl_magnitude([p2.x, p2.y, p2.z])
                W = (w1 + w2) / 2
                mag = W * L
                # mag = W
                # get mid point of line
                x_bar = ((2 * w1 + w2) / (w1 + w2)) * L / 3  # from p2
                load_point = line_load_obj.get_point_given_distance(
                    xbar=x_bar, point_coordinate=[p2.x, p2.y, p2.z]
                )
                load_str = self._assign_point_to_four_node(point=load_point, mag=mag)
                load_str_line += load_str  # append to major list for line load
                assigned_ele.append(ele[0])
        return load_str_line

    def _assign_beam_ele_line_load(self, line_load_obj: LineLoading):
        load_str_line = []
        ele_group = []
        width_dict = None
        if line_load_obj.long_beam_ele_load_flag:
            ele_group = self.Mesh_obj.long_ele
            width_dict = self.Mesh_obj.node_width_z_dict
        elif line_load_obj.trans_beam_ele_load_flag:
            ele_group = self.Mesh_obj.trans_ele
            width_dict = self.Mesh_obj.node_width_x_dict
        for ele in ele_group:
            if ele[3] != 0:  # exclude edge beams
                p1 = ele[1]  # node tag i
                p2 = ele[2]  # node tag j
                # convert to point load tuple
                p1_list = self.Mesh_obj.node_spec[p1]["coordinate"]
                p2_list = self.Mesh_obj.node_spec[p2]["coordinate"]
                p1_point = create_point(x=p1_list[0], z=p1_list[2])
                p2_point = create_point(x=p2_list[0], z=p2_list[2])
                L = get_distance(
                    p1_point, p2_point
                )  # distance between two point tuples of ele
                w1 = line_load_obj.load_point_1.p  # magnitude at vertex 1
                w2 = line_load_obj.line_end_point.p  # magnitude at vertex 2
                d1 = np.sum(width_dict.get(p1))  # width of node j
                d2 = np.sum(width_dict.get(p2))  # width of node j
                d = (d1 + d2) / 2  # average width
                W = (w1 + w2) / 2  # average mag
                mag = W * L * d  # convert UDL (N/m2) to point load, q * Length * width
                # get mid point of line
                x_bar = ((2 * w1 + w2) / (w1 + w2)) * L / 3  # from p2
                load_point = line_load_obj.get_point_given_distance(
                    xbar=x_bar, point_coordinate=[p2_point.x, p2_point.y, p2_point.z]
                )
                load_str = self._assign_point_to_four_node(point=load_point, mag=mag)
                load_str_line += load_str  # append to major list for line load

        return load_str_line

    # setter for patch loads
    def _assign_patch_load(self, patch_load_obj: PatchLoading) -> list:
        # searches grid that encompass the patch load
        # use getter for line load, 4 times for each point
        # between 4 dictionaries record the common grids as having the corners of the patch - to be evaluated different
        bound_node, bound_grid = self._get_bounded_nodes(patch_load_obj)
        patch_load_str = []  # final return str list
        # assign patch for grids fully bounded by patch
        for grid in bound_grid:
            nodes = self.Mesh_obj.grid_number_dict[grid]  # read grid nodes
            # get p value of each node
            p_list = []
            for tag in nodes:
                coord = self.Mesh_obj.node_spec[tag]["coordinate"]
                p = patch_load_obj.patch_mag_interpolate(coord[0], coord[2])[
                    0
                ]  # object function returns array like
                p_list.append(LoadPoint(coord[0], coord[1], coord[2], p))
            # get centroid of patch on grid
            xc, yc, zc = get_patch_centroid(p_list)
            inside_point = Point(xc, yc, zc)
            # volume = area of base x average height
            A = self._get_node_area(inside_point=inside_point, p_list=p_list)
            # _, A = calculate_area_given_four_points(inside_point, p_list[0], p_list[1], p_list[2], p_list[3])
            mag = A * sum([point.p for point in p_list]) / len(p_list)
            # assign point and mag to 4 nodes of grid
            load_str = self._assign_point_to_four_node(
                point=[xc, yc, zc], mag=mag, shape_func=patch_load_obj.shape_function
            )
            patch_load_str += load_str
        # apply patch for full bound grids completed

        # search the intersecting grids using line load function
        intersect_grid_1, _ = self._get_line_load_nodes(
            list_of_load_vertices=[
                patch_load_obj.load_point_1,
                patch_load_obj.load_point_2,
            ]
        )
        intersect_grid_2, _ = self._get_line_load_nodes(
            list_of_load_vertices=[
                patch_load_obj.load_point_2,
                patch_load_obj.load_point_3,
            ]
        )
        intersect_grid_3, _ = self._get_line_load_nodes(
            list_of_load_vertices=[
                patch_load_obj.load_point_3,
                patch_load_obj.load_point_4,
            ]
        )
        intersect_grid_4, _ = self._get_line_load_nodes(
            list_of_load_vertices=[
                patch_load_obj.load_point_4,
                patch_load_obj.load_point_1,
            ]
        )
        # merging process of the intersect grid dicts
        merged = check_dict_same_keys(intersect_grid_1, intersect_grid_2)
        merged = check_dict_same_keys(merged, intersect_grid_3)
        merged = check_dict_same_keys(merged, intersect_grid_4)
        self.global_patch_int_dict.update(
            merged
        )  # save intersect grid dict to global dict

        # all lines are ordered in path counter clockwise - sorted hereafter via sort_vertices
        # get nodes in grid that are left (check inside variable greater than 0)
        for grid, int_point_list in merged.items():  # [x y z]
            grid_nodes = self.Mesh_obj.grid_number_dict[grid]  # read grid nodes
            # get two grid nodes bounded by patch
            node_in_grid = [
                x
                for x, y in zip(grid_nodes, [node in bound_node for node in grid_nodes])
                if y
            ]
            node_list = int_point_list  # sort
            p_list = []
            # loop each int points - add extract coordinates, get patch magnitude using interpolation ,
            # convert coordinate to namedtuple Loadpoint and append to point list p_list
            for int_list in int_point_list.values():
                for int_point in int_list:  # [x y z]
                    p = (
                        patch_load_obj.patch_mag_interpolate(int_point[0], int_point[2])
                        if int_point != []
                        else []
                    )  # object function returns array like
                    # p is array object, extract
                    p_list.append(
                        LoadPoint(int_point[0], int_point[1], int_point[2], p[0])
                        if int_point != []
                        else []
                    )
            # loop each node in grid points
            for items in node_in_grid:
                coord = self.Mesh_obj.node_spec[items]["coordinate"]
                p = patch_load_obj.patch_mag_interpolate(coord[0], coord[2])[
                    0
                ]  # object function returns array like
                p_list.append(LoadPoint(coord[0], coord[1], coord[2], p))
            # Loop each p_list object to find duplicates if any, remove duplicate
            for count, point in enumerate(p_list):
                dupe = [point == val for val in p_list]
                # if duplicate, remove value
                if sum(dupe) > 1:
                    p_list.pop(count)
            # sort points in counterclockwise
            p_list, _ = sort_vertices(p_list)  # sort takes namedtuple
            # get centroid of patch on grid
            xc, yc, zc = get_patch_centroid(p_list)
            inside_point = Point(xc, yc, zc)
            # volume = area of base x average height
            # _, A = calculate_area_given_four_points(inside_point, p_list[0], p_list[1], p_list[2], p_list[3])
            A = self._get_node_area(inside_point=inside_point, p_list=p_list)
            mag = A * sum([point.p for point in p_list]) / len(p_list)
            # assign point and mag to 4 nodes of grid
            load_str = self._assign_point_to_four_node(
                point=[xc, yc, zc], mag=mag, shape_func=patch_load_obj.shape_function
            )
            patch_load_str += load_str
        return patch_load_str

    @staticmethod
    def _get_node_area(inside_point, p_list) -> float:
        A = calculate_area_given_vertices(p_list)
        return A

    # ----------------------------------------------------------------------------------------------------------
    #  functions to add load case and load combination
    def _distribute_load_types_to_model(
        self, load_case_obj: Union[LoadCase, CompoundLoad]
    ) -> list:
        global load_groups
        load_str = []
        # check the input parameter type, set load_groups parameter according to its type
        if isinstance(load_case_obj, LoadCase):
            load_groups = load_case_obj.load_groups
        elif isinstance(load_case_obj.load_groups[0]["load"], CompoundLoad):
            load_groups = load_case_obj.load_groups[0]["load"].compound_load_obj_list
        # loop through each load object
        load_str = []
        for load_dict in load_groups:
            load_obj = load_dict["load"]
            # if compound load, distribute each individual load types within the compound load
            if isinstance(load_obj, CompoundLoad):
                # load_obj is a Compound load class, start a nested loop through each load class within compound load
                # nested loop through each load in compound load, assign and get
                for nested_list_of_load in load_obj.compound_load_obj_list:
                    if isinstance(nested_list_of_load, NodalLoad):
                        load_str += nested_list_of_load.get_nodal_load_str()
                    elif isinstance(nested_list_of_load, PointLoad):
                        load_str += self._assign_point_to_four_node(
                            point=list(nested_list_of_load.load_point_1)[:-1],
                            mag=nested_list_of_load.load_point_1.p,
                            shape_func=nested_list_of_load.shape_function,
                        )
                    elif isinstance(nested_list_of_load, LineLoading):
                        if any(
                            [
                                nested_list_of_load.long_beam_ele_load_flag,
                                nested_list_of_load.trans_beam_ele_load_flag,
                            ]
                        ):
                            load_str += self._assign_beam_ele_line_load(
                                line_load_obj=nested_list_of_load
                            )
                        else:
                            (
                                line_grid_intersect,
                                line_ele_colinear,
                            ) = self._get_line_load_nodes(
                                line_load_obj=nested_list_of_load
                            )  # returns self.line_grid_intersect
                            self.global_line_int_dict.append(line_grid_intersect)
                            load_str += self._assign_line_to_four_node(
                                nested_list_of_load,
                                line_grid_intersect=line_grid_intersect,
                                line_ele_colinear=line_ele_colinear,
                            )
                    elif isinstance(nested_list_of_load, PatchLoading):
                        load_str += self._assign_patch_load(nested_list_of_load)
            # else, a single load type, assign it as it is
            else:
                # run single assignment of load type (load_obj is a load class)
                if isinstance(load_obj, NodalLoad):
                    load_str += [
                        load_obj.get_nodal_load_str()
                    ]  # here return load_str as list with single element
                elif isinstance(load_obj, PointLoad):
                    load_str += self._assign_point_to_four_node(
                        point=list(load_obj.load_point_1)[:-1],
                        mag=load_obj.load_point_1.p,
                        shape_func=load_obj.shape_function,
                    )
                elif isinstance(load_obj, LineLoading):
                    if any(
                        [
                            load_obj.long_beam_ele_load_flag,
                            load_obj.trans_beam_ele_load_flag,
                        ]
                    ):
                        load_str += self._assign_beam_ele_line_load(
                            line_load_obj=load_obj
                        )
                    else:
                        (
                            line_grid_intersect,
                            line_ele_colinear,
                        ) = self._get_line_load_nodes(
                            line_load_obj=load_obj
                        )  # returns self.line_grid_intersect
                        self.global_line_int_dict.append(line_grid_intersect)
                        load_str += self._assign_line_to_four_node(
                            load_obj,
                            line_grid_intersect=line_grid_intersect,
                            line_ele_colinear=line_ele_colinear,
                        )
                elif isinstance(load_obj, PatchLoading):
                    load_str += self._assign_patch_load(load_obj)

        return load_str

    # ---------------------------------------------------------------
    # interface functions for load analysis utilities
    def add_load_case(self, load_case_obj: Union[LoadCase, MovingLoad], load_factor=1):
        """
        Function to add load cases to Ospllage grillage model. Function also adds moving load cases

        :param load_factor: Optional load factor for the prescribed load case. Default = 1
        :param load_case_obj: LoadCase or MovingLoad object
        :type load_case_obj: LoadCase,MovingLoad

        """

        if isinstance(load_case_obj, LoadCase):
            # update the load command list of load case object
            load_str = self._distribute_load_types_to_model(load_case_obj=load_case_obj)
            # store load case + load command in dict and add to load_case_list
            load_case_dict = {
                "name": load_case_obj.name,
                "loadcase": deepcopy(load_case_obj),
                "load_command": load_str,
                "load_factor": load_factor,
            }  # FORMATTING HERE

            self.load_case_list.append(load_case_dict)
            if self.diagnostics:
                print("Load Case: {} added".format(load_case_obj.name))
        elif isinstance(load_case_obj, MovingLoad):
            # get the list of individual load cases
            list_of_incr_load_case_dict = []
            moving_load_obj = load_case_obj
            # object method to create incremental load cases representing the position of the load
            moving_load_obj.parse_moving_load_cases()

            # for each load case, find the load commands of load distribution
            for moving_load_case_list in moving_load_obj.moving_load_case:
                for increment_load_case in moving_load_case_list:
                    load_str = self._distribute_load_types_to_model(
                        load_case_obj=increment_load_case
                    )
                    increment_load_case_dict = {
                        "name": increment_load_case.name,
                        "loadcase": increment_load_case,
                        "load_command": load_str,
                        "load_factor": load_factor,
                    }
                    list_of_incr_load_case_dict.append(increment_load_case_dict)
                self.moving_load_case_dict[
                    moving_load_obj.name
                ] = list_of_incr_load_case_dict

            if self.diagnostics:
                print("Moving load case: {} created".format(moving_load_obj.name))
        else:
            raise ValueError(
                "Input of add_load_case not a valid object. Hint:accepts only LoadCase or MovingLoad "
                "objects"
            )

    def analyze(self, **kwargs):
        """
        Function to analyze defined load

        :keyword:

        * all (`bool`): If True, runs all load cases. If not provided, default to True.
        * load_case ('list' or 'str'): String or list of name strings for selected load case to be analyzed.
        * set_verbose(`bool`): If True, incremental load case report is not printed to terminal (default True)

        :except: raise ValueError if missing arguments for either load_case=, or all=

        """
        # analyze all load case defined in self.load_case_dict for OspGrillage instance
        # loop each load case dict
        # get run options from kwargs
        all_flag = True  # Default true
        selected_load_case: list = kwargs.get("load_case", None)  #

        # check if any load cases are defined
        if self.load_case_list == [] and self.moving_load_case_dict == {}:
            raise Exception("No load cases were defined")

        if selected_load_case:
            all_flag = False  # overwrite all flag to be false
        selected_moving_load_lc_list = None
        # check if kwargs other than load_case are specified
        # if all([kwargs, selected_load_case is None]):
        #     raise Exception("Error in analyze(options): only accepts load_case= ")

        # if selected_load_case kwargs given, filter and select load case from load case list to run
        # if given selected load case as a list, select load cases matching names in list
        if isinstance(selected_load_case, list):
            selected_basic_lc = [
                lc for lc in self.load_case_list if lc["name"] in selected_load_case
            ]
            selected_moving_load_lc_list = [
                {ml_name: lc}
                for ml_name, lc in self.moving_load_case_dict.items()
                if ml_name in selected_load_case
            ]
            if selected_moving_load_lc_list:
                selected_moving_load_lc_list = selected_moving_load_lc_list[
                    0
                ]  # get first entry

        # if single string of load case name
        elif isinstance(selected_load_case, str):
            selected_basic_lc = [
                lc for lc in self.load_case_list if lc["name"] == selected_load_case
            ]
            selected_moving_load_lc_list = [
                {ml_name: lc}
                for (ml_name, lc) in self.moving_load_case_dict.items()
                if ml_name == selected_load_case
            ]
            if selected_moving_load_lc_list:
                selected_moving_load_lc_list = selected_moving_load_lc_list[
                    0
                ]  # get first entry

        elif all_flag:  # else, run all load case in list
            selected_basic_lc = self.load_case_list
            selected_moving_load_lc_list = self.moving_load_case_dict
        else:
            raise Exception(
                "missing kwargs for run options: hint: requires input for `load_case=`"
            )

        # run basic load case
        for load_case_dict in selected_basic_lc:
            # create analysis object, run and get results
            load_case_obj = load_case_dict["loadcase"]
            load_command = load_case_dict["load_command"]
            load_factor = load_case_dict["load_factor"]
            load_case_analysis = Analysis(
                analysis_name=load_case_obj.name,
                ops_grillage_name=self.model_name,
                pyfile=self.pyfile,
                time_series_counter=self.global_time_series_counter,
                pattern_counter=self.global_pattern_counter,
                node_counter=self.Mesh_obj.node_counter,
                ele_counter=self.Mesh_obj.element_counter,
                constraint_type=self.constraint_type,
                load_case=load_case_obj,
            )
            load_case_analysis.add_load_command(load_command, load_factor=load_factor)
            # run the Analysis object, collect results, and store Analysis object in the list for Analysis load case
            (
                self.global_time_series_counter,
                self.global_pattern_counter,
                node_disp,
                ele_force,
                self.analysis_command,
            ) = load_case_analysis.evaluate_analysis()

            # print to terminal
            if self.diagnostics:
                print("Analysis: {} completed".format(load_case_obj.name))
            # store result in Recorder object
            self.results.insert_analysis_results(analysis_obj=load_case_analysis)

        # run moving load case
        # for moving_load_obj, load_case_dict_list in self.moving_load_case_dict.items():
        if selected_moving_load_lc_list:
            for ml_name, load_case_dict_list in selected_moving_load_lc_list.items():
                list_of_inc_analysis = []
                for load_case_dict in load_case_dict_list:
                    load_case_obj = load_case_dict["loadcase"]  # maybe unused
                    load_command = load_case_dict["load_command"]
                    load_factor = load_case_dict["load_factor"]
                    incremental_analysis = Analysis(
                        analysis_name=load_case_obj.name,
                        ops_grillage_name=self.model_name,
                        pyfile=self.pyfile,
                        time_series_counter=self.global_time_series_counter,
                        pattern_counter=self.global_pattern_counter,
                        node_counter=self.Mesh_obj.node_counter,
                        ele_counter=self.Mesh_obj.element_counter,
                        constraint_type=self.constraint_type,
                        load_case=load_case_obj,
                    )
                    incremental_analysis.add_load_command(
                        load_command, load_factor=load_factor
                    )
                    (
                        self.global_time_series_counter,
                        self.global_pattern_counter,
                        node_disp,
                        ele_force,
                        self.analysis_command,
                    ) = incremental_analysis.evaluate_analysis()
                    list_of_inc_analysis.append(incremental_analysis)
                    if self.diagnostics:
                        print("Analysis: {} completed".format(load_case_obj.name))
                    # store result in Recorder object
                self.results.insert_analysis_results(
                    list_of_inc_analysis=list_of_inc_analysis
                )
                if self.diagnostics:
                    print("Analysis: {} completed".format(ml_name))

    def add_load_combination(
        self, load_combination_name: str, load_case_and_factor_dict: dict
    ):
        """
        Function to add load combination to analysis. Load combinations are defined through a dict with
        load case name str to be included in combination as keys, and load factor (type float/int) as value of dict.

        :param load_combination_name: Name string of load combination
        :type load_combination_name: str
        :param load_case_and_factor_dict: dict with name string of load cases within the combination as key,
                                            corresponding load factor as value.
        :type load_case_and_factor_dict: str

        Example format of input dict for add_load_combination::

            load_comb = {"name_of_load_case_1":1.2, "name_of_load_case_2": 1.5}

        .. note::

            As of release 0.1.0, load combinations can be directly obtained (calculated on the fly) by specifying
            ``combination`` kwarg in :func:`~ospgrillage.osp_grillage.OspGrillage.get_results`. Hence, `add_combination`
            is here for adding and storing information of load combination to  :class:`~ospgrillage.osp_grillage.OspGrillage`
            object.

        """
        load_case_dict_list = []  # list of dict: structure of dict See line
        # create dict with key (combination name) and val (list of dict of load cases)
        for (
            load_case_name,
            combination_load_factor,
        ) in load_case_and_factor_dict.items():
            # lookup basic load cases for load_case_name
            index_list = [
                index
                for (index, val) in enumerate(self.load_case_list)
                if val["name"] == load_case_name
            ]
            # copy lc objects in index list if present
            if index_list:
                ind = index_list[0]
                load_case_dict = deepcopy(self.load_case_list[ind])
                load_case_dict["load_factor"] = combination_load_factor
                load_case_dict_list.append(load_case_dict)
            # else look up in moving load cases
            elif load_case_name in self.moving_load_case_dict.keys():
                for inc_load_case_dict in self.moving_load_case_dict[load_case_name]:
                    inc_load_case_dict["load_factor"] = combination_load_factor
                    load_case_dict_list.append(inc_load_case_dict)

            # get the dict from self.load_case_list
            # self.load_case_list has this format [{'loadcase':LoadCase object, 'load_command': list of str}...]

        self.load_combination_dict.setdefault(
            load_combination_name, load_case_dict_list
        )
        if self.diagnostics:
            print("Load Combination: {} created".format(load_combination_name))

    def get_results(self, **kwargs):
        """
        Function to get results from specific or all load cases. Alternatively, function process and returns load combination if
        "combina+tions" argument is provided. Result format is xarray DataSet. If a "save_file_name" is provided, saves
        xarray DataSet to NetCDF format to current working directory.

        :keyword:
        * combinations (`bool`): If provided, returns a modified DataSet according to combinations defined. Format of argument is dict()
                                 with keys of load case name string and values of load factors (`int` of `float`)
        * save_file_name (`str`): Name string of file name. Saves to NetCDF.
        * load_case (`str`): str or list of name string of specific load case to extract. Returned DataSet with the specified Load cases only

        :return: Xarray DataSet of analysis results - extracted based on keyword option specified.
                            If combination is True, returns a list of DataSet, with each element correspond to
                            a load combination.

        """
        # instantiate variables
        list_of_moving_load_case = []
        coordinate_name_list = None
        # get kwargs
        comb = kwargs.get("combinations", False)  # if Boolean true
        save_filename = kwargs.get("save_filename", None)  # str of file name
        specific_load_case = kwargs.get("load_case", None)  # str of fil
        local_force_flag = kwargs.get("local_forces", False)
        basic_da = self.results.compile_data_array(
            local_force_option=local_force_flag,
            main_ele_tags=self.Mesh_obj.element_counter,
        )

        if isinstance(specific_load_case, str):
            specific_load_case = [specific_load_case]

        # filter extract specific load case, overwriting basic da
        if specific_load_case:
            storing_da = None
            for load_case_name in specific_load_case:
                # lookup in basic load cases
                namelist = [lc["name"] for lc in self.load_case_list]
                for name in namelist:
                    if load_case_name == name:
                        extract_da = basic_da.sel(Loadcase=name)
                        if storing_da is None:
                            storing_da = extract_da
                        else:  # storing_da is not none, concat in "loadcase" dimension
                            storing_da = xr.concat(
                                [storing_da, extract_da], dim="Loadcase"
                            )
                        if self.diagnostics:
                            print("Extracted load case data for : {}".format(name))
                # lookup in moving load cases
                for moving_name in self.moving_load_case_dict.keys():
                    if load_case_name == moving_name:
                        # get all string of moving name, then slice
                        incremental_lc_name_list = [
                            a["name"] for a in self.moving_load_case_dict[moving_name]
                        ]
                        for name in incremental_lc_name_list:
                            extract_da = basic_da.sel(Loadcase=name)
                            if storing_da is None:
                                storing_da = extract_da
                            else:  # storing_da is not none, concat in "loadcase" dimension
                                storing_da = xr.concat(
                                    [storing_da, extract_da], dim="Loadcase"
                                )

            basic_da = (
                storing_da  # Overwrite basic_da, proceed to check/evaluate combinations
            )

        # if combinations
        if comb:
            # output_load_comb_dict = []  # {name: datarray, .... name: dataarray}
            # load comb name,  load case in load comb
            # this format: self.load_combination_dict.setdefault(load_combination_name, load_case_dict_list)
            # comb = [{road:1.2, DL: 1.5},{} , {} ]
            if not isinstance(comb, dict):
                raise Exception(
                    "Combination argument requires a dict or a list of dict: e.g. {'DL':1.2,'SIDL':1.5}"
                )

            # for load_case_dict_list in comb:  # {0:[{'loadcase':LoadCase object, 'load_command': list of str}
            if self.diagnostics:
                print("Obtaining load combinations ....")

            summation_array = None  # instantiate
            factored_array = None  # instantiate
            # check and add load cases to load combinations for basic non moving load cases
            for (
                load_case_name,
                load_factor,
            ) in (
                comb.items()
            ):  # [{'loadcase':LoadCase object, 'load_command': list of str}.]
                # if load case is a moving load, skip to next step
                if load_case_name in self.moving_load_case_dict.keys():
                    list_of_moving_load_case.append(
                        {load_case_name: load_factor}
                    )  # store dict combination for later
                    continue

                # load_case_name = load_case_dict['loadcase'].name
                # if first load case, the first extracted array becomes the summation array
                # TODO, coordinate is now Load case Object
                if summation_array is None:
                    summation_array = (
                        basic_da.sel(Loadcase=load_case_name) * load_factor
                    )
                else:  # add to summation array
                    summation_array += (
                        basic_da.sel(Loadcase=load_case_name) * load_factor
                    )

            # check and add load cases to load combinations for moving load cases
            # get the list of increm load case correspond to matching moving load case of load combination
            # list_of_moving_load_case.append(self.moving_load_case_dict.get(load_case_name, []))
            for moving_lc_combo_dict in list_of_moving_load_case:
                coordinate_name_list = []
                for moving_lc_name, load_factor in moving_lc_combo_dict.items():
                    for incremental_load_case_dict in self.moving_load_case_dict[
                        moving_lc_name
                    ]:
                        load_case_name = incremental_load_case_dict["name"]
                        if factored_array is None:
                            factored_array = (
                                basic_da.sel(Loadcase=load_case_name) * load_factor
                                + summation_array
                            )
                        else:
                            factored_array = xr.concat(
                                [
                                    factored_array,
                                    basic_da.sel(Loadcase=load_case_name) * load_factor
                                    + summation_array,
                                ],
                                dim="Loadcase",
                            )
                        # store new coordinate name for load case
                        coordinate_name_list.append(load_case_name)
            # check if combination has moving load, if no, combination output is array summed among basic load case
            if not factored_array:
                combination_array = summation_array
            else:  # comb has moving load, assign the coordinates along the load case dimension for identification
                combination_array = factored_array.assign_coords(
                    Loadcase=coordinate_name_list
                )
            return combination_array

        else:
            # return raw data array for manual post processing
            if save_filename:
                basic_da.to_netcdf(save_filename)
            return basic_da

    def get_element(self, **kwargs):
        """
        Function to query properties of elements in grillage model.

        :keyword:
        * options (`str): string for element data option. Either "elements" or "nodes" (default)
        * z_group_num (`int`): group number [0 to N] for N is the number of groups within a specific grillage element group.
                               this is needed for interior beams, where users which to query specific group (e.g. 2nd group)
                               within this "interior_main_beam" element group.
        * x_group_num (`int`): ditto for z_group_num but for x_group
        * edge_group_num(`int`): ditto for z_group_num but for edge groups

        :return: List of element data (tag)
        """
        # get query member details
        namestring = kwargs.get("member", None)
        select_z_group = kwargs.get(
            "z_group_num", 0
        )  # optional z_group number for internal beam members
        select_x_group = kwargs.get("x_group_num", None)
        select_edge_group = kwargs.get("edge_group_num", None)
        # prefix namestring variables
        element_option = "elements"
        node_option = "nodes"
        # instantiate variables
        sorted_return_list = []
        extracted_ele = []
        # read kwargs
        options = kwargs.get(
            "options", node_option
        )  # similar to ops_vis, "nodes","element","node_i","node_j"
        if not options:
            raise Exception(
                'Options not defined: Hint arg option=  "nodes","element","node_i","node_j"'
            )

        # reading common elements off namestring
        if namestring == "transverse_slab":
            extracted_ele = self.Mesh_obj.trans_ele
            # TODO
        elif namestring == "start_edge" or namestring == "end_edge":
            for edge_group in self.common_grillage_element_z_group[namestring]:
                extracted_ele = self.Mesh_obj.edge_group_to_ele[edge_group]
            if options == node_option:
                sorted_return_list = [
                    key
                    for key, val in self.Mesh_obj.edge_node_recorder.items()
                    if val == self.common_grillage_element_z_group[namestring][0]
                ]
            elif options == element_option:
                sorted_return_list = [ele[0] for ele in extracted_ele]
        else:  # longitudinal members
            extracted_ele = [
                self.Mesh_obj.z_group_to_ele[num]
                for num in self.common_grillage_element_z_group[namestring]
            ][select_z_group]
            if options == node_option:
                first_list = [i[1] for i in extracted_ele]  # first list of nodes
                second_list = [i[2] for i in extracted_ele]  # second list of nodes
                return_list = first_list + list(
                    set(second_list) - set(first_list)
                )  # get only unique nodes
                # sort nodes based on x coordinate
                node_x = [
                    self.Mesh_obj.node_spec[tag]["coordinate"][0] for tag in return_list
                ]
                sorted_return_list.append(
                    [x for _, x in sorted(zip(node_x, return_list))]
                )
            elif options == element_option:
                sorted_return_list = [i[0] for i in extracted_ele]
        return sorted_return_list

    def get_nodes(self):
        """
        Function to return all information for nodes in grillage model

        :return: dict contain node information
        """
        return self.Mesh_obj.node_spec

    def clear_load_cases(self, **kwargs):
        """
        Function to remove all/specific load cases from model. This function also resets the results stored in the
        model - users are require to re- :func:`~ospgrillage.osp_grillage.OspGrillage.analyze`.

        """
        specific_lc = kwargs.get("load_case", None)
        if isinstance(specific_lc, str):
            specific_lc = [specific_lc]
        if specific_lc:
            for lc in specific_lc:
                check_match = [lc in lc_name["name"] for lc_name in self.load_case_list]
                if any(check_match):
                    ind = [i for i, x in enumerate(check_match) if x][
                        0
                    ]  # list of 1 element
                    self.load_case_list.pop(ind)

        else:
            self.load_case_list = []  # reset load case

        # remove all results
        self.results = Results(self.Mesh_obj)  # reset results


# ---------------------------------------------------------------------------------------------------------------------
class Analysis:
    """
    Main class to handle the run/execution of load case, including incremental load cases of a moving load analysis.
    Analysis class is created and handled by the OspGrillage class.

    The following are the roles of Analysis object:

    * store information of ops commands for performing static (default) analysis of single/multiple load case(s).
    * execute the required ops commands to perform analysis using the OspGrillage model instance.
    * if flagged, writes an executable py file instead which performs the exact analysis as it would for an OspGrillage instance instead.
    * manages multiple load case's ops.load() commands, applying the specified load factors to the load cases for load combinations

    """

    remove_pattern_command: str

    def __init__(
        self,
        analysis_name: str,
        ops_grillage_name: str,
        pyfile: bool,
        node_counter,
        ele_counter,
        analysis_type="Static",
        time_series_counter=1,
        pattern_counter=1,
        load_case: LoadCase = None,
        **kwargs,
    ):
        self.analysis_name = analysis_name
        self.ops_grillage_name = ops_grillage_name
        self.time_series_tag = None
        self.pattern_tag = None
        self.analysis_type = analysis_type
        self.pyfile = pyfile
        self.analysis_file_name = (
            self.analysis_name + "of" + self.ops_grillage_name + ".py"
        )  # py file name
        # list recording load commands, time series and pattern for the input load case
        self.load_cases_dict_list = (
            []
        )  # keys # [{time_series,pattern,load_command},... ]
        # counters
        self.time_series_counter = time_series_counter
        self.plain_counter = pattern_counter
        # variables from keyword args
        self.constraint_type = kwargs.get("constraint_type", "Plain")  # Default plain
        # Variables recording results of analysis
        self.node_disp = dict()  # key node tag, val list of dof
        self.ele_force = (
            dict()
        )  # key ele tag, val list of forces on nodes of ele[ order according to ele tag]
        self.global_ele_force = (
            dict()
        )  # key ele tag, val list of forces on nodes of ele[ order according to ele tag]
        self.ele_force_shell = dict()  # ditto for ele force except only for shells
        self.global_ele_force_shell = (
            dict()
        )  # ditto for global ele force except only for shells
        # preset ops analysis commands
        self.wipe_command = "ops.wipeAnalysis()\n"  # default wipe command
        self.numberer_command = "ops.numberer('Plain')\n"  # default numberer is Plain
        self.system_command = "ops.system('BandGeneral')\n"  # default band general
        self.constraint_command = 'ops.constraints("{type}")\n'.format(
            type=self.constraint_type
        )  # default plain
        self.algorithm_command = "ops.algorithm('Linear')\n"  # default linear
        self.analyze_command = "ops.analyze(1)\n"  # default 1 step
        self.analysis_command = 'ops.analysis("{}")\n'.format(analysis_type)
        self.intergrator_command = "ops.integrator('LoadControl', 1)\n"
        self.sensitivity_integrator_command = "ops."
        self.mesh_node_counter = node_counter  # set node counter based on current Mesh
        self.mesh_ele_counter = ele_counter  # set ele counter based on current Mesh
        self.remove_pattern_command = (
            "ops.remove('loadPattern',{})\n"  # default remove load command
        )
        # save deepcopy of load case object
        self.load_cases_obj = deepcopy(load_case)
        # var to store all eval command
        self.all_command = []
        # if true for pyfile, create pyfile for analysis command
        if self.pyfile:
            with open(self.analysis_file_name, "w") as file_handle:
                # create py file or overwrite existing
                # writing headers and description at top of file
                file_handle.write(
                    "# Executable py file for Analysis of \n# Model name: {}\n".format(
                        self.ops_grillage_name
                    )
                )
                file_handle.write("# Load case: {}\n".format(self.analysis_name))
                # time
                now = datetime.now()
                dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
                file_handle.write("# Constructed on:{}\n".format(dt_string))
                # write imports
                file_handle.write(
                    "import numpy as np\nimport math\nimport openseespy.opensees as ops"
                    "\nimport openseespy.postprocessing.Get_Rendering as opsplt\n"
                )

    def _time_series_command(self, load_factor):
        time_series = "ops.timeSeries('Constant', {}, '-factor',{})\n".format(
            self.time_series_counter, load_factor
        )
        self.time_series_counter += 1  # update counter by 1
        return time_series

    def _pattern_command(self):
        pattern_command = "ops.pattern('Plain', {}, {})\n".format(
            self.plain_counter, self.time_series_counter - 1
        )
        # minus 1 to time series counter for time_series_command() precedes pattern_command() and incremented the time
        # series counter
        self.plain_counter += 1
        return pattern_command

    def add_load_command(self, load_str: list, load_factor):
        # create time series for added load case
        time_series = self._time_series_command(
            load_factor
        )  # get time series command - LF default 1
        pattern_command = self._pattern_command()  # get pattern command
        time_series_dict = {
            "time_series": time_series,
            "pattern": pattern_command,
            "load_command": load_str,
        }
        self.load_cases_dict_list.append(time_series_dict)  # add dict to list

    def evaluate_analysis(self):
        # write/execute ops.load commands for load groups
        if self.pyfile:
            with open(self.analysis_file_name, "a") as file_handle:
                file_handle.write(self.wipe_command)
                for load_dict in self.load_cases_dict_list:
                    file_handle.write(load_dict["time_series"])
                    file_handle.write(load_dict["pattern"])
                    for load_command in load_dict["load_command"]:
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
            self.all_command.append(self.wipe_command)
            if (
                self.plain_counter - 1 != 1
            ):  # plain counter increments by 1 upon self.pattern_command function, so -1 here
                for count in range(1, self.plain_counter - 1):
                    remove_command = self.remove_pattern_command.format(count)
                    eval(remove_command)  # remove previous load pattern if any
                    self.all_command.append(remove_command)
            for load_dict in self.load_cases_dict_list:
                eval(load_dict["time_series"])
                self.all_command.append(load_dict["time_series"])
                eval(load_dict["pattern"])
                self.all_command.append(load_dict["pattern"])
                for load_command in load_dict["load_command"]:
                    eval(load_command)
                    self.all_command.append(load_command)
            eval(self.intergrator_command)
            eval(self.numberer_command)
            eval(self.system_command)
            eval(self.constraint_command)
            eval(self.algorithm_command)
            eval(self.analysis_command)
            eval(self.analyze_command)
            self.all_command.append(self.intergrator_command)
            self.all_command.append(self.numberer_command)
            self.all_command.append(self.system_command)
            self.all_command.append(self.constraint_command)
            self.all_command.append(self.algorithm_command)
            self.all_command.append(self.analysis_command)
            self.all_command.append(self.analyze_command)

        # extract results
        self.extract_grillage_responses()
        # return time series and plain counter to update global time series and plain counter by by OspGrillage
        return (
            self.time_series_counter,
            self.plain_counter,
            self.node_disp,
            self.ele_force,
            self.all_command,
        )

    # function to extract grillage model responses (dx,dy,dz,rotx,roty,rotz,N,Vy,Vz,Mx,My,Mz) and store to Result class
    def extract_grillage_responses(self):
        """
        Function that wraps OpenSeesPy nodeDisp() and eleResponse(), gets results of current analysis - model instance
        in OpenSees.

        :return: Stores results in global_ele_force and node_disp class variable
        """
        if not self.pyfile:
            # first loop extract node displacements
            for node_tag in ops.getNodeTags():
                disp_list = ops.nodeDisp(node_tag)
                self.node_disp.setdefault(node_tag, disp_list)

            # loop through all elements in Mesh, extract local forces
            for ele_tag in ops.getEleTags():
                ele_force = ops.eleResponse(ele_tag, "localForces")
                self.ele_force.setdefault(ele_tag, ele_force)
                global_ele_force = ops.eleResponse(ele_tag, "forces")
                self.global_ele_force.setdefault(ele_tag, global_ele_force)
        else:
            print(
                "OspGrillage is at output mode, pyfile = True. Procedure for {} are generated.".format(
                    self.analysis_name
                )
            )


class Results:
    """
    Main class to store results of an Analysis class object, process into data array output for post processing/plotting.
    Class object is accessed within OspGrillage class object.
    """

    def __init__(self, mesh_obj: Mesh):
        # instantiate variables
        self.basic_load_case_record = dict()
        self.basic_load_case_record_global_forces = dict()
        self.moving_load_case_record = []
        self.moving_load_case_record_global_forces = []
        self.moving_load_counter = 0
        # store mesh data of holding model
        self.mesh_obj = mesh_obj
        # coordinates for dimensions
        self.displacement_component = [
            "dx",
            "dy",
            "dz",
            "theta_x",
            "theta_y",
            "theta_z",
        ]
        self.force_component = [
            "Vx_i",
            "Vy_i",
            "Vz_i",
            "Mx_i",
            "My_i",
            "Mz_i",
            "Vx_j",
            "Vy_j",
            "Vz_j",
            "Mx_j",
            "My_j",
            "Mz_j",
        ]
        # for force component of shell model (4 nodes)
        self.force_component_shell = [
            "Vx_i",
            "Vy_i",
            "Vz_i",
            "Mx_i",
            "My_i",
            "Mz_i",
            "Vx_j",
            "Vy_j",
            "Vz_j",
            "Mx_j",
            "My_j",
            "Mz_j",
            "Vx_k",
            "Vy_k",
            "Vz_k",
            "Mx_k",
            "My_k",
            "Mz_k",
            "Vx_l",
            "Vy_l",
            "Vz_l",
            "Mx_l",
            "My_l",
            "Mz_l",
        ]
        # dimension names
        self.dim = ["Loadcase", "Node", "Component"]
        self.dim2 = ["Loadcase", "Element", "Component"]
        self.dim_ele_beam = ["i", "j"]
        self.dim_ele_shell = ["i", "j", "k", "l"]

    def insert_analysis_results(
        self, analysis_obj: Analysis = None, list_of_inc_analysis: list = None
    ):
        # Create/parse data based on incoming analysis object or list of analysis obj (moving load)
        if analysis_obj:
            # compile ele forces for each node
            node_disp = analysis_obj.node_disp
            ele_force_dict = dict.fromkeys(
                list(ops.getEleTags())
            )  # dict key is element tag, value is ele force from
            global_ele_force_dict = dict.fromkeys(
                list(ops.getEleTags())
            )  # dict key is element tag, value is ele force from
            ele_nodes_dict = dict.fromkeys(list(ops.getEleTags()))
            # analysis_obj.ele_force
            # extract element forces and sort them to according to nodes - summing in the process
            for ele_num, ele_forces in analysis_obj.ele_force.items():
                ele_force_dict.update({ele_num: ele_forces})
                # get ele nodes
                ele_nodes = ops.eleNodes(ele_num)
                ele_nodes_dict.update({ele_num: ele_nodes})
            self.basic_load_case_record.setdefault(
                analysis_obj.analysis_name, [node_disp, ele_force_dict, ele_nodes_dict]
            )

            # repeat to extract global forces instead
            # extract element forces and sort them to according to nodes - summing in the process
            for ele_num, ele_forces in analysis_obj.global_ele_force.items():
                global_ele_force_dict.update({ele_num: ele_forces})
                ele_nodes = ops.eleNodes(ele_num)  # get ele nodes
                ele_nodes_dict.update({ele_num: ele_nodes})
            self.basic_load_case_record_global_forces.setdefault(
                analysis_obj.analysis_name,
                [node_disp, global_ele_force_dict, ele_nodes_dict],
            )
        # if moving load, input is a list of analysis obj
        elif list_of_inc_analysis:
            inc_load_case_record = dict()
            inc_load_case_global_force_record = (
                dict()
            )  # inc_load_case_record but with forces in global

            for inc_analysis_obj in list_of_inc_analysis:
                # compile ele forces for each node
                node_disp = inc_analysis_obj.node_disp
                ele_force_dict = dict.fromkeys(list(ops.getEleTags()))
                ele_force_global_dict = dict.fromkeys(list(ops.getEleTags()))
                ele_nodes_dict = dict.fromkeys(list(ops.getEleTags()))
                # extract element forces and sort them to according to nodes - summing in the process
                for ele_num, ele_forces in inc_analysis_obj.ele_force.items():
                    ele_force_dict.update({ele_num: ele_forces})
                    # get ele nodes
                    ele_nodes = ops.eleNodes(ele_num)
                    ele_nodes_dict.update({ele_num: ele_nodes})

                inc_load_case_record.setdefault(
                    inc_analysis_obj.analysis_name,
                    [node_disp, ele_force_dict, ele_nodes_dict],
                )
                for ele_num, ele_forces in inc_analysis_obj.global_ele_force.items():
                    ele_force_global_dict.update({ele_num: ele_forces})
                inc_load_case_global_force_record.setdefault(
                    inc_analysis_obj.analysis_name,
                    [node_disp, ele_force_global_dict, ele_nodes_dict],
                )

            self.moving_load_case_record.append(inc_load_case_record)
            self.moving_load_case_record_global_forces.append(
                inc_load_case_global_force_record
            )

    def compile_data_array(self, local_force_option=True, main_ele_tags=None):
        # Function called to compile analysis results into xarray
        # Coordinates of dimension
        node = list(self.mesh_obj.node_spec.keys())  # for Node
        ele = list(ops.getEleTags())

        # Sort data for dataArrays
        # for basic load case  {loadcasename:[{1:,2:...},{1:,2:...}], ... , loadcasename:[{1:,2:...},{1:,2:...} }
        basic_node_disp_list = []
        basic_load_case_coord = []
        basic_ele_force_list = []
        extracted_ele_nodes_list = False  # a 2D array of ele node i and ele node j
        ele_nodes_list = []
        base_ele_force_list_beam = []
        base_ele_force_list_shell = []
        ele_tag = []
        # check if force option is global or local
        if local_force_option:
            basic_dict = self.basic_load_case_record
            moving_dict = self.moving_load_case_record
        else:  # global forces
            basic_dict = self.basic_load_case_record_global_forces
            moving_dict = self.moving_load_case_record_global_forces

        # loop all basic load case
        for load_case_name, resp_list_of_2_dict in basic_dict.items():
            # extract displacement
            basic_node_disp_list.append(
                [a for a in list(resp_list_of_2_dict[0].values())]
            )  # list index 0 is disp
            # extract force
            basic_ele_force_list.append(
                [a for a in list(resp_list_of_2_dict[1].values())]
            )  # list index 1 is force
            # extract based on element type
            base_ele_force_list_beam.append(
                [
                    a
                    for a in list(resp_list_of_2_dict[1].values())
                    if len(a) == len(self.force_component)
                ]
            )
            base_ele_force_list_shell.append(
                [
                    a
                    for a in list(resp_list_of_2_dict[1].values())
                    if len(a) == len(self.force_component_shell)
                ]
            )
            if not extracted_ele_nodes_list:
                ele_nodes_list = list(
                    resp_list_of_2_dict[2].values()
                )  # list index 2 is ele nodes variable
                extracted_ele_nodes_list = (
                    True  # set to true, only extract if its the first time extracting
                )
                ele_tag = list(resp_list_of_2_dict[2].keys())
            # for section forces of each element
            # Coordinate of Load Case dimension
            basic_load_case_coord.append(load_case_name)
            # combine disp and force with respect to Component axis : size 12

        # loop all moving load cases
        for moving_load_case_inc_dict in moving_dict:
            # for each load case increment in moving load case
            for (
                increment_load_case_name,
                inc_resp_list_of_2_dict,
            ) in moving_load_case_inc_dict.items():
                # basic_array_list.append([a + b for (a, b) in zip(list(inc_resp_list_of_2_dict[0].values()),
                #                                                       list(inc_resp_list_of_2_dict[1].values()))])
                basic_node_disp_list.append(
                    [a for a in list(inc_resp_list_of_2_dict[0].values())]
                )

                if local_force_option:
                    basic_ele_force_list.append(
                        [
                            a
                            for a in list(inc_resp_list_of_2_dict[1].values())
                            if len(a) == len(self.force_component)
                        ]
                    )
                else:
                    # global force
                    basic_ele_force_list.append(
                        [a for a in list(inc_resp_list_of_2_dict[1].values())]
                    )

                # lists for shell model output
                base_ele_force_list_beam.append(
                    [
                        a
                        for key, a in zip(
                            list(inc_resp_list_of_2_dict[1].keys()),
                            list(inc_resp_list_of_2_dict[1].values()),
                        )
                        if len(a) == len(self.force_component)
                        if key < main_ele_tags
                    ]
                )
                base_ele_force_list_shell.append(
                    [
                        a
                        for a in list(inc_resp_list_of_2_dict[1].values())
                        if len(a) == len(self.force_component_shell)
                    ]
                )
                # Coordinate of Load Case dimension
                # inc_moving_load_case_coord.append(increment_load_case_name)
                basic_load_case_coord.append(increment_load_case_name)
                if not extracted_ele_nodes_list:
                    ele_nodes_list = list(inc_resp_list_of_2_dict[2].values())
                    ele_tag = list(inc_resp_list_of_2_dict[2].keys())
                    extracted_ele_nodes_list = True
        # convert to np array format
        basic_array = np.array(basic_node_disp_list, dtype=object)
        force_array = np.array(basic_ele_force_list, dtype=object)
        ele_array = np.array(ele_nodes_list, dtype=object)

        ele_tag = np.array(ele_tag)
        ele_tag_shell = [tag for tag, e in zip(ele_tag, ele_array) if len(e) > 2]
        ele_array_shell = [e for tag, e in zip(ele_tag, ele_array) if len(e) > 2]
        ele_tag_beam = [
            tag
            for tag, e in zip(ele_tag, ele_array)
            if len(e) == 2
            if tag < main_ele_tags
        ]
        ele_array_beam = [
            e
            for tag, e in zip(ele_tag, ele_array)
            if len(e) == 2
            if tag < main_ele_tags
        ]
        force_array_shell = np.array(base_ele_force_list_shell)
        force_array_beam = np.array(base_ele_force_list_beam)

        # create data array for each basic load case if any, else return
        if basic_array.size:
            # displacement data array
            basic_da = xr.DataArray(
                data=basic_array,
                dims=self.dim,
                coords={
                    self.dim[0]: basic_load_case_coord,
                    self.dim[1]: node,
                    self.dim[2]: self.displacement_component,
                },
            )

            ele_nodes_beam = xr.DataArray(
                data=ele_array_beam,
                dims=[self.dim2[1], "Nodes"],
                coords={self.dim2[1]: ele_tag_beam, "Nodes": self.dim_ele_beam},
            )
            # create data set based on
            if isinstance(self.mesh_obj, ShellLinkMesh):
                force_da_beam = xr.DataArray(
                    data=force_array_beam,
                    dims=self.dim2,
                    coords={
                        self.dim2[0]: basic_load_case_coord,
                        self.dim2[1]: ele_tag_beam,
                        self.dim2[2]: self.force_component,
                    },
                )
                force_da_shell = xr.DataArray(
                    data=force_array_shell,
                    dims=self.dim2,
                    coords={
                        self.dim2[0]: basic_load_case_coord,
                        self.dim2[1]: ele_tag_shell,
                        self.dim2[2]: self.force_component_shell,
                    },
                )
                ele_nodes_shell = xr.DataArray(
                    data=ele_array_shell,
                    dims=[self.dim2[1], "Nodes"],
                    coords={self.dim2[1]: ele_tag_shell, "Nodes": self.dim_ele_shell},
                )
                result = xr.Dataset(
                    {
                        "displacements": basic_da,
                        "forces_beam": force_da_beam,
                        "forces_shell": force_da_shell,
                        "ele_nodes_beam": ele_nodes_beam,
                        "ele_nodes_shell": ele_nodes_shell,
                    }
                )
            else:
                force_da_beam = xr.DataArray(
                    data=force_array,
                    dims=self.dim2,
                    coords={
                        self.dim2[0]: basic_load_case_coord,
                        self.dim2[1]: ele_tag
                        if not local_force_option
                        else ele_tag_beam,
                        self.dim2[2]: self.force_component,
                    },
                )
                result = xr.Dataset(
                    {
                        "displacements": basic_da,
                        "forces": force_da_beam,
                        "ele_nodes": ele_nodes_beam,
                    }
                )

        else:  # no result return None
            result = None
        return result


# ---------------------------------------------------------------------------------------------------------------------
# concrete classes of grillage model


class OspGrillageBeam(OspGrillage):
    """
    Concrete class for beam grillage model type.
    """

    def __init__(
        self,
        bridge_name,
        long_dim,
        width,
        skew: Union[list, float, int] = 0,
        num_long_grid: int = 0,
        num_trans_grid: int = 0,
        edge_beam_dist: Union[list, float, int] = 1,
        mesh_type="Ortho",
        model="3D",
        **kwargs,
    ):
        # create mesh and model
        super().__init__(
            bridge_name,
            long_dim,
            width,
            skew,
            num_long_grid,
            num_trans_grid,
            edge_beam_dist,
            mesh_type,
            model="3D",
            **kwargs,
        )
        #


class OspGrillageShell(OspGrillage):
    """
    Concrete class for shell model type
    """

    def __init__(
        self,
        bridge_name,
        long_dim,
        width,
        skew: Union[list, float, int],
        num_long_grid: int,
        num_trans_grid: int,
        edge_beam_dist: Union[list, float, int],
        mesh_type="Ortho",
        model="3D",
        **kwargs,
    ):
        # input variables specific to shell model - see default parameters if not specified
        self.offset_beam_y_dist = kwargs.get("offset_beam_y_dist", 0)  # default 0
        self.mesh_size_x = kwargs.get("max_mesh_size_x", 1)  # default 1 unit meter
        self.mesh_size_z = kwargs.get("max_mesh_size_z", 1)  # default 1 unit meter

        # model variables specific to Shell type
        self.shell_element_command_list = (
            []
        )  # list of str for ops.element() shell command

        # create mesh and model
        super().__init__(
            bridge_name,
            long_dim,
            width,
            skew,
            num_long_grid,
            num_trans_grid,
            edge_beam_dist,
            mesh_type,
            model="3D",
            **kwargs,
        )
        # overwrite/ variables specific to shell mesh
        self.constraint_type = (
            "Transformation"  # constraint type to allow MP constraint objects
        )
        # overwrite standard element list for shell model
        self._create_standard_element_list()

    # ----------------------------------------------------------------------------------------------------------------
    # overwrite functions of base Mesh class - specific for
    def create_osp_model(self, pyfile=False):
        """
        Function to create model instance in OpenSees model space. If pyfile input is True, function creates an
        executable pyfile for generating the grillage model in OpenSees model space.

        :param pyfile: if True returns an executable py file instead of creating OpenSees instance of model.
        :type pyfile: bool

        """
        self.pyfile = pyfile

        if self.pyfile:
            with open(self.filename, "w") as file_handle:
                # create py file or overwrite existing
                # writing headers and description at top of file
                file_handle.write(
                    "# Grillage generator wizard\n# Model name: {}\n".format(
                        self.model_name
                    )
                )
                # time
                now = datetime.now()
                dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
                file_handle.write("# Constructed on:{}\n".format(dt_string))
                # write imports
                file_handle.write(
                    "import numpy as np\nimport math\nimport openseespy.opensees as ops"
                    "\nimport openseespy.postprocessing.Get_Rendering as opsplt\n"
                )
        # model() command
        self._write_op_model()
        # create grillage mesh object + beam element groups
        self._run_mesh_generation()

        # create shell element commands
        for ele_str in self.shell_element_command_list:
            if self.pyfile:
                with open(self.filename, "a") as file_handle:
                    file_handle.write(ele_str)
            else:
                eval(ele_str)
        # create rigid link command
        self._write_rigid_link()
        # create the result file for the Mesh object
        self.results = Results(self.Mesh_obj)
        # flag

    # overwrites base class for beam element grillage - specific for Shell model
    def _create_standard_element_list(self):
        """
        Function to create standard element list for grillage model type.
        This child class overwrite parent class's function for beam grillage model type.
        :return:
        """
        # standard element for beam class
        for key, val in zip(
            self.common_grillage_element_keys[0 : self.long_member_index],
            sort_list_into_four_groups(
                self.Mesh_obj.offset_z_groups, option="shell"
            ).values(),
        ):
            self.common_grillage_element_z_group.update({key: val})
        # update edge beam groups' value
        self.common_grillage_element_z_group.update(
            {
                self.common_grillage_element_keys[0]: [
                    self.Mesh_obj.model_plane_z_groups[0],
                    self.Mesh_obj.model_plane_z_groups[-1],
                ]
            }
        )

    # ----------------------------------------------------------------------------------------------------------------
    # interface function
    def set_member(
        self, grillage_member_obj: GrillageMember, member=None, specific_group=None
    ):
        """
        Function to set grillage member class object to elements of grillage members.

        :param grillage_member_obj: `GrillageMember` class object
        :type grillage_member_obj: GrillageMember
        :param member: str of member category - see below table for the available name strings
        :type member: str


         =====================================    ======================================
         Standard grillage elements name str      Description
         =====================================    ======================================
          edge_beam                               Elements along x axis at top and bottom edges of mesh (z = 0, z = width)
          exterior_main_beam_1                    Elements along first grid line after bottom edge (z = 0)
          interior_main_beam                      For all elements in x direction between grid lines of exterior_main_beam_1 and exterior_main_beam_2
          exterior_main_beam_1                    Elements along first grid line after top edge (z = width)
         =====================================    ======================================


        :raises: ValueError If missing argument for member=
        """
        if self.diagnostics:
            print("Setting member: {} of model".format(member))
        if member is None:
            raise ValueError(
                "Missing target elements of grillage model to be assigned. Hint, member="
            )
        # check and write member's section command
        section_tag = self._write_section(grillage_member_obj)
        # check and write member's material command
        material_tag = self._write_material(member=grillage_member_obj)
        # dictionary for key = common member tag, val is list of str for ops.element()
        ele_command_dict = dict()
        ele_command_list = []
        ele_group_to_command_dict = dict()
        ele_tag_to_command_dict = dict()
        # if option for pyfile is True, write the header for element group commands
        if self.pyfile:
            with open(self.filename, "a") as file_handle:
                file_handle.write(
                    "# Element generation for member: {}\n".format(member)
                )

        # check if assign GrillageMember obj has unit width flagged True
        if grillage_member_obj.section.unit_width:
            raise Exception(
                "GrillageMember obj for",
                grillage_member_obj,
                "flagged with unit_width feature = True is"
                "not acceptable for shell model ",
            )
        else:  # assign to longitudinal beam members
            for z_group in self.common_grillage_element_z_group[member]:
                ele_command_list += self._get_element_command_list(
                    grillage_member_obj=grillage_member_obj,
                    list_of_ele=self.Mesh_obj.z_group_to_ele[z_group],
                    material_tag=material_tag,
                    section_tag=section_tag,
                )
                ele_group_to_command_dict[z_group] = ele_command_list

                for nth, ele in enumerate(self.Mesh_obj.z_group_to_ele[z_group]):
                    ele_tag_to_command_dict[ele[0]] = ele_command_list[nth]

                ele_command_list = []
        # store into dict or replace existing

        ele_command_dict[member] = ele_group_to_command_dict

        self.element_command_list.update(ele_tag_to_command_dict)

    # functions specific to Shell model class
    def set_shell_members(
        self, grillage_member_obj: GrillageMember, quad=True, tri=False
    ):
        """
        Function to set shell/quad members across entire mesh grid.

        :param quad: Boolean to flag setting quad shell members
        :param tri: Boolean to flag setting triangular shell members
        :param grillage_member_obj: GrillageMember object
        :type grillage_member_obj: GrillageMember
        :raises ValueError: If GrillageMember object was not specified for quad or shell element. Also raises this error
                            if components of GrillageMember object (e.g. section or material) is not a valid property
                            for the specific shell element type in accordance with OpenSees conventions.

        .. note::
            Feature to be updated with class segregation later on 0.1.1

        """
        # this function creates shell elements out of the node grids of Mesh object
        # if self.Mesh_obj is None:  # checks if
        #     raise ValueError("Model instance not created. Run ops.create_ops() function before setting members")
        # check and write member's section command if any
        section_tag = self._write_section(grillage_member_obj)
        # check and write member's material command if any
        material_tag = self._write_material(member=grillage_member_obj)
        # for each grid in Mesh, create a shell element
        for grid_nodes_list in self.Mesh_obj.grid_number_dict.values():
            shell_counter = self.global_ele_counter
            ele_str = grillage_member_obj.get_element_command_str(
                ele_tag=shell_counter,
                node_tag_list=grid_nodes_list,
                materialtag=material_tag,
                sectiontag=section_tag,
            )
            self.shell_element_command_list.append(ele_str)
            self.global_ele_counter += 1

    # overwrite base fix() command procedure
    def _write_op_fix(self, mesh_obj):
        """
        Overwritten sub procedure to create ops.fix() command for
        boundary condition definition in the grillage model. If pyfile is flagged true, writes
        the ops.fix() command to py file instead.

        """
        if self.pyfile:
            with open(self.filename, "a") as file_handle:
                file_handle.write("# Boundary condition implementation\n")
        for node_tag, edge_group_num in mesh_obj.edge_support_nodes.items():
            fix_str = "ops.fix({}, *{})\n".format(
                node_tag, self.edge_support_type_dict[edge_group_num]
            )
            if self.pyfile:  # if writing py file
                with open(self.filename, "a") as file_handle:
                    file_handle.write(fix_str)
            else:  # run instance
                eval(fix_str)
                self.model_command_list.append(fix_str)
