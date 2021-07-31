# -*- coding: utf-8 -*-
"""
This module manages user interface functions and class defintions for the
grillage members. In our terminology, we define a section as the geomterical 
properties of the structural elements, and the member as the combination of 
the section and material properties.
"""


def create_section(**kwargs):
    """
    User interface for section creation
    """
    return Section(**kwargs)


def create_member(**kwargs):
    """
    User interface for member creation
    """
    return GrillageMember(**kwargs)


class Section:
    """
    Section class to define various grillage sections. Class
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
        :param E: Elastic modulus
        :type E: float
        :param A: Cross sectional area
        :type A: float
        :param Iz: Moment of inertia about z axis
        :type Iz: float
        :param J: Torsional inertia
        :type J: float
        :param Ay: Cross sectional area in the y direction
        :type Ay: float
        :param Az: Cross sectional area in the z direction
        :type Az: float
        :param Iy: Moment of inertia about z axis
        :type Iy: float
        :param G: Shear modulus
        :type G: float
        :param alpha_y: shear shape factor along the local y-axis (optional)
        :type alpha_y: float
        :param op_ele_type: Opensees element type
        :type op_ele_type: str
        :param op_section_type: Opensees section type
        :type op_section_type: str
        :param unit_width: Flag for unit width properties
        :type unit_width: bool

        Example
        section('Elastic', BeamSecTag,Ec,ABeam,IzBeam)

        :keyword:

        """
        # sections
        self.op_section_type = op_section_type  # section tag based on Openseespy
        self.section_command_flag = False  # default False
        # section geometry properties variables
        self.E = kwargs.get("E", None)
        self.A = kwargs.get("A", None)
        self.Iz = kwargs.get("Iz", None)
        self.Iy = kwargs.get("Iy", None)
        self.G = kwargs.get("G", None)
        self.Ay = kwargs.get("Ay", None)
        self.Az = kwargs.get("Az", None)
        self.J = kwargs.get("J", None)
        self.alpha_y = kwargs.get("alpha_y", None)
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

        # check if section command is needed for the section object
        if self.op_section_type is not None:
            self.section_command_flag = True  # section_command_flag set to True.

    def get_asterisk_arguments(self, width=1):
        # """
        # Function to output list of arguments for element type requiring an argument list (with preceding asterisk).
        # This is needed for element types ElasticTimoshenkoBeam, elasticBeamColumn - where no section is required as
        # inputs
        # :return: str containing member properties in accordance with convention of Opensees element type
        # """
        asterisk_input = None

        # if elastic Beam column elements, return str of section input
        if self.op_ele_type == "ElasticTimoshenkoBeam":
            if None in [
                self.E,
                self.G,
                self.A,
                self.J,
                self.Iy,
                self.Iz,
                self.Ay,
                self.Az,
            ]:
                raise ValueError(
                    "One or more missing arguments for Section: {}".format(
                        self.op_section_type
                    )
                )
            asterisk_input = "[{:.3e}, {:.3e}, {:.3e}, {:.3e}, {:.3e}, {:.3e}, {:.3e}, {:.3e}]".format(
                self.E,
                self.G,
                self.A,
                self.J,
                self.Iy * width,
                self.Iz * width,
                self.Ay * width,
                self.Az * width,
            )
        elif self.op_ele_type == "elasticBeamColumn":  # eleColumn
            if None in [self.E, self.G, self.A, self.J, self.Iy, self.Iz]:
                raise ValueError(
                    "One or more missing arguments for Section: {}".format(
                        self.op_section_type
                    )
                )
            asterisk_input = "[{:.3e}, {:.3e}, {:.3e}, {:.3e}, {:.3e}, {:.3e}]".format(
                self.E, self.G, self.A * width, self.J, self.Iy * width, self.Iz * width
            )

        elif self.op_ele_type == "ModElasticBeam2d":
            if None in [
                self.A * width,
                self.E,
                self.Iz * width,
                self.K11,
                self.K33,
                self.K44,
            ]:
                raise ValueError(
                    "One or more missing arguments for Section: {}".format(
                        self.op_section_type
                    )
                )
            asterisk_input = "[{:.3e}, {:.3e}, {:.3e}, {:.3e}, {:.3e}, {:.3e}]".format(
                self.A * width, self.E, self.Iz * width, self.K11, self.K33, self.K44
            )
        # else, section tag required in element() input, OpsGrillage automatically assigns the section tag within
        # set_member() function
        return asterisk_input

    def get_section_arg_str(self, ele_width=1):
        # Function to return arguments for ops.section() command. Arguments are based on the type of section. E.g. Elastic
        # takes no material tag, whilst Plate Fibre Section requires a material object tag to be defined.
        #
        # :return section_type: str of section type
        # :return section_arg: str of section inputs

        # extract section variables from Section class
        section_type = self.op_section_type  # opensees section type
        # section argument
        section_arg = self.get_asterisk_arguments(
            width=ele_width
        )  # list of argument for section - Openseespy convention
        return section_type, section_arg

    def get_section_command(self, section_tag=1, ele_width=1):
        # here sort based on section type , return sec_str which will be populated by OpsGrillage
        # in general first format entry {} is section type, second {} is section tag, each specific entries are
        # explained in comments below each condition
        sec_str = None
        section_type = self.op_section_type
        if section_type == "Elastic":
            # section type, section tag, argument entries from self.get_asterisk_input()
            _, sec_arg = self.get_section_arg_str(ele_width=ele_width)
            sec_str = 'ops.section("{}", {}, *{})\n'.format(
                section_type, section_tag, sec_arg
            )
        elif section_type == "ElasticMembranePlateSection":
            # section type, section tag, E_mod, nu, h, rho
            sec_str = 'ops.section("{}", {}, {}, {}, {}, {})\n'

        return sec_str


