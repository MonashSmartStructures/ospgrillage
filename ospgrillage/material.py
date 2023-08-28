# -*- coding: utf-8 -*-
"""
This module contains the user interface function and class to manage
 material properties that allow definition offine grillage elements.
 The module also contains methods that wraps ```OpenSeesPy``` material object creation.
"""

import json


def create_material(**kwargs):
    """
    User interface function to create :class:`Material` object

    The constructor of :class:`Material` object takes in three types of keyword arguments:

    #. Keyword for looking up the *ospgrillage* material library i.e. mat_lib.json.
    #. General material properties - such as E, and G
    #. Specific arguments of ``OpenSeesPy`` material library.


    :parameter:

    * code (`str`): name string of code according to mat_lib.json
    * type (`str`): Either "concrete" or "steel"
    * grade(`str`): Grade of material according to code

    The following keywords are examples of general material properties:

    :keyword:

    * E (`float`): Elastic modulus
    * G (`float`): Shear modulus

    """
    return Material(**kwargs)


class Material:
    """
    This class stores information and provides methods to parse input material properties into ``OpenSeesPy`` Material
    objects.

    `Here <https://openseespydoc.readthedocs.io/en/latest/src/uniaxialMaterial.html>`_ are the information about OpenSees
    Material objects.

    As *ospgrillage* is mainly intended for bridge decks , concrete and steel makes up the primary
    materials. In turn, *ospgrillage* wraps the UniAxialMaterial object of ``OpenSeesPy`` since it contains the primary
    options for Concrete and Steel.

    The Material class also allow users to utilize codified material properties (e.g. AS5100, ASHTOO).
    These material properties are stored in a material library file (mat_lib.json). Users are required to pass in
    the appropriate keyword arguments (dict keys) to select the desirable codified materials. Users may access
    mat_lib.json. Additionally, this class is able create the mat_lib.json file and pass it through

    .. note::

        Current version of mat_lib.json is 0.1.0
    """

    def __init__(self, **kwargs):
        """
        The constructor of Material takes in three types of inputs:

        #. Keywords for looking up the *ospgrillage* material library i.e. mat_lib.json.
        #. General material properties - such as E, and G
        #. Specific material arguments of ``OpenSeesPy``.

        For (1), the following keywords are **required**:

        :keyword:

        * code (`str`): name string of code according to mat_lib.json
        * type (`str`): Either "concrete" or "steel"
        * grade(`str`): Grade of material according to code

        For (2), the minimum required material properties are:

        :keyword:

        * E (`float`): Elastic modulus
        * G (`float`): Shear modulus
        * v (`float`): Poisson's ratio
        * rho (`float`): Density

        For (3), refer to `OpenSeesPy <https://openseespydoc.readthedocs.io/en/latest/src/uniaxialMaterial.html>`_.


        """
        # Instantiate variables
        self.ops_mat_type = kwargs.get(
            "ops_mat_type", None
        )  # this is the os convention for materials e.g. Concrete01
        self.op_mat_arg = None  # arguments according to OpenSeesPy
        self.units = kwargs.get("units", None)  # default SI units
        # assigns variables for all kwargs for codified material types
        self.code = kwargs.get("code", None)
        self.material_type = kwargs.get("material", None)
        self.material_grade = kwargs.get("grade", None)
        # assign generic material properties
        self.elastic_modulus = kwargs.get("E", None)
        self.shear_modulus = kwargs.get("G", None)
        self.poisson_ratio = kwargs.get("v", None)
        self.density = kwargs.get("rho", None)

        # get mat lib file
        self.default_mat = kwargs.get("default_material", True)
        self._mat_lib = self._read_mat_lib()
        # ----------------------------------------------------------------------------------
        # material vars

        # properties for Standard Elastic OpenSeesPy material

        # properties for Concrete - symbols according to OpenSees uniaxialMaterial/Concrete
        self.fpc = kwargs.get("fpc", None)
        self.epsc0 = kwargs.get("epsc0", None)
        self.fpcu = kwargs.get("fpcu", None)
        self.epsU = kwargs.get("epsU", None)

        # properties for Steel - symbols according to OpenSees uniaxialMaterial/Steel
        self.Fy = kwargs.get("Fy", None)
        self.E0 = kwargs.get("E0", None)
        self.b = kwargs.get("b", None)  # strain -hardening ratio.
        self.a1 = kwargs.get("a1", None)
        self.a2 = kwargs.get(
            "a2", None
        )  # isotropic hardening parameter , see Ops Steel01
        self.a3 = kwargs.get("a3", None)
        self.a4 = kwargs.get("a4", None)

        # ----------------------------------------------------------------------------------
        # process all inputs into relevant inputs for OpenSees material command
        self._parse_material_command()

    def _parse_material_command(self):
        """
        Checks and parse the material properties based on the input types - either codified, general, or OpenSeesPy
        specific material inputs.
        """
        # check if code material is selected, if yes read from material library json
        if self.code:
            self.poisson_ratio = self._mat_lib[self.material_type][self.code][
                self.material_grade
            ]["v"]
            self.elastic_modulus = self._mat_lib[self.material_type][self.code][
                self.material_grade
            ]["E"]
            self.fpc = self._mat_lib[self.material_type][self.code][
                self.material_grade
            ]["fc"]
            self.density = self._mat_lib[self.material_type][self.code][
                self.material_grade
            ]["rho"]
            self.units = self._mat_lib[self.material_type][self.code]["units"]
        else:  # a custom material
            pass

        # perform conversion for units
        if self.units == "SI":
            self.elastic_modulus = self.elastic_modulus * 1e9
            self.fpc = self.fpc * 1e6

        # check poison ratio
        if not self.poisson_ratio:
            self.poisson_ratio = 0.3

        # if G not defined, calculate using formula E/(2(1+v))
        if self.shear_modulus is None:
            self.shear_modulus = self.elastic_modulus / (2 * (1 + self.poisson_ratio))

        if self.material_type == "concrete":
            self.ops_mat_type = (
                "Concrete01"  # default opensees material type to represent concrete
            )
        elif self.material_type == "steel":
            self.ops_mat_type = (
                "Steel01"  # default opensees material type to represent steel
            )

    def get_material_args(self):
        """
        Function to get OpenSeesPy material type and arguments. This function is handled by
        :class:`ospgrillage.osp_grillage.OspGrillage`.

        :returns: Str of OpenSeesPy material type and list of material properties correspond to the inputs of
         OpenSeesPy commands
        """
        if self.ops_mat_type == "Concrete01":
            self.op_mat_arg = [self.fpc, self.epsc0, self.fpcu, self.epsU]
        elif self.ops_mat_type == "Steel01":
            self.op_mat_arg = [
                self.Fy,
                self.E0,
                self.b,
                self.a1,
                self.a2,
                self.a3,
                self.a4,
            ]
        elif self.ops_mat_type == "Elastic":
            self.op_mat_arg = [self.elastic_modulus]
        # TO ADD for MORE materials

        # check if None in entries
        if None in self.op_mat_arg:
            raise Exception(
                "One or more missing/non-numeric parameters for Material: {} ".format(
                    self.ops_mat_type
                )
            )
        return self.ops_mat_type, self.op_mat_arg

    @staticmethod
    def _create_default_dict():
        """
        Function to create the default mat_lib.js file. The default version is 0.0.1.
        Just to make sure the JSON file is formatted correctly
        Note: 1 ksi = 6.89475728 MPa
        """

        mat_lib = {
            "concrete": {
                "AS5100-2017": {
                    "units": "SI",
                    "25MPa": {"fc": 25, "E": 26.7, "v": 0.2, "rho": 2.4e3},
                    "32MPa": {"fc": 32, "E": 30.1, "v": 0.2, "rho": 2.4e3},
                    "40MPa": {"fc": 40, "E": 32.8, "v": 0.2, "rho": 2.4e3},
                    "50MPa": {"fc": 50, "E": 34.8, "v": 0.2, "rho": 2.4e3},
                    "65MPa": {"fc": 65, "E": 37.4, "v": 0.2, "rho": 2.4e3},
                    "80MPa": {"fc": 80, "E": 39.6, "v": 0.2, "rho": 2.4e3},
                    "100MPa": {"fc": 100, "E": 42.2, "v": 0.2, "rho": 2.4e3},
                },
                "AASHTO-LRFD-8th": {
                    "units": "SI",
                    "2.4ksi": {"fc": 16.55, "E": 23.2223, "v": 0.2, "rho": 2.4027e3},
                    "3.0ksi": {"fc": 20.68, "E": 24.997, "v": 0.2, "rho": 2.4027e3},
                    "3.6ksi": {"fc": 24.82, "E": 26.547, "v": 0.2, "rho": 2.4027e3},
                    "4.0ksi": {"fc": 27.58, "E": 27.486, "v": 0.2, "rho": 2.4027e3},
                    "5.0ksi": {"fc": 34.47, "E": 29.587, "v": 0.2, "rho": 2.4027e3},
                    "6.0ksi": {"fc": 41.37, "E": 31.856, "v": 0.2, "rho": 2.4027e3},
                    "7.5ksi": {"fc": 51.71, "E": 34.999, "v": 0.2, "rho": 2.4027e3},
                    "10.0ksi": {"fc": 68.95, "E": 39.8, "v": 0.2, "rho": 2.4027e3},
                    "15.0ksi": {"fc": 103.42, "E": 48.582, "v": 0.2, "rho": 2.4027e3},
                },
            },
            "steel": {
                "AS5100.6-2004": {
                    "units": "SI",
                    "R250N": {"fy": 250, "E": 200.0, "v": 0.25, "rho": 7850},
                    "D500N": {"fy": 500, "E": 200.0, "v": 0.25, "rho": 7850},
                    "D500L": {"fy": 500, "E": 200.0, "v": 0.25, "rho": 7850},
                },
                "AASHTO-LRFD-8th": {
                    "units": "SI",
                    "A615-40": {"fy": 275.8, "E": 200.0, "v": 0.3, "rho": 7849},
                    "A615-60": {"fy": 413.67, "E": 200.0, "v": 0.3, "rho": 7849},
                    "A615-75": {"fy": 517.12, "E": 200.0, "v": 0.3, "rho": 7849},
                    "A615-80": {"fy": 551.58, "E": 200.0, "v": 0.3, "rho": 7849},
                    "A615-100": {"fy": 689.48, "E": 200.0, "v": 0.3, "rho": 7849},
                },
            },
        }

        return mat_lib

    @staticmethod
    def _write_mat_lib(mat_lib):
        """
        Write out the passed material dict
        Not to be used in the ordinary course of events at risk of overwriting
        manual edits to the mat_lib
        Used for initial creation of the mat_lib
        """

        with open("mat_lib.json", "w") as f:
            json.dump(mat_lib, f, indent=4)

    def _read_mat_lib(self):
        """
        Read material library from json file
        """
        mat_lib = {}
        try:
            with open("mat_lib.json", "r") as f:
                mat_lib = json.load(f)
        except (FileNotFoundError, IOError):
            print("Material library unable to be read\nUsing default library")
            mat_lib = self._create_default_dict()
            self._write_mat_lib(mat_lib)
        return mat_lib

    def get_ops_material_command(self, material_tag):
        """
        Parse material properties into OpenSeesPy Material commands.

        :param material_tag: tag of material defined in in OpenSeesPy space
        :type material_tag: int

        :return: Str of OpenSees command to create material in OpenSeesPy

        """
        # e.g. concrete01 or steel01
        mat_str = None
        if (
            self.ops_mat_type == "Concrete01"
            or self.ops_mat_type == "Steel01"
            or self.ops_mat_type == "Elastic"
        ):
            mat_str = 'ops.uniaxialMaterial("{type}", {tag}, *{vec})\n'.format(
                type=self.ops_mat_type, tag=material_tag, vec=self.op_mat_arg
            )

        return mat_str
