
# ----------------------------------------------------------------------------------------------------------------
class Section:
    """
    Section class to define various grillage sections. Class
    """

    def __init__(self, E, A, Iz, J, Ay, Az, Iy=None, G=None, alpha_y=None, op_ele_type=None, mass=0, c_mass_flag=False,
                 unit_width=False, op_section_type=None, K11=None, K33=None, K44=None):
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
        self.K11 = K11
        self.K33 = K33
        self.K44 = K44
        # types for element definition and unit width properties
        self.op_ele_type = op_ele_type
        self.unit_width = unit_width
        self.mass = mass
        self.c_mass_flag = c_mass_flag
        # check if section command is needed for the section object
        if self.op_section_type is not None:
            self.section_command_flag = True  # section_command_flag set to True.

    def get_asterisk_arguments(self, width=1):
        """
        Function to output list of arguments for element() command following Openseespy convention. Function also
        output
        :return: list containing member properties in accordance with  input convention
        """
        asterisk_input = None

        # if elastic Beam column elements, return str of section input
        if self.op_ele_type == "ElasticTimoshenkoBeam":
            # section_input = [self.E, self.G, self.A, self.J, self.Iy, self.Iz, self.Ay, self.Az]
            asterisk_input = "[{:.3e}, {:.3e}, {:.3e}, {:.3e}, {:.3e}, {:.3e}, {:.3e}, {:.3e}]".format(self.E,
                                                                                                       self.G,
                                                                                                       self.A,
                                                                                                       self.J,
                                                                                                       self.Iy * width,
                                                                                                       self.Iz * width,
                                                                                                       self.Ay * width,
                                                                                                       self.Az * width)
        elif self.op_ele_type == "elasticBeamColumn":  # eleColumn
            # section_input = [self.E, self.G, self.A, self.J, self.Iy, self.Iz]
            asterisk_input = "[{:.3e}, {:.3e}, {:.3e}, {:.3e}, {:.3e}, {:.3e}]".format(self.E, self.G, self.A * width,
                                                                                       self.J, self.Iy * width,
                                                                                       self.Iz * width)

        elif self.op_ele_type == "ModElasticBeam2d":
            asterisk_input = "[{:.3e}, {:.3e}, {:.3e}, {:.3e}, {:.3e}, {:.3e}]".format(
                self.A * width, self.E, self.Iz * width, self.K11, self.K33, self.K44)
        # else, section tag required in element() input, OpsGrillage automatically assigns the section tag within
        # set_member() function
        return asterisk_input

    def get_element_command_str(self, ele, ele_width=1, sectiontag=None):
        """
        Function called within OpsGrillage class `set_member()` function.
        """
        # format for ele
        # [node i, node j, ele group, ele tag, transtag]

        # TODO add strs for more Opensees element types here
        if self.op_ele_type == "ElasticTimoshenkoBeam":
            section_input = self.get_asterisk_arguments(ele_width)
            ele_str = "ops.element(\"{type}\", {tag}, *[{i}, {j}], *{memberprop}, {transftag}, {mass})\n".format(
                type=self.op_ele_type, tag=ele[0], i=ele[1], j=ele[2], memberprop=section_input, transftag=ele[4],
                mass=self.mass)
        if self.op_ele_type == "elasticBeamColumn":
            section_input = self.get_asterisk_arguments(ele_width)
            ele_str = "ops.element(\"{type}\", {tag}, *[{i}, {j}], *{memberprop}, {transftag}, {mass})\n".format(
                type=self.op_ele_type, tag=ele[0], i=ele[1], j=ele[2], memberprop=section_input, transftag=ele[4],
                mass=self.mass)
        if self.op_ele_type == "nonlinearBeamColumn":
            pass

        # return string to OpsGrillage for writing command
        return ele_str


# ----------------------------------------------------------------------------------------------------------------
class GrillageMember:
    """
    Grillage member class.
    """

    def __init__(self, section, material, member_name="Undefined"):
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