# ----------------------------------------------------------------------------------------------------------------
class GrillageMember:
    """
    Main class for Grillage member definition. Class requires two objects as input parameters: a Section object and a
    Material object.
    """

    def __init__(
        self,
        section: Section,
        material,
        member_name="Undefined",
        quad_ele_flag=True,
        tri_ele_flag=False,
    ):
        """
        :param section: Section class object assigned to GrillageMember
        :type section: :class:`Section`
        :param material: Material class object assigned to GrillageMember
        :type material: :class:`uniaxialMaterial`
        :param name: Name of the grillage member (Optional)
        """
        self.member_name = member_name
        self.section = section
        self.material = material
        self.quad_flag = quad_ele_flag
        self.tri_ele_flag = tri_ele_flag

    def get_element_command_str(
        self,
        ele_tag,
        node_tag_list,
        transf_tag=None,
        ele_width=1,
        materialtag=None,
        sectiontag=None,
    ) -> str:

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
            _, section_input = self.section.get_section_arg_str(ele_width)
            ele_str = 'ops.element("{type}", {tag}, *{node_tag_list}, *{memberprop}, {transftag}, {mass})\n'.format(
                type=self.section.op_ele_type,
                tag=ele_tag,
                node_tag_list=node_tag_list,
                memberprop=section_input,
                transftag=transf_tag,
                mass=self.section.mass,
            )
        if self.section.op_ele_type == "elasticBeamColumn":
            _, section_input = self.section.get_section_arg_str(ele_width)
            ele_str = 'ops.element("{type}", {tag}, *{node_tag_list}, *{memberprop}, {transftag}, {mass})\n'.format(
                type=self.section.op_ele_type,
                tag=ele_tag,
                node_tag_list=node_tag_list,
                memberprop=section_input,
                transftag=transf_tag,
                mass=self.section.mass,
            )
        if self.section.op_ele_type == "nonlinearBeamColumn":
            ele_str = 'ops.element("{type}",{tag},*{node_tag_list},{num_int_pt},{sectag},{transftag},{mass})\n'.format(
                type=self.section.op_ele_type,
                tag=ele_tag,
                node_tag_list=node_tag_list,
                num_int_pt=self.section.num_int_pt,
                sectag=sectiontag,
                transftag=transf_tag,
                mass=self.section.mass,
            )

        if self.section.op_ele_type == "ShellMITC4":
            ele_str = 'ops.element("{type}", {tag}, *{node_tag_list}, {sectag}})\n'.format(
                type=self.section.op_ele_type,
                tag=ele_tag,
                node_tag_list=node_tag_list,
                sectag=sectiontag,
            )

        # return string to OpsGrillage for writing command
        return ele_str
