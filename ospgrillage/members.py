# -*- coding: utf-8 -*-
"""
This module manages user interface functions and class definitions for the
grillage members. In our terminology, we define a section as the geometrical
properties of the structural elements, and the member as the combination of
the section and material properties.
"""


def create_section(**kwargs):
    """
    User interface for section creation.
    :keyword:
    * takes in keyword arguments of Openseespy.

    :returns Section: Section object
    """
    return Section(**kwargs)


def create_member(**kwargs):
    """
    User interface for member creation.
    :keyword:
    * material (`Material`): Material object
    * section (`Section`): Section object

    :returns GrillageMember: Grillage member object
    """
    return GrillageMember(**kwargs)


class Section:
    """
    Class for structural cross sections.Stores geometric properties related to Openseespy command in creating sections
    in Opensees model space.

    This class does not provide methods which wraps Openseespy Section() commands - this is done by GrillageMember class

    For developers wishing to expand the library of sections, introduce in this class:

    #. The keywrod arguments for the new sections.

    """

    def __init__(
        self,
        op_ele_type="elasticBeamColumn",
        mass=0,
        c_mass_flag=False,
        unit_width=False,
        op_section_type="Elastic",
        **kwargs
    ):
        """
        The constructor takes in two types of keyword arguments.

        #. General section properties - such as A, I, J for example. These properties are parses into the appropriate
            Opensees section arguments.
        #. Openseespy section arguments - i.e. specific keyword for a specific ops.section() type.

        `Here <https://openseespydoc.readthedocs.io/en/latest/src/section.html>`_ is a list of Opensees

        Here are the main input for the constructor to properly parse the inputs to Openseespy sections.

        :param op_ele_type: Opensees element type
        :type op_ele_type: str
        :param op_section_type: Opensees section type
        :type op_section_type: str
        :param unit_width: Flag for unit width properties
        :type unit_width: bool

        Here are the common keyword arguments for defining a section.

        :keyword:
        * A (``float``): Cross sectional area
        * Iz (``float``): Moment of inertia about local z axis
        * Iy (``float``): Moment of inertia about local y axis
        * J (``float``): Torsional inertia - about local x axis
        * Az (``float``): Cross sectional area in the local z direction
        * Ay (``float``): Cross sectional area in the local y direction

        """
        # Opensees py section type
        self.op_section_type = op_section_type  # section tag based on Openseespy - default is elastic
        self.section_command_flag = False  # flag for parsing , check if section() command is needed. default False
        # Openseespy section arguments

        self.A = kwargs.get("A", None)
        self.Iz = kwargs.get("Iz", None)
        self.Iy = kwargs.get("Iy", None)

        self.Ay = kwargs.get("Ay", None)
        self.Az = kwargs.get("Az", None)
        self.J = kwargs.get("J", None)
        self.alpha_y = kwargs.get("alpha_y", None)
        self.alpha_z = kwargs.get("alpha_z", None)
        self.K11 = kwargs.get("K11", None)
        self.K33 = kwargs.get("K33", None)
        self.K44 = kwargs.get("K44", None)
        # types for element definition and unit width properties
        self.op_ele_type = op_ele_type
        self.unit_width = unit_width
        self.mass = mass
        self.c_mass_flag = c_mass_flag
        # keyword args
        self.num_int_pt = kwargs.get("num_int_pt", None)
        self.integration_type = kwargs.get("integration_type", None)
        # quad/tri element parameters
        self.thick = kwargs.get("thick", None)


# ----------------------------------------------------------------------------------------------------------------
class GrillageMember:
    """
    Parent class for defining a Grillage member. Provides methods to wrap Openseespy Element() command.

    Some Opensees element() command takes in directly both material and section properties, while some requires
    first defining an Openseepy material, or Opensees section object. The role of this class is to parse the material
    and section information into its corresponding Openseespy Element() command.

    `Here <https://openseespydoc.readthedocs.io/en/latest/src/element.html>`_ is more information about Openseespy
    Element definition.

    For developers wishing to expand the library of elements, introduce in this class:

    #. The Openseespy section() command for the desire section - under the get_ops_section_command() method
    #. The Openseespy element() command for the element - under the get_element_command_str() method


    """

    def __init__(self, section: Section, material, member_name="Undefined", quad_ele_flag=False, tri_ele_flag=False):
        """
        Constructor takes two input object. A Material, and Section object.

        :param section: Section class object
        :type section: :class:`Section`
        :param material: Material class object
        :type material: :class:`Material`
        :param member_name: Name of the grillage member (Optional)
        :type member_name: str
        """
        self.member_name = member_name
        self.section = section
        self.material = material
        self.quad_flag = quad_ele_flag
        self.tri_ele_flag = tri_ele_flag

        if any([self.section.op_ele_type == "ElasticTimoshenkoBeam", self.section.op_ele_type == "elasticBeamColumn"]):
            self.material_command_flag = False
            self.section_command_flag = False  #

    def get_member_prop_arguments(self, width=1):
        # """
        # Function to output list of arguments for element type requiring an argument list (with preceding asterisk).
        # This is needed for element types ElasticTimoshenkoBeam, elasticBeamColumn - where no section is required as
        # inputs
        # :return: str containing member properties in accordance with convention of Opensees element type
        # """
        asterisk_input = None

        # if elastic Beam column elements, return str of section input
        if self.section.op_ele_type == "ElasticTimoshenkoBeam":
            if None in [self.material.E, self.material.G, self.section.A, self.section.J, self.section.Iy,
                        self.section.Iz, self.section.Ay, self.section.Az]:
                raise ValueError("One or more missing arguments for Section: {}".format(self.section.op_ele_type))
            asterisk_input = "[{:.3e}, {:.3e}, {:.3e}, {:.3e}, {:.3e}, {:.3e}, {:.3e}, {:.3e}]".format(self.material.E,
                                                                                                       self.material.G,
                                                                                                       self.section.A * width,
                                                                                                       self.section.J * width,
                                                                                                       self.section.Iy * width,
                                                                                                       self.section.Iz * width,
                                                                                                       self.section.Ay * width,
                                                                                                       self.section.Az * width)
        elif self.section.op_ele_type == "elasticBeamColumn":  # eleColumn
            if None in [self.material.E, self.material.G, self.section.A, self.section.J, self.section.Iy,
                        self.section.Iz]:
                raise ValueError("One or more missing arguments for Section: {}".format(self.section.op_ele_type))
            asterisk_input = "[{:.3e}, {:.3e}, {:.3e}, {:.3e}, {:.3e}, {:.3e}]".format(self.material.E, self.material.G,
                                                                                       self.section.A * width,
                                                                                       self.section.J * width,
                                                                                       self.section.Iy * width,
                                                                                       self.section.Iz * width)

        elif self.section.op_ele_type == "ModElasticBeam2d":
            if None in [self.section.A, self.material.E, self.section.Iz * width, self.section.K11, self.section.K33,
                        self.section.K44]:
                raise ValueError("One or more missing arguments for Section: {}".format(self.section.op_section_type))
            asterisk_input = "[{:.3e}, {:.3e}, {:.3e}, {:.3e}, {:.3e}, {:.3e}]".format(
                self.section.A * width, self.material.E, self.section.Iz * width, self.section.K11, self.section.K33,
                self.section.K44)

        # TO be populated with more inputs for various element types

        return asterisk_input

    # Function to return argument, handled by OspGrillage
    def get_section_arguments(self, ele_width=1):
        section_args = None

        if self.section.op_section_type == "Elastic":
            section_args = [self.material.E, self.section.A, self.section.Iz, self.section.Iy, self.material.G,
                            self.section.J, self.section.alpha_y, self.section.alpha_z]

        return section_args

    def get_ops_section_command(self, section_tag=1, material_tag=None, ele_width=1):
        # here sort based on section type , return sec_str which will be populated by OpsGrillage
        # in general first format entry {} is section type, second {} is section tag, each specific entries are
        # explained in comments below each condition
        sec_str = None
        section_type = self.section.op_section_type
        if section_type == "Elastic":
            # section type, section tag, argument entries from self.get_asterisk_input()
            sec_arg = self.get_section_arguments(ele_width=ele_width)
            sec_str = "ops.section(\"{type}\", {tag}, *{arg})\n".format(type=section_type, tag=section_tag, arg=repr(sec_arg))
        elif section_type == "ElasticMembranePlateSection":
            # section type, section tag, E_mod, nu, h, rho
            sec_str = "ops.section(\"{}\", {}, {}, {}, {}, {})\n"

        return sec_str

    def get_element_command_str(self, ele_tag, node_tag_list, transf_tag=None, ele_width=1, materialtag=None,
                                sectiontag=None) -> str:

        # Function called within OpsGrillage class `set_member()` function.
        #
        # For shell elements, n1 n2 n3 n4 are counter clockwise node (n1 being node in quadrant -1 , -1 ). This is checked
        # using sort_vertices function.
        #
        # Procedure to be called
        # 1) OpsGrillage assigns the material and section first, then returns the tag of material and section
        # 2) OpsGrillage calls get_element_command_str of GrillageMember, then it takes in material section and returns
        #  the element command ops.element() for the respective grillage member

        # format for ele
        # [node i, node j, ele group, ele tag, transtag]
        section_input = None
        ele_str = None
        if self.section.op_ele_type == "ElasticTimoshenkoBeam":
            section_input = self.get_member_prop_arguments(ele_width)
            ele_str = "ops.element(\"{type}\", {tag}, *{node_tag_list}, *{memberprop}, {transftag}, {mass})\n".format(
                type=self.section.op_ele_type, tag=ele_tag, node_tag_list=node_tag_list, memberprop=section_input,
                transftag=transf_tag,
                mass=self.section.mass)
        elif self.section.op_ele_type == "elasticBeamColumn":
            section_input = self.get_member_prop_arguments(ele_width)
            ele_str = "ops.element(\"{type}\", {tag}, *{node_tag_list}, *{memberprop}, {transftag}, {mass})\n".format(
                type=self.section.op_ele_type, tag=ele_tag, node_tag_list=node_tag_list, memberprop=section_input,
                transftag=transf_tag,
                mass=self.section.mass)
        elif self.section.op_ele_type == "nonlinearBeamColumn":
            ele_str = "ops.element(\"{type}\",{tag},*{node_tag_list},{num_int_pt},{sectag},{transftag},{mass})\n".format(
                type=self.section.op_ele_type, tag=ele_tag, node_tag_list=node_tag_list,
                num_int_pt=self.section.num_int_pt,
                sectag=sectiontag, transftag=transf_tag, mass=self.section.mass)

        elif self.section.op_ele_type == "ShellMITC4":
            ele_str = "ops.element(\"{type}\", {tag}, *{node_tag_list}, {sectag}})\n".format(
                type=self.section.op_ele_type, tag=ele_tag, node_tag_list=node_tag_list, sectag=sectiontag)

        # HERE TO POPULATE WITH MORE ELEMENT TYPES

        return ele_str
